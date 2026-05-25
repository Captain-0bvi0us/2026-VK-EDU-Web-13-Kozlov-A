from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="questions.tasks.publish_new_answer")
def publish_new_answer(question_id: int, answer_id: int) -> bool:
    from core.centrifugo import publish, question_channel
    from core.utils import user_display_name
    from django.utils import formats, timezone

    from .models import Answer

    try:
        answer = (
            Answer.objects.select_related("author", "author__profile", "question")
            .get(pk=answer_id, question_id=question_id)
        )
    except Answer.DoesNotExist:
        logger.warning("publish_new_answer: ответ %s не найден", answer_id)
        return False

    avatar_url = ""
    try:
        if answer.author.profile and answer.author.profile.avatar:
            avatar_url = answer.author.profile.avatar.url
    except Exception:  # noqa: BLE001
        avatar_url = ""

    created_local = timezone.localtime(answer.created_at)
    payload = {
        "type": "new_answer",
        "answer": {
            "id": answer.pk,
            "text": answer.text,
            "author": {
                "username": answer.author.get_username(),
                "display": user_display_name(answer.author),
                "avatar_url": avatar_url,
            },
            "created_at": answer.created_at.isoformat(),
            "created_display": formats.date_format(created_local, "j E Y, H:i"),
        },
    }
    return publish(question_channel(question_id), payload)
