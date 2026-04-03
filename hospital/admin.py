from django.contrib import admin
from .models import Appointment, MedicalRecord, Billing


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'status', 'created_at']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['patient__username', 'doctor__username', 'patient__first_name', 'doctor__first_name']
    raw_id_fields = ['patient', 'doctor']
    ordering = ['-appointment_date', '-appointment_time']
    actions = ['mark_approved', 'mark_completed']

    def mark_approved(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f'{queryset.count()} appointment(s) marked as Approved.')
    mark_approved.short_description = 'Mark selected as Approved'

    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
        self.message_user(request, f'{queryset.count()} appointment(s) marked as Completed.')
    mark_completed.short_description = 'Mark selected as Completed'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'title', 'record_type', 'uploaded_at']
    list_filter = ['record_type', 'uploaded_at']
    search_fields = ['patient__username', 'title']
    raw_id_fields = ['patient']


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'amount', 'is_paid', 'issued_at', 'paid_at']
    list_filter = ['is_paid', 'issued_at']
    search_fields = ['appointment__patient__username']
    raw_id_fields = ['appointment']
