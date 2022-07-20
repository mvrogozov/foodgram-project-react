from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'login',
        'name',
        'surname',
        'email'
    )
    search_fields = ('username', 'email')
    list_filter = ('username',)


admin.site.register(User, UserAdmin)
