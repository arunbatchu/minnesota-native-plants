// MathJax configuration for MkDocs Material + pymdownx.arithmatex (generic mode).
//
// mkdocs.yml has listed this file under extra_javascript for a long time, but
// it did not exist — every page load 404'd on it. This is that file.
//
// Arithmatex in generic mode wraps math in \(...\) and \[...\] before MathJax
// sees it, so only those delimiters are configured here. Bare $...$ is
// deliberately NOT an inline delimiter: this book quotes install costs like
// "$800 – $1,800", and enabling $ would let MathJax typeset a price range as
// an equation.
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

// Re-typeset after Material's instant-loading navigation swaps the page body,
// otherwise math renders on first load and never again.
if (typeof document$ !== "undefined") {
  document$.subscribe(() => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.startup.output.clearCache();
      window.MathJax.typesetClear();
      window.MathJax.texReset();
      window.MathJax.typesetPromise();
    }
  });
}
