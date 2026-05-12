import os
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .avatar_validators import validate_avatar_upload

SESSION_KEY_STAGED_AVATAR = "signup_staged_avatar"


def stage_signup_avatar(uploaded_file, session_key: str) -> dict:
    validate_avatar_upload(uploaded_file)
    name = os.path.basename(uploaded_file.name)[:200] or "image.jpg"
    ext = os.path.splitext(name)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"
    rel = f"temp_signup/{session_key}_{uuid.uuid4().hex}{ext}"
    default_storage.save(rel, ContentFile(uploaded_file.read()))
    return {"path": rel, "original_name": name}


def delete_staged(info: dict | None) -> None:
    if not info:
        return
    path = info.get("path")
    if path and default_storage.exists(path):
        default_storage.delete(path)
