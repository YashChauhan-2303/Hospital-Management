from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    # Root
    path('', views.index_redirect, name='index'),

    # Patient
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('records/', views.medical_records, name='medical_records'),
    path('bills/<int:bill_pk>/download/', views.download_bill, name='download_bill'),

    # Doctor
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/approve/<int:appointment_pk>/', views.approve_appointment, name='approve_appointment'),
    path('doctor/complete/<int:appointment_pk>/', views.complete_appointment, name='complete_appointment'),
    path('doctor/cancel/<int:appointment_pk>/', views.cancel_appointment, name='cancel_appointment'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
]
