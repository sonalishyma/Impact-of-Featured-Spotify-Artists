document.getElementById('navToggle').addEventListener('click', function () {
  document.getElementById('navLinks').classList.toggle('open');
});

document.querySelectorAll('.nav-links a').forEach(function (link) {
  link.addEventListener('click', function () {
    document.getElementById('navLinks').classList.remove('open');
  });
});

// The editorial direction for this site intentionally avoids all visible dash marks.
// Keep code, links, and data keys untouched while cleaning rendered copy and chart labels.
function removeVisibleHyphens(root) {
  var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  var nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(function (node) {
    if (!node.parentElement || node.parentElement.closest('script, style')) return;
    node.nodeValue = node.nodeValue.replace(/[\u002D\u058A\u05BE\u1400\u1806\u2010-\u2015\u2E17\u2E1A\u2E3A-\u2E3B\u2E40\u301C\u3030\u30A0\uFE31-\uFE32\uFE58\uFE63\uFF0D\u2212]/g, ' ');
  });
}

removeVisibleHyphens(document.body);

var hyphenObserver = new MutationObserver(function (mutations) {
  mutations.forEach(function (mutation) {
    mutation.addedNodes.forEach(function (node) {
      if (node.nodeType === Node.TEXT_NODE) {
        node.nodeValue = node.nodeValue.replace(/[\u002D\u2010-\u2015\u2212]/g, ' ');
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        removeVisibleHyphens(node);
      }
    });
  });
});
hyphenObserver.observe(document.body, { childList: true, subtree: true });

var observedSections = document.querySelectorAll('header[id], section[id]');
var sectionObserver = new IntersectionObserver(function (entries) {
  entries.forEach(function (entry) {
    if (!entry.isIntersecting) return;
    document.querySelectorAll('.nav-links a').forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id);
    });
  });
}, { rootMargin: '-20% 0px -70% 0px' });
observedSections.forEach(function (section) { sectionObserver.observe(section); });
