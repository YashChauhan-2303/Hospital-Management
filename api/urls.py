from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('ai-doctor/', views.ai_doctor_view, name='ai_doctor'),
]
