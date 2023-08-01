from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import User

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'is_staff', 'is_superuser']
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email', 'username')

    # fieldsets = (
    #                 (None, {'fields': ('username', 'email', 'password', 'userpic', 'phone', 'phone_verify')}),
    #                 ('Персональная информация', {'fields': ('first_name', 'last_name', 'date_of_birth')}),
    #                 ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    #             )
    # add_fieldsets = (
    #     (None, {'fields': ('userpic', 'phone', 'phone_verify', 'date_of_birth')}),
    #     ('Персональная информация', {'fields': ('date_of_birth')}),
    # )

