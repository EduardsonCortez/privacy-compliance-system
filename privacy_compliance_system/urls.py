# privacy_compliance_system/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from privacy_app import views  # 🔥 IMPORTANT FIX

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Custom Login (role-based)
    path('login/', views.custom_login, name='login'),

    # 🔓 Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 🌐 App URLs
    path('', include('privacy_app.urls')),
]