from django import forms
from .models import Appointment, MedicalRecord
from django.contrib.auth import get_user_model

User = get_user_model()


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'symptoms']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-input'}),
            'appointment_type': forms.Select(attrs={'class': 'form-input'}),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe your symptoms or reason for visit...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show doctors in the dropdown
        self.fields['doctor'].queryset = User.objects.filter(
            role='DOCTOR', is_active=True
        ).select_related('doctor_profile').order_by('first_name')
        self.fields['doctor'].label = 'Select Doctor'
        self.fields['doctor'].empty_label = '— Choose a Doctor —'


class DoctorNoteForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Add consultation notes...',
            }),
        }


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['title', 'record_type', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Blood Test Report'}),
            'record_type': forms.Select(attrs={'class': 'form-input'}),
            'file': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.jpg,.jpeg,.png,.gif'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional description...'}),
        }
