def user_display_name(user) -> str:
    full = (user.get_full_name() or "").strip()
    return full if full else user.get_username()
