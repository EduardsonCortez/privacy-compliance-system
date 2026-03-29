from django.contrib import admin
from .models import ConsentRecord, DataBreachReport, PrivacyPolicy, AuditLog, UserProfile


# =========================
# USER PROFILE ADMIN 🔥
# =========================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)


# =========================
# CONSENT RECORDS ADMIN
# =========================
@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):

    list_display = ('full_name', 'email', 'purpose', 'consent_given', 'date_submitted')
    search_fields = ('full_name', 'email')


# =========================
# DATA BREACH REPORT ADMIN
# =========================
@admin.register(DataBreachReport)
class DataBreachReportAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'severity', 'status', 'date_reported')
    list_filter = ('severity', 'status')


# =========================
# PRIVACY POLICY ADMIN
# =========================
@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):

    list_display = ('title', 'is_active', 'date_posted')
    search_fields = ('title',)


# =========================
# AUDIT LOG ADMIN
# =========================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action',)
    search_fields = ('user__username',)