.bail on
.echo off

-- Run from the repository root:
-- sqlite3 :memory: < sql/analysis.sql

DROP TABLE IF EXISTS raw_tracks;
DROP TABLE IF EXISTS cleaned_tracks;

CREATE TABLE raw_tracks (
    source_row INTEGER,
    track_id TEXT,
    artists TEXT,
    album_name TEXT,
    track_name TEXT,
    popularity INTEGER,
    duration_ms INTEGER,
    explicit TEXT,
    danceability REAL,
    energy REAL,
    musical_key INTEGER,
    loudness REAL,
    mode INTEGER,
    speechiness REAL,
    acousticness REAL,
    instrumentalness REAL,
    liveness REAL,
    valence REAL,
    tempo REAL,
    time_signature INTEGER,
    track_genre TEXT
);

.mode csv
.import --skip 1 data/dataset.csv raw_tracks

CREATE TABLE cleaned_tracks AS
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY track_id
            ORDER BY source_row
        ) AS duplicate_rank
    FROM raw_tracks
), normalized AS (
    SELECT
        *,
        ' ' || LOWER(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                COALESCE(track_name, ''),
                '.', ' '), '-', ' '), '(', ' '), ')', ' '),
                '[', ' '), ']', ' '), '/', ' '), ',', ' '), '★', ' ')
        ) || ' ' AS normalized_title
    FROM ranked
    WHERE duplicate_rank = 1
      AND duration_ms > 0
)
SELECT
    track_id,
    artists,
    album_name,
    track_name,
    popularity,
    duration_ms,
    duration_ms / 1000.0 AS duration_sec,
    CASE WHEN LOWER(explicit) = 'true' THEN 1 ELSE 0 END AS explicit,
    danceability,
    energy,
    loudness,
    valence,
    track_genre,
    CASE
        WHEN INSTR(COALESCE(artists, ''), ';') > 0 THEN 1
        WHEN INSTR(normalized_title, ' feat ') > 0 THEN 1
        WHEN INSTR(normalized_title, ' ft ') > 0 THEN 1
        WHEN INSTR(normalized_title, ' featuring ') > 0 THEN 1
        WHEN INSTR(normalized_title, ' with ') > 0 THEN 1
        ELSE 0
    END AS has_feature
FROM normalized;

.headers on
.mode box

.print ''
.print 'QUERY 1: Data cleaning audit'
SELECT
    (SELECT COUNT(*) FROM raw_tracks) AS raw_rows,
    (SELECT COUNT(*) FROM cleaned_tracks) AS cleaned_rows,
    (SELECT COUNT(*) FROM raw_tracks) -
        (SELECT COUNT(*) FROM cleaned_tracks) AS rows_removed,
    (SELECT COUNT(DISTINCT track_id) FROM cleaned_tracks) AS unique_track_ids,
    (SELECT COUNT(*) FROM cleaned_tracks WHERE duration_ms <= 0) AS invalid_durations;

.print ''
.print 'QUERY 2: Popularity by collaboration status'
SELECT
    CASE has_feature WHEN 1 THEN 'Featured artist' ELSE 'Solo' END AS track_type,
    COUNT(*) AS tracks,
    ROUND(AVG(popularity), 2) AS mean_popularity,
    ROUND(AVG(duration_sec), 1) AS mean_duration_sec,
    ROUND(100.0 * AVG(explicit), 1) AS explicit_percent
FROM cleaned_tracks
GROUP BY has_feature
ORDER BY has_feature;

.print ''
.print 'QUERY 3: Raw difference in mean popularity'
WITH group_means AS (
    SELECT has_feature, AVG(popularity) AS mean_popularity
    FROM cleaned_tracks
    GROUP BY has_feature
)
SELECT ROUND(
    MAX(CASE WHEN has_feature = 1 THEN mean_popularity END) -
    MAX(CASE WHEN has_feature = 0 THEN mean_popularity END),
    3
) AS featured_minus_solo_points
FROM group_means;

.print ''
.print 'QUERY 4: Genres with the highest collaboration share'
SELECT
    track_genre,
    COUNT(*) AS tracks,
    SUM(has_feature) AS featured_tracks,
    ROUND(100.0 * AVG(has_feature), 1) AS featured_share_percent,
    ROUND(AVG(popularity), 1) AS mean_popularity
FROM cleaned_tracks
GROUP BY track_genre
HAVING COUNT(*) >= 500
ORDER BY featured_share_percent DESC, tracks DESC
LIMIT 8;

.print ''
.print 'QUERY 5: Popularity gap within each genre'
SELECT
    track_genre,
    SUM(CASE WHEN has_feature = 0 THEN 1 ELSE 0 END) AS solo_tracks,
    SUM(CASE WHEN has_feature = 1 THEN 1 ELSE 0 END) AS featured_tracks,
    ROUND(AVG(CASE WHEN has_feature = 0 THEN popularity END), 2) AS solo_mean,
    ROUND(AVG(CASE WHEN has_feature = 1 THEN popularity END), 2) AS featured_mean,
    ROUND(
        AVG(CASE WHEN has_feature = 1 THEN popularity END) -
        AVG(CASE WHEN has_feature = 0 THEN popularity END),
        2
    ) AS within_genre_gap
FROM cleaned_tracks
GROUP BY track_genre
HAVING solo_tracks >= 100 AND featured_tracks >= 100
ORDER BY ABS(within_genre_gap) DESC
LIMIT 8;

.print ''
.print 'QUERY 6: Exact genre composition decomposition'
WITH genre_stats AS (
    SELECT
        track_genre,
        SUM(CASE WHEN has_feature = 0 THEN 1.0 ELSE 0 END) AS n0,
        SUM(CASE WHEN has_feature = 1 THEN 1.0 ELSE 0 END) AS n1,
        AVG(CASE WHEN has_feature = 0 THEN popularity END) AS m0,
        AVG(CASE WHEN has_feature = 1 THEN popularity END) AS m1
    FROM cleaned_tracks
    GROUP BY track_genre
), totals AS (
    SELECT SUM(n0) AS total0, SUM(n1) AS total1
    FROM genre_stats
), components AS (
    SELECT
        SUM(((g.n1 / t.total1) - (g.n0 / t.total0)) * g.m0) AS composition,
        SUM((g.n1 / t.total1) * (g.m1 - g.m0)) AS within_genre
    FROM genre_stats AS g
    CROSS JOIN totals AS t
)
SELECT
    ROUND(composition, 3) AS composition_points,
    ROUND(within_genre, 3) AS within_genre_points,
    ROUND(composition + within_genre, 3) AS reconstructed_raw_gap,
    ROUND(100.0 * composition / (composition + within_genre), 1) AS composition_percent
FROM components;

.print ''
.print 'QUERY 7: Sensitivity after excluding zero-popularity tracks'
WITH group_means AS (
    SELECT has_feature, COUNT(*) AS tracks, AVG(popularity) AS mean_popularity
    FROM cleaned_tracks
    WHERE popularity > 0
    GROUP BY has_feature
)
SELECT
    SUM(tracks) AS tracks_retained,
    ROUND(MAX(CASE WHEN has_feature = 0 THEN mean_popularity END), 2) AS solo_mean,
    ROUND(MAX(CASE WHEN has_feature = 1 THEN mean_popularity END), 2) AS featured_mean,
    ROUND(
        MAX(CASE WHEN has_feature = 1 THEN mean_popularity END) -
        MAX(CASE WHEN has_feature = 0 THEN mean_popularity END),
        3
    ) AS featured_minus_solo_points
FROM group_means;
