from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .services import GeminiService


@login_required
@require_http_methods(['GET', 'POST'])
def ai_doctor_view(request):
    """AI Doctor pre-consultation form using Gemini."""
    report = None
    symptoms = ''

    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        if symptoms:
            report = GeminiService.get_preconsultation_report(symptoms)
        else:
            report = {'error': 'Please describe your symptoms before submitting.'}

    api_configured = GeminiService.is_configured()

    return render(request, 'api/ai_doctor.html', {
        'report': report,
        'symptoms': symptoms,
        'api_configured': api_configured,
    })
