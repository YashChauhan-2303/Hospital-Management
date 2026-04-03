from django.db import models
from django.conf import settings
from django.utils import timezone


class Appointment(models.Model):
    """Appointment between patient and doctor."""

    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TYPE_ONLINE = 'ONLINE'
    TYPE_OFFLINE = 'OFFLINE'

    TYPE_CHOICES = [
        (TYPE_ONLINE, 'Online (Video Call)'),
        (TYPE_OFFLINE, 'Offline (In-Person)'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'},
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'},
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default=TYPE_OFFLINE
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    symptoms = models.TextField(blank=True, help_text='Describe your symptoms')
    notes = models.TextField(blank=True, help_text='Doctor notes (filled after consultation)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"{self.patient.get_full_name()} → Dr. {self.doctor.get_full_name()} on {self.appointment_date}"

    def can_join_meeting(self):
        """Returns True if patient can join the online meeting."""
        return (
            self.appointment_type == self.TYPE_ONLINE
            and self.status == self.STATUS_APPROVED
        )

    def get_gmeet_url(self):
        """Returns doctor's Google Meet URL if applicable."""
        try:
            return self.doctor.doctor_profile.gmeet_url
        except Exception:
            return ''


class MedicalRecord(models.Model):
    """Patient medical vault — file uploads."""

    RECORD_TYPES = [
        ('LAB_REPORT', 'Lab Report'),
        ('PRESCRIPTION', 'Prescription'),
        ('SCAN', 'Scan / Imaging'),
        ('DISCHARGE', 'Discharge Summary'),
        ('OTHER', 'Other'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records',
        limit_choices_to={'role': 'PATIENT'},
    )
    title = models.CharField(max_length=200)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='OTHER')
    file = models.FileField(upload_to='medical_records/%Y/%m/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.patient.get_full_name()} — {self.title}"

    def is_image(self):
        name = self.file.name.lower()
        return name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))

    def is_pdf(self):
        return self.file.name.lower().endswith('.pdf')


class Billing(models.Model):
    """Auto-generated billing record when appointment is completed."""

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='billing',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='bills/%Y/%m/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Bill #{self.pk} — {self.appointment.patient.get_full_name()} — ₹{self.amount}"

    def mark_paid(self):
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save()
