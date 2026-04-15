"""
Gemini AI Service for Pre-Consultation Reports.
Falls back gracefully when GEMINI_API_KEY is not configured.
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Wrapper around the Gemini generative AI API."""

    # Try latest models first, then fall back to older ones
    MODEL_NAMES = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
    MODEL_NAME = 'gemini-2.5-flash'

    SYSTEM_PROMPT = """You are a senior medical AI assistant for MediCare HMS.
A patient will describe their symptoms. Your job is to generate a professional
Pre-Consultation Report with the following JSON structure ONLY (no extra text):

{
  "urgency": "LOW | MEDIUM | HIGH | CRITICAL",
  "urgency_reason": "Brief reason for urgency level",
  "recommended_specialist": "Doctor specialty name",
  "specialist_reason": "Why this specialist",
  "summary": "2-3 sentence clinical summary of the patient's condition",
  "key_symptoms": ["symptom1", "symptom2", "symptom3"],
  "suggested_tests": ["test1", "test2"],
  "lifestyle_tips": ["tip1", "tip2"],
  "disclaimer": "This is an AI-generated pre-consultation report and is not a medical diagnosis."
}

Be accurate, empathetic, and professional. Always include the disclaimer."""

    @classmethod
    def is_configured(cls):
        return bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != 'your_gemini_api_key_here')

    @classmethod
    def get_preconsultation_report(cls, symptoms: str) -> dict:
        """
        Call Gemini API with patient symptoms and return a structured report.

        Returns a dict with keys:
          urgency, urgency_reason, recommended_specialist, specialist_reason,
          summary, key_symptoms, suggested_tests, lifestyle_tips, disclaimer, error (if any)
        """
        if not cls.is_configured():
            return cls._fallback_response(symptoms, error="Gemini API key not configured. Please add GEMINI_API_KEY to your .env file.")

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)

            # Try each model in order
            last_error = None
            for model_name in cls.MODEL_NAMES:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=cls.SYSTEM_PROMPT,
                    )

                    prompt = f"Patient's symptoms: {symptoms}"
                    response = model.generate_content(prompt)
                    raw_text = response.text.strip()

                    # Strip markdown fences if present
                    if raw_text.startswith('```'):
                        raw_text = raw_text.split('```')[1]
                        if raw_text.startswith('json'):
                            raw_text = raw_text[4:]
                        raw_text = raw_text.strip()

                    report = json.loads(raw_text)
                    report['error'] = None
                    logger.info(f"Successfully used model: {model_name}")
                    return report
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Model {model_name} failed: {e}. Trying next model...")
                    continue

            # If all models fail, return error
            if last_error:
                logger.error(f"All models failed. Last error: {last_error}")
                return cls._fallback_response(symptoms, error="Could not reach Gemini API. Please try again later.")

        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parse error: {e}")
            return cls._fallback_response(symptoms, error="Could not parse AI response. Please try again.")

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return cls._fallback_response(symptoms, error=f"AI service error: {str(e)}")

    @classmethod
    def _fallback_response(cls, symptoms: str, error: str = None) -> dict:
        """Returns a demo/fallback response when API is unavailable."""
        return {
            'urgency': 'MEDIUM',
            'urgency_reason': 'Based on described symptoms — AI analysis not available.',
            'recommended_specialist': 'General Physician',
            'specialist_reason': 'A general physician can do initial assessment and refer accordingly.',
            'summary': f'The patient has described the following symptoms: {symptoms[:200]}. '
                       'A professional medical evaluation is recommended for accurate diagnosis.',
            'key_symptoms': [s.strip() for s in symptoms.split(',')[:4]] or ['Unspecified symptoms'],
            'suggested_tests': ['Complete Blood Count (CBC)', 'Basic Metabolic Panel'],
            'lifestyle_tips': ['Stay hydrated', 'Get adequate rest', 'Monitor symptoms closely'],
            'disclaimer': 'This is an AI-generated pre-consultation report and is not a medical diagnosis.',
            'error': error,
        }
