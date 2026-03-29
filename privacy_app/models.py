from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# =========================
# USER PROFILE (ROLE SYSTEM 🔥)
# =========================
class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('STAFF', 'Staff'),
        ('USER', 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# AUTO CREATE USER PROFILE
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'ADMIN' if instance.is_superuser else 'USER'
        UserProfile.objects.create(user=instance, role=role)


# =========================
# CONSENT RECORDS
# =========================
class ConsentRecord(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    purpose = models.TextField()
    consent_given = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_submitted']

    def __str__(self):
        return f"{self.full_name} - Consent"


# =========================
# DATA BREACH REPORT
# =========================
class DataBreachReport(models.Model):

    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Investigating', 'Investigating'),
        ('Resolved', 'Resolved'),
    ]

    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="No Title")  # FIX 🔥
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    affected_users = models.IntegerField(default=0)
    date_reported = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_reported']

    def __str__(self):
        return f"Breach Report #{self.id} - {self.severity}"


# =========================
# PRIVACY POLICY
# =========================
class PrivacyPolicy(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title


# =========================
# AUDIT LOG
# =========================
class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('CONSENT_SUBMITTED', 'Consent Submitted'),
        ('BREACH_REPORTED', 'Breach Reported'),
        ('POLICY_UPDATED', 'Policy Updated'),
        ('LOGOUT', 'User Logout'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"