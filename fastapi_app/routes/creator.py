import fastapi_app.django_setup

from fastapi import APIRouter, HTTPException
from creator_app.models import User, CreatorProfile

router = APIRouter(prefix="/creator", tags=["Creator"])


# ------------------------------
# Create / Update Creator Profile
# ------------------------------
@router.post("/save")
def save_creator_profile(
    email: str,
    creator_name: str,
    creator_type: str,
    experience_level: str,
    primary_niche: str,
    secondary_niche: str | None = None,
    platforms: str | None = None,
    followers: int | None = None,
    portfolio_category: str | None = None,
    portfolio_link: str | None = None,
    collaboration_type: str | None = None,
    project_type: str | None = None,
    location: str | None = None,
):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    profile, created = CreatorProfile.objects.update_or_create(
        user=user,
        defaults={
            "creator_name": creator_name,
            "creator_type": creator_type,
            "experience_level": experience_level,
            "primary_niche": primary_niche,
            "secondary_niche": secondary_niche,
            "platforms": platforms,
            "followers": followers,
            "portfolio_category": portfolio_category,
            "portfolio_link": portfolio_link,
            "collaboration_type": collaboration_type,
            "project_type": project_type,
            "location": location,
        },
    )

    user.role = "creator"
    user.save()

    return {"message": "Creator profile saved", "created": created}


# ------------------------------
# Get Creator Profile
# ------------------------------
@router.get("/get/{email}")
def get_creator_profile(email: str):
    try:
        user = User.objects.get(email=email)
        profile = CreatorProfile.objects.get(user=user)
    except (User.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    return {
        "email": email,
        "creator_name": profile.creator_name,
        "creator_type": profile.creator_type,
        "experience_level": profile.experience_level,
        "primary_niche": profile.primary_niche,
        "secondary_niche": profile.secondary_niche,
        "platforms": profile.platforms,
        "followers": profile.followers,
        "portfolio_category": profile.portfolio_category,
        "portfolio_link": profile.portfolio_link,
        "collaboration_type": profile.collaboration_type,
        "project_type": profile.project_type,
        "location": profile.location,
    }


# ------------------------------
# List All Creators (FIND CREATOR)
# ------------------------------
@router.get("/list")
def list_creators():
    profiles = CreatorProfile.objects.all()

    return [
        {
            "email": p.user.email,
            "creator_name": p.creator_name,
            "creator_type": p.creator_type,
            "primary_niche": p.primary_niche,
            "location": p.location,
            "followers": p.followers,
        }
        for p in profiles
    ]


# ------------------------------
# Delete Creator Profile
# ------------------------------
@router.delete("/delete/{email}")
def delete_creator_profile(email: str):
    try:
        user = User.objects.get(email=email)
        CreatorProfile.objects.get(user=user).delete()
    except (User.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    return {"message": "Creator profile deleted"}


# ------------------------------
# EDIT Creator Profile
# ------------------------------
@router.put("/edit")
def edit_creator_profile(
    email: str,
    creator_name: str | None = None,
    creator_type: str | None = None,
    experience_level: str | None = None,
    primary_niche: str | None = None,
    secondary_niche: str | None = None,
    platforms: str | None = None,
    followers: int | None = None,
    portfolio_category: str | None = None,
    portfolio_link: str | None = None,
    collaboration_type: str | None = None,
    project_type: str | None = None,
    location: str | None = None,
):
    try:
        user = User.objects.get(email=email)
        profile = CreatorProfile.objects.get(user=user)
    except (User.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    # Update ONLY provided fields
    if creator_name is not None:
        profile.creator_name = creator_name
    if creator_type is not None:
        profile.creator_type = creator_type
    if experience_level is not None:
        profile.experience_level = experience_level
    if primary_niche is not None:
        profile.primary_niche = primary_niche
    if secondary_niche is not None:
        profile.secondary_niche = secondary_niche
    if platforms is not None:
        profile.platforms = platforms
    if followers is not None:
        profile.followers = followers
    if portfolio_category is not None:
        profile.portfolio_category = portfolio_category
    if portfolio_link is not None:
        profile.portfolio_link = portfolio_link
    if collaboration_type is not None:
        profile.collaboration_type = collaboration_type
    if project_type is not None:
        profile.project_type = project_type
    if location is not None:
        profile.location = location

    profile.save()

    return {"message": "Creator profile updated successfully"}

