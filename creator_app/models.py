from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone  # make sure this import exists at the top



# ============================================================
# CREATOR PROFILE MODEL
# ============================================================

class CreatorProfile(models.Model):
    user = models.OneToOneField("creator_app.UserData", on_delete=models.CASCADE)

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
    user = models.OneToOneField("creator_app.UserData", on_delete=models.CASCADE)

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
# ONLY USER TABLE
# ============================================================

class UserData(models.Model):
    id = models.AutoField(primary_key=True)

    email = models.EmailField(unique=True, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)

    provider = models.CharField(max_length=50, blank=True, null=True)

    password = models.CharField(max_length=255, blank=True, null=True)

    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    role = models.CharField(max_length=50, blank=True, null=True)

    userid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)

    last_active = models.DateTimeField(null=True, blank=True)
    is_typing = models.BooleanField(default=False)
    # NEW — required for accurate typing indicator
    typing_with = models.IntegerField(null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.email} ({self.provider})"


# ============================================================
# MESSAGE MODELS
# ============================================================

class Conversation(models.Model):
    user1 = models.ForeignKey("creator_app.UserData", on_delete=models.CASCADE, related_name="convo_user1")
    user2 = models.ForeignKey("creator_app.UserData", on_delete=models.CASCADE, related_name="convo_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Conversation between {self.user1.email} and {self.user2.email}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("creator_app.UserData", on_delete=models.CASCADE)

    content = models.TextField()
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW — Reply support
    reply_to = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies"
    )

    # NEW — File attachment support
    file = models.FileField(
        upload_to="message_files/",
        null=True,
        blank=True
    )

    message_type = models.CharField(max_length=20, default="text")
    seen_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"


# ============================================================
# TEST MODEL
# ============================================================

class TestModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
