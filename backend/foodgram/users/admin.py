from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    search_fields = ('username', 'email')
    list_filter = ('username',)


admin.site.register(User, UserAdmin)
