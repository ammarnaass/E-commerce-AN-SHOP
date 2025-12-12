from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'is_customer', 'email_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('معلومات شخصية'), {'fields': ('first_name', 'last_name', 'phone_number', 
                                          'profile_image', 'date_of_birth')}),
        (_('الصلاحيات'), {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                    'is_customer', 'groups', 'user_permissions')}),
        (_('التحقق'), {'fields': ('email_verified', 'phone_verified')}),
        (_('التواريخ'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'city']
    search_fields = ['user__email', 'full_name', 'phone_number', 'city']
    readonly_fields = ['created_at', 'updated_at']
