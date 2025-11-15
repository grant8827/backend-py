"""
Admin configuration for user management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin with custom fields"""
    
    list_display = ('email', 'username', 'dj_name', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'dj_name', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('DJ Profile', {
            'fields': ('dj_name', 'bio', 'avatar')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Settings', {
            'fields': ('is_verified', 'email_notifications')
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Profile', {
            'fields': ('first_name', 'last_name', 'dj_name'),
        }),
    )