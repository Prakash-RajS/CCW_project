from django.db import models
from django.contrib.auth.hashers import make_password, check_password


# ============================================================
# USER MODEL
# ============================================================

class User(models.Model):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)

    # Role → "creator" or "collaborator"
    role = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Hash password
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    # Verify password
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email


# ============================================================
# CREATOR PROFILE MODEL
# ============================================================

class CreatorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    creator_name = models.CharField(max_length=255)

    creator_type = models.CharField(max_length=255)
    experience_level = models.CharField(max_length=100)

    primary_niche = models.CharField(max_length=255)
    secondary_niche = models.CharField(max_length=255, blank=True, null=True)

    platforms = models.CharField(max_length=255, blank=True, null=True)
    followers = models.IntegerField(blank=True, null=True)

    portfolio_category = models.CharField(max_length=255)
    portfolio_link = models.URLField(blank=True, null=True)

    collaboration_type = models.CharField(max_length=255)
    project_type = models.CharField(max_length=255)

    location = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Creator Profile"


# ============================================================
# COLLABORATOR PROFILE MODEL
# ============================================================

class CollaboratorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    language = models.CharField(max_length=100)

    skill_category = models.CharField(max_length=255)
    experience = models.CharField(max_length=100)

    pricing_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pricing_unit = models.CharField(max_length=50, blank=True, null=True)

    availability = models.CharField(max_length=255, blank=True, null=True)
    timing = models.CharField(max_length=255, blank=True, null=True)

    social_link = models.URLField(blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)

    badges = models.CharField(max_length=255, blank=True, null=True)
    skills_rating = models.IntegerField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Collaborator Profile"


# ============================================================
# SOCIAL LOGIN USER MODEL (Auth0 / Google / Facebook)
# ============================================================

class UserData(models.Model):
    id = models.AutoField(primary_key=True)

    # social login email (Google, Facebook)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)

    provider = models.CharField(max_length=50, blank=True, null=True)  # google / facebook / auth0

    password = models.CharField(max_length=255, blank=True, null=True)  # social login hash

    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    # Social login ID like: google-oauth2|12938129381293
    userid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    # Verify password
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    

    def __str__(self):
        return f"{self.email} ({self.provider})"


# ============================================================
# TEST MODEL
# ============================================================

class TestModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
