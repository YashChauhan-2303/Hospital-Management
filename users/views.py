from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import PatientRegistrationForm, DoctorRegistrationForm, CustomLoginForm
from .models import CustomUser


def home_redirect(request):
    """Redirect root URL to appropriate dashboard."""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return redirect('users:login')


def register_view(request):
    """Unified registration page with role selection."""
    role = request.GET.get('role', 'patient').upper()

    if role == 'DOCTOR':
        form_class = DoctorRegistrationForm
        form_title = 'Register as Doctor'
    else:
        form_class = PatientRegistrationForm
        form_title = 'Register as Patient'
        role = 'PATIENT'

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to MediCare HMS, {user.get_full_name() or user.username}!')
            return redirect(user.get_dashboard_url())
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = form_class()

    return render(request, 'users/register.html', {
        'form': form,
        'form_title': form_title,
        'role': role,
    })


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Custom login view with role-based redirect."""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(user.get_dashboard_url())
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Logout and redirect to login page."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('users:login')
