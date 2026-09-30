// Apply the saved/system theme before first paint to avoid a flash.
(function () {
  var t = null;
  try { t = localStorage.getItem("cg_theme"); } catch (e) {}
  var dark = t === "dark" || ((!t || t === "system") && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.classList.toggle("dark", dark);
})();
