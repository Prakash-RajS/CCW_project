import fastapi_app.django_setup
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from creator_app.models import UserData
from django.conf import settings
import os

router = APIRouter(prefix='/profile', tags=['Profile'])

BASE_DIR = settings.BASE_DIR


# ------------------------------
# GET USER DATA BY ID
# ------------------------------
@router.get('/get/{user_id}')
def get_user_data(user_id: int):
    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        'profile_pic': user.profile_pic.url if user.profile_pic else None,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'address': user.address,
        'city': user.city,
        'state': user.state
    }


# ------------------------------
# EDIT USER DATA USING USER ID
# ------------------------------
@router.put('/edit/{user_id}')
def edit_user_data(
    user_id: int,
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    phone_number: str | None = Form(None),
    address: str | None = Form(None),
    city: str | None = Form(None),
    state: str | None = Form(None),
    profile_pic: UploadFile | None = File(None)
):
    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if phone_number is not None:
        user.phone_number = phone_number
    if address is not None:
        user.address = address
    if city is not None:
        user.city = city
    if state is not None:
        user.state = state

    # Handle profile picture upload
    if profile_pic is not None:
        save_path = os.path.join(BASE_DIR, "fastapi_app", "profile_pic")
        os.makedirs(save_path, exist_ok=True)

        file_path = os.path.join(save_path, profile_pic.filename)

        with open(file_path, "wb") as f:
            f.write(profile_pic.file.read())

        user.profile_pic = f"profile_pic/{profile_pic.filename}"

    user.save()

    return {"message": "UserData updated successfully"}
