/* realtime обновление страницы вопроса через Centrifugo.
 *
 * Сценарии:
 *   - ответов не было → первый ответ должен корректно отобразиться;
 *   - пользователь на странице, где ответ должен оказаться → добавляем в DOM
 *     без перезагрузки (с учётом per_page);
 *   - пользователь на другой странице → alert (без вставки).
 */

(function () {
  "use strict";

  var ALERT_MESSAGE =
    "Появился новый ответ на этот вопрос. Обновите страницу или перейдите на нужную страницу пагинации, чтобы увидеть его.";

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function readInt(value, fallback) {
    var n = parseInt(value, 10);
    return Number.isFinite(n) && n > 0 ? n : fallback;
  }

  function renderAnswerHtml(payload, isQuestionAuthor) {
    var a = payload.answer || {};
    var author = a.author || {};
    var placeholder =
      (window.CupOfQ && window.CupOfQ.placeholderAvatar) ||
      "/static/core/img/avatar-placeholder.svg";
    var avatar = author.avatar_url || placeholder;
    var correctBlock = isQuestionAuthor
      ? '<button type="button" class="btn btn-link btn-sm text-start p-0 text-decoration-none js-mark-correct" data-post-url="/answer/' +
        encodeURIComponent(a.id) +
        '/correct/">Отметить как правильный</button>'
      : '<input class="form-check-input" type="checkbox" id="correct-' +
        encodeURIComponent(a.id) +
        '" disabled>' +
        '<label class="form-check-label small text-muted" for="correct-' +
        encodeURIComponent(a.id) +
        '">Только автор вопроса может отметить правильный ответ</label>';
    return (
      '<article id="answer-' +
      encodeURIComponent(a.id) +
      '" class="question-card mb-3 js-answer-row" data-answer-id="' +
      encodeURIComponent(a.id) +
      '">' +
      '<div class="row g-3">' +
      '<div class="col-auto d-flex flex-column align-items-center gap-2">' +
      '<img src="' +
      escapeHtml(avatar) +
      '" class="rounded-3 cq-avatar" width="48" height="48" alt="' +
      escapeHtml(author.display || "") +
      '">' +
      '<div class="vote-box" role="group" aria-label="Голосование за ответ">' +
      '<button type="button" class="btn-vote btn-vote-up" disabled title="Войдите, чтобы голосовать">▲</button>' +
      '<span class="score">0</span>' +
      '<button type="button" class="btn-vote btn-vote-down" disabled title="Войдите, чтобы голосовать">▼</button>' +
      "</div>" +
      "</div>" +
      '<div class="col">' +
      '<p class="mb-2">' +
      escapeHtml(a.text || "") +
      "</p>" +
      '<div class="answer-meta mb-2">' +
      "<span>Ответил <strong>" +
      escapeHtml(author.display || "") +
      "</strong></span>" +
      "<span>·</span>" +
      "<span>" +
      escapeHtml(a.created_display || "") +
      "</span>" +
      "</div>" +
      '<div class="form-check js-correct-wrap">' +
      correctBlock +
      "</div>" +
      "</div>" +
      "</div>" +
      "</article>"
    );
  }

  function ensureAnswersHeader(container) {
    var emptyMsg = container.querySelector(".js-no-answers");
    if (emptyMsg) {
      emptyMsg.remove();
    }
  }

  function appendAnswer(container, payload, isQuestionAuthor) {
    if (document.getElementById("answer-" + payload.answer.id)) {
      return false;
    }
    ensureAnswersHeader(container);
    container.insertAdjacentHTML(
      "beforeend",
      renderAnswerHtml(payload, isQuestionAuthor),
    );
    return true;
  }

  function createPublicationHandler(state) {
    return function (data) {
      if (!data || data.type !== "new_answer" || !data.answer) return;

      var answerId = data.answer.id;
      if (state.processed.has(answerId)) return;
      state.processed.add(answerId);

      state.totalAnswers += 1;

      var destinedPage = Math.ceil(state.totalAnswers / state.perPage);

      var author = data.answer.author || {};
      var isOwnAnswer =
        state.currentUsername &&
        author.username &&
        state.currentUsername === author.username;

      if (state.viewerPage === destinedPage) {
        appendAnswer(state.answersContainer, data, state.isQuestionAuthor);
        return;
      }

      if (!isOwnAnswer) {
        window.alert(ALERT_MESSAGE);
      }
    };
  }

  function bindSubscription(sub, onPublication) {
    if (!sub || sub.__cupofqBound) return;
    sub.__cupofqBound = true;
    sub.on("publication", function (ctx) {
      onPublication(ctx.data || {});
    });
    sub.on("error", function (ctx) {
      console.warn("centrifugo subscription error", ctx);
    });
  }

  function attachSubscription(centrifuge, channel, onPublication) {
    var sub = centrifuge.getSubscription(channel);
    if (!sub) {
      sub = centrifuge.newSubscription(channel);
    }
    bindSubscription(sub, onPublication);
  }

  async function init() {
    var page = document.getElementById("question-page");
    if (!page) return;
    var questionId = page.dataset.questionId;
    if (!questionId) return;
    var answersContainer = document.getElementById("answers-list");
    if (!answersContainer) return;

    if (typeof Centrifuge === "undefined") {
      console.warn("Centrifuge SDK is not loaded");
      return;
    }

    var state = {
      answersContainer: answersContainer,
      isQuestionAuthor: page.dataset.isQuestionAuthor === "1",
      viewerPage: readInt(page.dataset.currentPage, 1),
      perPage: readInt(page.dataset.perPage, 3),
      totalAnswers: readInt(page.dataset.answerCount, 0) || 0,
      currentUsername: page.dataset.currentUsername || "",
      processed: new Set(),
    };

    var tokenUrl =
      "/api/centrifugo/token/?question_id=" + encodeURIComponent(questionId);
    var tokenResp;
    try {
      tokenResp = await fetch(tokenUrl, { credentials: "same-origin" });
    } catch (e) {
      console.warn("centrifugo: cannot fetch token", e);
      return;
    }
    if (!tokenResp.ok) {
      console.warn("centrifugo: token HTTP", tokenResp.status);
      return;
    }
    var tokenData = await tokenResp.json();
    var channel =
      tokenData.channel || tokenData.namespace + ":question." + questionId;

    var centrifuge = new Centrifuge(tokenData.ws_url, {
      token: tokenData.token,
    });

    attachSubscription(centrifuge, channel, createPublicationHandler(state));

    centrifuge.on("error", function (ctx) {
      console.warn("centrifugo connection error", ctx);
    });

    centrifuge.connect();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
