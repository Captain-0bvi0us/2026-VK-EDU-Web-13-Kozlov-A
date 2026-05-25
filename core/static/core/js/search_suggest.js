/* поисковые подсказки.
 *
 * - запрос отправляется на /api/search/suggest/?q=...;
 * - debounce 250 мс, чтобы не дёргать сервер на каждый символ;
 * - выпадающий список под полем; клик / Enter переходит к вопросу.
 */

(function () {
  "use strict";

  function debounce(fn, ms) {
    var timer = null;
    return function () {
      var args = arguments;
      var ctx = this;
      if (timer) clearTimeout(timer);
      timer = setTimeout(function () {
        fn.apply(ctx, args);
      }, ms);
    };
  }

  function renderItems(box, items) {
    if (!items.length) {
      box.innerHTML =
        '<li class="search-suggest-empty text-secondary px-3 py-2">Ничего не найдено</li>';
      box.classList.remove("d-none");
      return;
    }
    var html = items
      .map(function (it) {
        return (
          '<li><a href="' +
          encodeURI(it.url) +
          '" class="d-block px-3 py-2 text-decoration-none">' +
          it.title_highlighted +
          "</a></li>"
        );
      })
      .join("");
    box.innerHTML = html;
    box.classList.remove("d-none");
  }

  function init() {
    var input = document.getElementById("q-search");
    var box = document.getElementById("q-search-suggest");
    var form = input && input.closest("form.search-wrap");
    var url = form && form.dataset.suggestUrl;
    if (!input || !box || !url) return;

    var lastQuery = "";
    var ctrl = null;

    var runSearch = debounce(function () {
      var q = input.value.trim();
      if (q.length < 2) {
        box.classList.add("d-none");
        box.innerHTML = "";
        lastQuery = "";
        return;
      }
      if (q === lastQuery) return;
      lastQuery = q;
      if (ctrl) ctrl.abort();
      ctrl = typeof AbortController !== "undefined" ? new AbortController() : null;
      var fetchOpts = { credentials: "same-origin" };
      if (ctrl) fetchOpts.signal = ctrl.signal;
      fetch(url + "?q=" + encodeURIComponent(q), fetchOpts)
        .then(function (r) {
          if (!r.ok) throw new Error("status " + r.status);
          return r.json();
        })
        .then(function (data) {
          renderItems(box, data.results || []);
        })
        .catch(function () {
          /* ignore */
        });
    }, 250);

    input.addEventListener("input", runSearch);

    input.addEventListener("blur", function () {
      setTimeout(function () {
        box.classList.add("d-none");
      }, 150);
    });
    input.addEventListener("focus", function () {
      if (box.innerHTML) box.classList.remove("d-none");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
