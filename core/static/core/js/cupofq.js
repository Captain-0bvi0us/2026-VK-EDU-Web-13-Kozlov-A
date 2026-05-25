(function ($) {
  "use strict";

  function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== "") {
      const parts = document.cookie.split(";");
      for (let i = 0; i < parts.length; i += 1) {
        const cookie = parts[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          value = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return value;
  }

  const csrftoken = getCookie("csrftoken");

  function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain && csrftoken) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    },
  });

  function loginUrlWithNext() {
    const base = $("body").data("loginUrl") || "/login/";
    const next = window.location.pathname + window.location.search;
    const sep = base.indexOf("?") >= 0 ? "&" : "?";
    return base + sep + "next=" + encodeURIComponent(next);
  }

  function updateVoteBox($box, score, vote) {
    const v = Number(vote);
    const s = Number(score);
    $box.find(".score").text(s);
    $box.removeClass("is-up is-down");
    if (v === 1) $box.addClass("is-up");
    else if (v === -1) $box.addClass("is-down");
    $box.find(".btn-vote-up").attr("aria-pressed", v === 1);
    $box.find(".btn-vote-down").attr("aria-pressed", v === -1);
    $box.find(".score").toggleClass("text-danger", s < 0);
  }

  function bindVote(selectorUp, selectorDown, actionKey) {
    $(document).on("click", selectorUp + ", " + selectorDown, function (e) {
      e.preventDefault();
      const $btn = $(this);
      const up = $btn.is(selectorUp);
      const url = $btn.data("postUrl");
      if (!url) return;
      const $box = $btn.closest(".vote-box");
      $.ajax({
        url: url,
        method: "POST",
        data: { action: up ? "up" : "down" },
        dataType: "json",
      })
        .done(function (data) {
          if (data.ok) updateVoteBox($box, data.score, data.vote);
          else window.alert(data.message || data.error || "Ошибка");
        })
        .fail(function (xhr) {
          if (xhr.status === 401) {
            window.location.href = loginUrlWithNext();
            return;
          }
          let msg = "Не удалось отправить голос";
          if (xhr.status === 403) msg = "Нельзя голосовать за свой контент";
          try {
            const d = xhr.responseJSON || JSON.parse(xhr.responseText);
            if (d && d.error) msg = d.error;
            if (d && d.message) msg = d.message;
          } catch (err) {
            /* ignore */
          }
          window.alert(msg);
        });
    });
  }

  bindVote(".js-vote-question-up", ".js-vote-question-down");
  bindVote(".js-vote-answer-up", ".js-vote-answer-down");

  $(document).on("click", ".js-mark-correct", function (e) {
    e.preventDefault();
    const $btn = $(this);
    const url = $btn.data("postUrl");
    if (!url) return;
    $.ajax({
      url: url,
      method: "POST",
      dataType: "json",
    })
      .done(function (data) {
        if (!data.ok) {
          window.alert(data.message || data.error || "Ошибка");
          return;
        }
        window.location.reload();
      })
      .fail(function (xhr) {
        if (xhr.status === 401) {
          window.location.href = loginUrlWithNext();
          return;
        }
        let msg = "Не удалось отметить ответ";
        try {
          const d = xhr.responseJSON || JSON.parse(xhr.responseText);
          if (d && d.error) msg = d.error;
        } catch (err) {
          /* ignore */
        }
        window.alert(msg);
      });
  });
})(window.jQuery);
