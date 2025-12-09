import fastapi_app.django_setup

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from creator_app.models import UserData

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

import re
import time
import logging
import os
import requests
import jwt
from random import randint
from dotenv import load_dotenv

load_dotenv()

# ================================
# Router & Templates
# ================================
router = APIRouter(prefix="/auth", tags=["Authentication"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATE_DIR)
logger = logging.getLogger(__name__)

# ================================
# TEST PAGE ROUTE
# ================================
@router.get("/auth-test", response_class=HTMLResponse)
def auth_test(request: Request):
    return templates.TemplateResponse("auth_test.html", {"request": request})


# ================================
# Auth0 SETTINGS
# ================================
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv(
    "AUTH0_CALLBACK_URL",
    "http://localhost:8000/auth/auth0/callback"
)

# ================================
# OTP CACHE & CONFIG
# ================================
OTP_CACHE = {}
OTP_EXPIRY = 600            # 10 minutes
RESEND_COOLDOWN = 5         # seconds


def hash_password(value: str):
    return make_password(value)


# ================================
# SIGNUP
# ================================
@router.post("/signup")
def signup(email: str, phone: str, password: str, role: str | None = None):

    strong_regex = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
        r"(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )

    if not re.match(strong_regex, password):
        raise HTTPException(400, "Weak password")

    if UserData.objects.filter(email=email).exists():
        raise HTTPException(400, "Email already exists")

    user = UserData(email=email, phone_number=phone, role=role or "")
    user.set_password(password)
    user.save()

    return {"message": "Signup successful", "user_id": user.id}


# ================================
# LOGIN
# ================================
@router.post("/login")
def login(email: str, password: str):

    try:
        user = UserData.objects.get(email=email)
    except UserData.DoesNotExist:
        raise HTTPException(401, "Invalid email or password")

    if not user.check_password(password):
        raise HTTPException(401, "Invalid email or password")

    return {"message": "Login successful", "user_id": user.id, "role": user.role}


# ================================
# SEND OTP
# ================================
@router.post("/forgot-password/send-otp")
def send_otp(email: str):

    try:
        user = UserData.objects.get(email=email)
    except UserData.DoesNotExist:
        raise HTTPException(404, "Email not found")

    otp = randint(100000, 999999)
    now = time.time()

    OTP_CACHE[email] = {
        "otp": otp,
        "expires": now + OTP_EXPIRY,
        "sent_time": now
    }

    message = (
        f"Hello,\n\n"
        f"Your verification code is: {otp}\n\n"
        f"Do not share this code with anyone.\n\n"
        f"– Stackly.AI Security Team"
    )

    send_mail(
        subject="Your Stackly.AI OTP Code",
        message=message,
        from_email=None,
        recipient_list=[email],
    )

    return {"message": "OTP sent"}


# ================================
# RESEND OTP
# ================================
@router.post("/forgot-password/resend-otp")
def resend_otp(email: str):

    if email in OTP_CACHE:
        record = OTP_CACHE[email]
        now = time.time()

        if now - record.get("sent_time") < RESEND_COOLDOWN:
            raise HTTPException(
                429,
                f"Please wait {RESEND_COOLDOWN} seconds before resending OTP."
            )

    return send_otp(email)


# ================================
# VERIFY OTP
# ================================
@router.post("/forgot-password/verify-otp")
def verify_otp(email: str, otp: int):

    if email not in OTP_CACHE:
        raise HTTPException(400, "OTP not requested")

    entry = OTP_CACHE[email]

    if time.time() > entry["expires"]:
        del OTP_CACHE[email]
        raise HTTPException(400, "OTP expired")

    if entry["otp"] != otp:
        raise HTTPException(400, "Invalid OTP")

    return {"message": "OTP verified"}


# ================================
# RESET PASSWORD
# ================================
@router.post("/forgot-password/reset")
def reset_password(email: str, new_password: str, confirm_password: str):

    if new_password != confirm_password:
        raise HTTPException(400, "Passwords do not match")

    try:
        user = UserData.objects.get(email=email)
    except UserData.DoesNotExist:
        raise HTTPException(404, "User not found")

    user.set_password(new_password)

    return {"message": "Password reset successful"}


# ================================
# CHANGE PASSWORD (USER ID)
# ================================
@router.post("/change-password/{user_id}")
def change_password(user_id: int, old_password: str, new_password: str, confirm_password: str):

    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        raise HTTPException(404, "User not found")

    if not user.check_password(old_password):
        raise HTTPException(400, "Old password incorrect")

    if new_password != confirm_password:
        raise HTTPException(400, "Passwords do not match")

    strong_regex = (
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
        r"(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )
    if not re.match(strong_regex, new_password):
        raise HTTPException(400, "Weak password")

    user.set_password(new_password)

    return {"message": "Password changed successfully"}


# ================================
# AUTH0 SOCIAL LOGIN ROUTES
# ================================
@router.get("/auth0/login/google")
def login_google():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email&connection=google-oauth2"
    )
    return RedirectResponse(url)


@router.get("/auth0/login/facebook")
def login_facebook():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email&connection=facebook"
    )
    return RedirectResponse(url)


@router.get("/auth0/login/apple")
def login_apple():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email&connection=apple"
    )
    return RedirectResponse(url)


# ================================
# AUTH0 CALLBACK LOGIC (FIXED)
# ================================
def get_provider_from_sub(sub: str):
    return sub.split("|", 1)[0] if sub else "auth0"


def _auth0_callback_logic(code: str):

    token_res = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": AUTH0_CALLBACK_URL,
        }
    )

    tokens = token_res.json()

    if "id_token" not in tokens:
        raise HTTPException(400, "Token exchange failed")

    decoded = jwt.decode(tokens["id_token"], options={"verify_signature": False})

    email = decoded.get("email")
    sub = decoded.get("sub")
    provider = get_provider_from_sub(sub)

    if not email:
        email = f"{sub.replace('|', '_')}@noemail.local"

    # ============================================================
    # 🔥 FIX: Prevent UNIQUE constraint error on userid
    # ============================================================
    existing_user = UserData.objects.filter(userid=sub).first()

    if existing_user:
        return {
            "message": "Auth0 login successful",
            "user_id": existing_user.id,
            "email": existing_user.email,
            "provider": existing_user.provider,
            "next_step": "choose_role"
        }

    # If new → create fresh user
    user_data = UserData.objects.create(
        email=email,
        first_name=decoded.get("given_name") or "",
        last_name=decoded.get("family_name") or "",
        provider=provider,
        userid=sub,
        password=hash_password(sub),
    )

    return {
        "message": "Auth0 login successful",
        "user_id": user_data.id,
        "email": email,
        "provider": provider,
        "next_step": "choose_role"
    }


@router.get("/auth0/callback")
def auth0_callback(code: str = None, error: str = None, error_description: str = None):

    if error:
        raise HTTPException(400, f"Auth0 Error: {error} – {error_description}")

    if not code:
        raise HTTPException(400, "Missing 'code' parameter")

    return _auth0_callback_logic(code)
