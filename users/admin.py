from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = UserAdmin.fieldsets + (
        ('HMS Role & Info', {
            'fields': ('role', 'phone', 'date_of_birth', 'profile_picture'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('HMS Role & Info', {
            'fields': ('role', 'phone', 'date_of_birth'),
        }),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'consultation_fee', 'experience_years', 'is_available']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
