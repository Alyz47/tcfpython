from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Address


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username', 'last_login', 'date_joined', 'active', 'admin', 'superuser')
    list_display_links = ('email',)
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    search_fields = ['pk', 'email', 'username']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'profile_picture', 'birth_date', 'created', 'modified')
    ordering = ('-created',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'country', 'city', 'street_address', 'postal_code']
    list_filter = ['country', 'city']
    search_fields = ['user__username', 'city', 'street_address', 'postal_code']


admin.site.register(Address, AddressAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
