from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Profile

User = get_user_model()

admin.site.site_header = "CupOfQ — админка"
admin.site.site_title = "CupOfQ"
admin.site.index_title = "Панель управления"


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "профиль"
    fk_name = "user"
    extra = 1
    max_num = 1


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = (*DjangoUserAdmin.inlines, ProfileInline)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "has_avatar"]
    list_select_related = ["user"]
    search_fields = ["user__username", "user__email", "user__first_name", "user__last_name"]
    raw_id_fields = ["user"]

    @staticmethod
    @admin.display(description="есть аватар", boolean=True)
    def has_avatar(obj: Profile) -> bool:
        return bool(obj.avatar)
