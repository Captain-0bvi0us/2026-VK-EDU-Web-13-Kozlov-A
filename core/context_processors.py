from .sidebar import best_members_for_sidebar, popular_tags_for_sidebar


def sidebar_context(request):
    return {
        "popular_tags": popular_tags_for_sidebar(),
        "best_members": best_members_for_sidebar(),
    }
