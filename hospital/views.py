from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.http import FileResponse, Http404
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, MedicalRecord, Billing
from .forms import AppointmentForm, DoctorNoteForm, MedicalRecordForm
from .utils import generate_billing_pdf

User = get_user_model()


def role_required(role):
    """Decorator to restrict views to specific roles."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login')
            if request.user.role != role:
                messages.error(request, 'Access denied.')
                return redirect('users:login')
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorator


# ─── ROOT REDIRECT ────────────────────────────────────────────────────────────

def index_redirect(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return redirect('users:login')


# ─── PATIENT VIEWS ───────────────────────────────────────────────────────────

@login_required
@role_required('PATIENT')
def patient_dashboard(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('doctor', 'doctor__doctor_profile').order_by('-appointment_date')

    upcoming = appointments.filter(status__in=['PENDING', 'APPROVED'])
    completed = appointments.filter(status='COMPLETED')
    bills = Billing.objects.filter(
        appointment__patient=request.user
    ).select_related('appointment').order_by('-issued_at')
    records = MedicalRecord.objects.filter(patient=request.user).order_by('-uploaded_at')[:5]

    context = {
        'appointments': upcoming,
        'completed_appointments': completed,
        'bills': bills,
        'recent_records': records,
        'total_appointments': appointments.count(),
        'pending_count': upcoming.filter(status='PENDING').count(),
        'approved_count': upcoming.filter(status='APPROVED').count(),
        'completed_count': completed.count(),
    }
    return render(request, 'hospital/patient_dashboard.html', context)


@login_required
@role_required('PATIENT')
def book_appointment(request):
    doctors = User.objects.filter(role='DOCTOR', is_active=True).select_related('doctor_profile')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = Appointment.STATUS_PENDING
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Awaiting doctor approval.')
            return redirect('hospital:patient_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()

    return render(request, 'hospital/book_appointment.html', {
        'form': form,
        'doctors': doctors,
    })


@login_required
@role_required('PATIENT')
def medical_records(request):
    records = MedicalRecord.objects.filter(patient=request.user).order_by('-uploaded_at')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = request.user
            record.save()
            messages.success(request, 'Medical record uploaded successfully!')
            return redirect('hospital:medical_records')
        else:
            messages.error(request, 'Error uploading record. Please check the file.')
    else:
        form = MedicalRecordForm()

    return render(request, 'hospital/medical_records.html', {
        'records': records,
        'form': form,
    })


@login_required
def download_bill(request, bill_pk):
    bill = get_object_or_404(Billing, pk=bill_pk, appointment__patient=request.user)
    if not bill.pdf_file:
        raise Http404("Bill PDF not found.")
    return FileResponse(bill.pdf_file.open('rb'), as_attachment=True, filename=f'Invoice-{bill.pk:05d}.pdf')


# ─── DOCTOR VIEWS ────────────────────────────────────────────────────────────

@login_required
@role_required('DOCTOR')
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(
        doctor=request.user
    ).select_related('patient').order_by('-appointment_date')

    pending = appointments.filter(status='PENDING')
    approved = appointments.filter(status='APPROVED')
    completed = appointments.filter(status='COMPLETED')

    context = {
        'pending_appointments': pending,
        'approved_appointments': approved,
        'completed_appointments': completed,
        'total_count': appointments.count(),
        'pending_count': pending.count(),
        'approved_count': approved.count(),
        'completed_count': completed.count(),
    }
    return render(request, 'hospital/doctor_dashboard.html', context)


@login_required
@role_required('DOCTOR')
def approve_appointment(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk, doctor=request.user)
    appointment.status = Appointment.STATUS_APPROVED
    appointment.save()
    messages.success(request, f'Appointment with {appointment.patient.get_full_name()} approved!')
    return redirect('hospital:doctor_dashboard')


@login_required
@role_required('DOCTOR')
def complete_appointment(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk, doctor=request.user)

    if request.method == 'POST':
        note_form = DoctorNoteForm(request.POST, instance=appointment)
        if note_form.is_valid():
            appointment = note_form.save(commit=False)
            appointment.status = Appointment.STATUS_COMPLETED
            appointment.save()

            # Auto-generate billing
            try:
                fee = appointment.doctor.doctor_profile.consultation_fee
            except Exception:
                fee = 500.00

            billing = Billing.objects.create(
                appointment=appointment,
                amount=fee,
            )

            # Check if payment was received
            is_paid = note_form.cleaned_data.get('is_paid', False)
            if is_paid:
                billing.mark_paid()
                messages.success(request, 'Appointment completed and payment recorded!')
            else:
                generate_billing_pdf(billing)
                billing.save()
                messages.success(request, 'Appointment completed and invoice generated!')

            return redirect('hospital:doctor_dashboard')
    else:
        note_form = DoctorNoteForm(instance=appointment)

    return render(request, 'hospital/complete_appointment.html', {
        'appointment': appointment,
        'note_form': note_form,
    })


@login_required
@role_required('DOCTOR')
def doctor_analytics(request):
    """Doctor analytics and earnings dashboard."""
    # Analytics data for earnings and consultations
    completed_appointments = Appointment.objects.filter(
        doctor=request.user,
        status='COMPLETED'
    ).select_related('billing')

    total_consultations = completed_appointments.count()

    # Get billing info
    billings = Billing.objects.filter(
        appointment__doctor=request.user
    ).select_related('appointment')

    total_earnings = billings.aggregate(total=Sum('amount'))['total'] or 0
    paid_earnings = billings.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    pending_earnings = billings.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0

    # Monthly earnings (last 6 months)
    now = timezone.now()
    monthly_earnings = []
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (now - timedelta(days=30*(i-1))).replace(day=1) if i > 0 else now

        month_total = Billing.objects.filter(
            appointment__doctor=request.user,
            issued_at__gte=month_start,
            issued_at__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_earnings.append({
            'month': month_start.strftime('%b %Y'),
            'earnings': float(month_total)
        })

    # Recent completed with fees
    recent_completed = completed_appointments[:10]

    context = {
        'total_consultations': total_consultations,
        'total_earnings': float(total_earnings),
        'paid_earnings': float(paid_earnings),
        'pending_earnings': float(pending_earnings),
        'average_fee': float(total_earnings / total_consultations) if total_consultations > 0 else 0,
        'monthly_earnings': monthly_earnings,
        'recent_completed': recent_completed,
    }
    return render(request, 'hospital/doctor_analytics.html', context)


@login_required
@role_required('DOCTOR')
def cancel_appointment(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk, doctor=request.user)
    appointment.status = Appointment.STATUS_CANCELLED
    appointment.save()
    messages.info(request, 'Appointment cancelled.')
    return redirect('hospital:doctor_dashboard')


@login_required
@role_required('DOCTOR')
def toggle_payment_status(request, billing_pk):
    """Toggle payment status for a billing record."""
    billing = get_object_or_404(Billing, pk=billing_pk, appointment__doctor=request.user)

    if request.method == 'POST':
        # Toggle payment status
        if billing.is_paid:
            billing.is_paid = False
            billing.paid_at = None
            messages.info(request, 'Payment marked as unpaid.')
        else:
            billing.is_paid = True
            billing.paid_at = timezone.now()
            messages.success(request, 'Payment marked as paid!')

        billing.save()

    # Redirect to referrer or analytics page
    referrer = request.META.get('HTTP_REFERER', 'hospital:doctor_analytics')
    return redirect(referrer) if referrer else redirect('hospital:doctor_analytics')




# ─── ADMIN VIEWS ─────────────────────────────────────────────────────────────

@login_required
@role_required('ADMIN')
def admin_dashboard(request):
    total_patients = User.objects.filter(role='PATIENT').count()
    total_doctors = User.objects.filter(role='DOCTOR').count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='PENDING').count()
    completed_appointments = Appointment.objects.filter(status='COMPLETED').count()

    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor'
    ).order_by('-created_at')[:10]

    doctors = User.objects.filter(role='DOCTOR').select_related('doctor_profile').annotate(
        appt_count=Count('doctor_appointments')
    ).order_by('-appt_count')[:8]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'recent_appointments': recent_appointments,
        'top_doctors': doctors,
    }
    return render(request, 'hospital/admin_dashboard.html', context)
