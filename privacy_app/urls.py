from django.urls import path
from . import views

urlpatterns = [

    # 🏠 Dashboard
    path('', views.dashboard, name='dashboard'),

    # 📝 Consent Form
    path('consent/', views.consent_form, name='consent_form'),

    # 🚨 Breach Report
    path('breach/', views.breach_report, name='breach_report'),

    # 📜 Privacy Policy
    path('policy/', views.privacy_policy, name='privacy_policy'),

    # 📄 PDF Report
    path('report/pdf/', views.generate_report, name='generate_report'),

    # 🔓 Logout (🔥 IMPORTANT ADD)
    path('logout/', views.custom_logout, name='logout'),

    # 🔐 (OPTIONAL fallback)
    # path('home/', views.dashboard, name='home'),
]