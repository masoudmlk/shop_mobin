from django.contrib import admin

from core.models import AuthToken, User

admin.site.register(User)


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('token_key', 'user', 'created', 'expiry',)
    fields = ()
    raw_id_fields = ('user',)

