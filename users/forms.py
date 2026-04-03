from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, DoctorProfile


class PatientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}),
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'form-input'}),
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-input'
            field.widget.attrs['autocomplete'] = 'off'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_PATIENT
        user.phone = self.cleaned_data.get('phone', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    specialization = forms.ChoiceField(
        choices=DoctorProfile.SPECIALIZATIONS,
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
    consultation_fee = forms.DecimalField(
        max_digits=8, decimal_places=2, initial=500,
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
    )
    gmeet_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://meet.google.com/...'}),
    )
    experience_years = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_DOCTOR
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                consultation_fee=self.cleaned_data['consultation_fee'],
                gmeet_url=self.cleaned_data.get('gmeet_url', ''),
                experience_years=self.cleaned_data.get('experience_years', 0),
                bio=self.cleaned_data.get('bio', ''),
            )
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username or Email', 'autofocus': True}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
    )
