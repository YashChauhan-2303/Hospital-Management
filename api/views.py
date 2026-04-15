from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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


@login_required
@require_http_methods(['POST'])
def ai_doctor_json(request):
    """JSON API endpoint for AI Doctor - returns instant health tips and feedback."""
    try:
        data = json.loads(request.body)
        symptoms = data.get('symptoms', '').strip()

        if not symptoms:
            return JsonResponse({
                'success': False,
                'error': 'Please describe your symptoms before submitting.'
            }, status=400)

        # Get AI analysis from Gemini
        report = GeminiService.get_preconsultation_report(symptoms)

        return JsonResponse({
            'success': True,
            'data': report
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)
