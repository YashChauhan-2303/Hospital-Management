from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('ai-doctor/', views.ai_doctor_view, name='ai_doctor'),
    path('ai-doctor/analyze/', views.ai_doctor_json, name='ai_doctor_json'),
]
