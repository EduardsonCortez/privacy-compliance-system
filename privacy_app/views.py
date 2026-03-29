from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from reportlab.pdfgen import canvas
from datetime import datetime

from django.core.mail import send_mail
from django.conf import settings

from functools import wraps

from .forms import ConsentForm, DataBreachForm
from .models import PrivacyPolicy, ConsentRecord, DataBreachReport, AuditLog


# =========================
# 🔐 ROLE-BASED ACCESS CONTROL
# =========================
def role_required(allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect('login')

            try:
                role = request.user.userprofile.role
            except Exception:
                return redirect('login')

            if role not in allowed_roles:
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


# =========================
# 🌐 GET CLIENT IP
# =========================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


# =========================
# 🔐 CUSTOM LOGIN
# =========================
def custom_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            if not user.is_active:
                return render(request, 'login.html', {'error': 'Account disabled'})

            login(request, user)

            # 🔥 AUDIT LOG
            AuditLog.objects.create(
                user=user,
                action='LOGIN',
                description='User logged in',
                ip_address=get_client_ip(request)
            )

            try:
                role = user.userprofile.role
            except Exception:
                return redirect('login')

            if role in ['ADMIN', 'STAFF']:
                return redirect('dashboard')
            elif role == 'USER':
                return redirect('consent_form')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# =========================
# 🔓 LOGOUT (WITH AUDIT)
# =========================
def custom_logout(request):

    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action='LOGOUT',
            description='User logged out',
            ip_address=get_client_ip(request)
        )

    logout(request)
    return redirect('login')


# =========================
# 📊 DASHBOARD
# =========================
@login_required
@role_required(['ADMIN', 'STAFF'])
def dashboard(request):

    total_consents = ConsentRecord.objects.count()
    total_breaches = DataBreachReport.objects.count()

    low = DataBreachReport.objects.filter(severity="Low").count()
    medium = DataBreachReport.objects.filter(severity="Medium").count()
    high = DataBreachReport.objects.filter(severity="High").count()
    critical = DataBreachReport.objects.filter(severity="Critical").count()

    critical_alert = DataBreachReport.objects.filter(
        severity="Critical",
        status="Pending"
    ).exists()

    recent_logs = AuditLog.objects.order_by('-timestamp')[:5]
    recent_breaches = DataBreachReport.objects.order_by('-date_reported')[:5]

    context = {
        'total_consents': total_consents,
        'total_breaches': total_breaches,
        'low': low,
        'medium': medium,
        'high': high,
        'critical': critical,
        'critical_alert': critical_alert,
        'recent_breaches': recent_breaches,
        'recent_logs': recent_logs,
    }

    return render(request, 'dashboard.html', context)


# =========================
# 📋 CONSENT FORM
# =========================
@login_required
@role_required(['ADMIN', 'STAFF', 'USER'])
def consent_form(request):

    if request.method == 'POST':
        form = ConsentForm(request.POST)

        if form.is_valid():
            consent = form.save(commit=False)
            consent.user = request.user
            consent.ip_address = get_client_ip(request)
            consent.save()

            AuditLog.objects.create(
                user=request.user,
                action='CONSENT_SUBMITTED',
                description='User submitted consent',
                ip_address=get_client_ip(request)
            )

            return redirect('consent_form')

    else:
        form = ConsentForm()

    return render(request, 'consent_form.html', {'form': form})


# =========================
# 🚨 BREACH REPORT
# =========================
@login_required
@role_required(['ADMIN', 'STAFF'])
def breach_report(request):

    if request.method == 'POST':
        form = DataBreachForm(request.POST)

        if form.is_valid():
            breach = form.save(commit=False)
            breach.reported_by = request.user
            breach.save()

            ip = get_client_ip(request)

            AuditLog.objects.create(
                user=request.user,
                action='BREACH_REPORTED',
                description='Data breach reported',
                ip_address=ip
            )

            # 🔥 EMAIL ALERT
            if breach.severity == "Critical":
                send_mail(
                    subject="🚨 CRITICAL DATA BREACH ALERT",
                    message=f"""
A critical data breach has been reported.

Title: {breach.title}
Description: {breach.description}
Reported by: {request.user.username}
Status: {breach.status}

Immediate action is required.
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=True
                )

            return redirect('dashboard')

    else:
        form = DataBreachForm()

    return render(request, 'breach_report.html', {'form': form})


# =========================
# 📜 PRIVACY POLICY
# =========================
@login_required
@role_required(['ADMIN', 'STAFF', 'USER'])
def privacy_policy(request):

    policies = PrivacyPolicy.objects.filter(is_active=True)

    return render(request, 'privacy_policy.html', {'policies': policies})


# =========================
# 📄 PDF REPORT
# =========================
@login_required
@role_required(['ADMIN', 'STAFF'])
def generate_report(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="privacy_report.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Data Privacy Compliance Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Generated on: {datetime.now()}")

    total_consents = ConsentRecord.objects.count()
    total_breaches = DataBreachReport.objects.count()

    p.drawString(100, 720, f"Total Consents: {total_consents}")
    p.drawString(100, 700, f"Total Breaches: {total_breaches}")

    p.showPage()
    p.save()

    return response