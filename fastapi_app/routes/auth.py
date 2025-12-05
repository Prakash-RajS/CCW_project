import fastapi_app.django_setup

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from creator_app.models import User, UserData

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

import re
import time
import logging
import os
import requests
import jwt
import urllib.parse
from random import randint
from dotenv import load_dotenv

load_dotenv()

# ================================
# Router & Templates
# ================================
router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="fastapi_app/templates")
logger = logging.getLogger(__name__)

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

OTP_CACHE = {}

# ================================
# Helper Functions
# ================================

def get_user_by_email(email: str):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def create_user(email: str, phone_number: str, password: str, role: str | None = None):
    if UserData.objects.filter(email=email).exists():
        raise HTTPException(400, "Email already exists")

    if UserData.objects.filter(phone_number=phone_number).exists():
        raise HTTPException(400, "Phone already exists")

    user = UserData(email=email, phone_number=phone_number, role=role or "")
    user.set_password(password)
    user.save()  # <-- IMPORTANT

    return user



def hash_password(value: str):
    return make_password(value)


def get_provider_from_sub(sub: str):
    if not sub:
        return "auth0"
    return sub.split("|", 1)[0]


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
        raise HTTPException(
            400,
            "Weak password. Must include upper, lower, number, special char & 8+ chars."
        )

    # FIXED — pass 'phone' as phone_number
    user = create_user(email=email, phone_number=phone, password=password, role=role)

    # Save to database
    user.save()

    return {"message": "Signup successful"}



# ================================
# LOGIN
# ================================
@router.post("/login")
def login(email: str, password: str):
    user = get_user_by_email(email)

    if not user or not user.check_password(password):
        raise HTTPException(401, "Invalid email or password")

    return {"message": "Login successful", "role": user.role}


# ================================
# OTP SEND
# ================================
@router.post("/forgot-password/send-otp")
def send_otp(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "Email not found")

    otp = randint(100000, 999999)
    OTP_CACHE[email] = {"otp": otp, "expires": time.time() + 60}

    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP is {otp}. It expires in 60 seconds.",
        from_email=None,
        recipient_list=[email],
    )

    return {"message": "OTP sent"}


# ================================
# OTP VERIFY
# ================================
@router.post("/forgot-password/verify-otp")
def verify_otp(email: str, otp: int):
    if email not in OTP_CACHE:
        raise HTTPException(400, "OTP not requested")

    record = OTP_CACHE[email]

    if time.time() > record["expires"]:
        del OTP_CACHE[email]
        raise HTTPException(400, "OTP expired")

    if record["otp"] != otp:
        raise HTTPException(400, "Invalid OTP")

    return {"message": "OTP verified"}


# ================================
# PASSWORD RESET
# ================================
@router.post("/forgot-password/reset")
def reset_password(email: str, old_password: str, new_password: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(404, "User not found")

    if not user.check_password(old_password):
        raise HTTPException(400, "Incorrect old password")

    user.set_password(new_password)
    return {"message": "Password reset successful"}


# ============================================================
# 🔥 PROVIDER-SPECIFIC LOGIN ROUTES (ADDED NOW)
# ============================================================

@router.get("/auth0/login/google")
def login_google():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email"
        f"&connection=google-oauth2"
    )
    return RedirectResponse(url)


@router.get("/auth0/login/facebook")
def login_facebook():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email"
        f"&connection=facebook"
    )
    return RedirectResponse(url)


@router.get("/auth0/login/apple")
def login_apple():
    url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&scope=openid profile email"
        f"&connection=apple"
    )
    return RedirectResponse(url)


# ================================
# AUTH0 CALLBACK LOGIC
# ================================
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

    logger.warning(f"AUTH0 SUB: {sub}")
    logger.warning(f"PROVIDER DETECTED: {provider}")

    # 🔥 ADDED FALLBACK — ONLY CHANGE YOU ASKED FOR
    if not email:
        email = f"{sub.replace('|', '_')}@facebook.local"
        logger.warning(f"NO EMAIL FROM AUTH0 → USING FALLBACK EMAIL: {email}")

    user_data, created = UserData.objects.get_or_create(
        email=email,
        defaults={
            "first_name": decoded.get("given_name") or "",
            "last_name": decoded.get("family_name") or "",
            "provider": provider,
            "userid": sub,
            "password": hash_password(sub),
        },
    )

    return {
        "message": "Auth0 login successful",
        "email": email,
        "provider": provider,
        "next_step": "choose_role"
    }


@router.get("/auth0/callback")
def auth0_callback(code: str = None, error: str = None, error_description: str = None):
    if error:
        raise HTTPException(400, f"Auth0 Error: {error} → {error_description}")

    if not code:
        raise HTTPException(400, "Missing 'code' parameter from Auth0")

    return _auth0_callback_logic(code)


# ================================
# HTML TEST PAGE
# ================================
@router.get("/auth-test", response_class=HTMLResponse)
def auth_test(request: Request):
    return templates.TemplateResponse("auth_test.html", {"request": request})
