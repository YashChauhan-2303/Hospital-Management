from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user with role-based access control."""

    ROLE_ADMIN = 'ADMIN'
    ROLE_DOCTOR = 'DOCTOR'
    ROLE_PATIENT = 'PATIENT'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_DOCTOR, 'Doctor'),
        (ROLE_PATIENT, 'Patient'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_PATIENT,
    )
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', null=True, blank=True
    )

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    def get_dashboard_url(self):
        from django.urls import reverse
        if self.role == self.ROLE_ADMIN:
            return reverse('hospital:admin_dashboard')
        elif self.role == self.ROLE_DOCTOR:
            return reverse('hospital:doctor_dashboard')
        return reverse('hospital:patient_dashboard')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class DoctorProfile(models.Model):
    """Extended profile for doctors."""

    SPECIALIZATIONS = [
        ('General Physician', 'General Physician'),
        ('Cardiologist', 'Cardiologist'),
        ('Neurologist', 'Neurologist'),
        ('Orthopedist', 'Orthopedist'),
        ('Dermatologist', 'Dermatologist'),
        ('Pediatrician', 'Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
        ('Gynecologist', 'Gynecologist'),
        ('Ophthalmologist', 'Ophthalmologist'),
        ('ENT Specialist', 'ENT Specialist'),
        ('Oncologist', 'Oncologist'),
        ('Endocrinologist', 'Endocrinologist'),
        ('Gastroenterologist', 'Gastroenterologist'),
        ('Pulmonologist', 'Pulmonologist'),
        ('Urologist', 'Urologist'),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
    )
    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATIONS,
        default='General Physician',
    )
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=500.00
    )
    gmeet_url = models.URLField(blank=True, help_text='Google Meet link for online consultations')
    experience_years = models.PositiveIntegerField(default=0)
    available_days = models.CharField(
        max_length=200,
        default='Monday,Tuesday,Wednesday,Thursday,Friday',
        help_text='Comma-separated days',
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} — {self.specialization}"
