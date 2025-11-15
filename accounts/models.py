"""
User model and authentication for OneStopRadio
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with additional fields for DJ platform"""
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # DJ-specific fields
    dj_name = models.CharField(max_length=100, blank=True, help_text="Stage/DJ name")
    bio = models.TextField(blank=True, max_length=500)
    
    # Account settings
    is_verified = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Trial and Premium features
    is_premium = models.BooleanField(default=False)
    trial_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.dj_name or self.username})"
    
    @property
    def full_name(self):
        """Return full name or username if names not provided"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username
    
    @property
    def display_name(self):
        """Return DJ name, full name, or username in that order"""
        return self.dj_name or self.full_name or self.username
    
    @property
    def is_trial_expired(self):
        """Check if trial period has expired"""
        if not self.trial_expires_at:
            return False
        return timezone.now() > self.trial_expires_at
    
    def start_trial(self):
        """Start 1-month free trial"""
        from datetime import timedelta
        self.trial_expires_at = timezone.now() + timedelta(days=30)
        self.save(update_fields=['trial_expires_at'])