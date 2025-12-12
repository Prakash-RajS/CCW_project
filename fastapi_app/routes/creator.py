import fastapi_app.django_setup

from typing import Optional, List
from django.db.models import Q
from fastapi import APIRouter, HTTPException, Query

from creator_app.models import UserData, CreatorProfile

router = APIRouter(prefix="/creator", tags=["Creator"])


# ------------------------------------------------
# FILTER CREATORS  (ADDED — NOTHING REMOVED)
# ------------------------------------------------
@router.get("/search")
def search_creators(
    search: Optional[str] = None,
    niche: Optional[str] = None,
    creator_type: Optional[str] = None,
    location: Optional[str] = None,
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
    platforms: Optional[List[str]] = Query(None),
    experience_level: Optional[str] = None,
    collaboration_type: Optional[str] = None,
):
    profiles = CreatorProfile.objects.all()

    # Text search
    if search:
        profiles = profiles.filter(
            Q(creator_name__icontains=search) |
            Q(primary_niche__icontains=search)
        )

    # Filters
    if niche:
        profiles = profiles.filter(primary_niche__iexact=niche)

    if creator_type:
        profiles = profiles.filter(creator_type__iexact=creator_type)

    if location:
        profiles = profiles.filter(location__icontains=location)

    if min_followers is not None:
        profiles = profiles.filter(followers__gte=min_followers)

    if max_followers is not None:
        profiles = profiles.filter(followers__lte=max_followers)

    if experience_level:
        profiles = profiles.filter(experience_level__iexact=experience_level)

    if collaboration_type:
        profiles = profiles.filter(collaboration_type__iexact=collaboration_type)

    # Multi-platform filter (OR logic)
    if platforms:
        q = Q()
        for p in platforms:
            q |= Q(platforms__icontains=p)
        profiles = profiles.filter(q)

    return [
        {
            "user_id": p.user.id,
            "email": p.user.email,
            "creator_name": p.creator_name,
            "creator_type": p.creator_type,
            "primary_niche": p.primary_niche,
            "location": p.location,
            "followers": p.followers,
            "platforms": p.platforms,
            "experience_level": p.experience_level,
            "collaboration_type": p.collaboration_type,
            "project_type": p.project_type,
        }
        for p in profiles
    ]


# ------------------------------------------------
# Create / Update Creator Profile (USER ID VERSION)
# ------------------------------------------------
@router.post("/save/{user_id}")
def save_creator_profile(
    user_id: int,
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
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
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


# ------------------------------------------------
# Get Creator Profile by USER ID
# ------------------------------------------------
@router.get("/get/{user_id}")
def get_creator_profile(user_id: int):
    try:
        user = UserData.objects.get(id=user_id)
        profile = CreatorProfile.objects.get(user=user)
    except (UserData.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    return {
        "user_id": user_id,
        "email": user.email,
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


# ------------------------------------------------
# List All Creators
# ------------------------------------------------
@router.get("/list")
def list_creators():
    profiles = CreatorProfile.objects.all()

    return [
        {
            "user_id": p.user.id,
            "email": p.user.email,
            "creator_name": p.creator_name,
            "creator_type": p.creator_type,
            "primary_niche": p.primary_niche,
            "location": p.location,
            "followers": p.followers,
        }
        for p in profiles
    ]


# ------------------------------------------------
# Delete Creator Profile by USER ID
# ------------------------------------------------
@router.delete("/delete/{user_id}")
def delete_creator_profile(user_id: int):
    try:
        user = UserData.objects.get(id=user_id)
        CreatorProfile.objects.get(user=user).delete()
    except (UserData.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    return {"message": "Creator profile deleted"}


# ------------------------------------------------
# Edit Creator Profile (USER ID VERSION)
# ------------------------------------------------
@router.put("/edit/{user_id}")
def edit_creator_profile(
    user_id: int,
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
        user = UserData.objects.get(id=user_id)
        profile = CreatorProfile.objects.get(user=user)
    except (UserData.DoesNotExist, CreatorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Creator profile not found")

    if creator_name is not None: profile.creator_name = creator_name
    if creator_type is not None: profile.creator_type = creator_type
    if experience_level is not None: profile.experience_level = experience_level
    if primary_niche is not None: profile.primary_niche = primary_niche
    if secondary_niche is not None: profile.secondary_niche = secondary_niche
    if platforms is not None: profile.platforms = platforms
    if followers is not None: profile.followers = followers
    if portfolio_category is not None: profile.portfolio_category = portfolio_category
    if portfolio_link is not None: profile.portfolio_link = portfolio_link
    if collaboration_type is not None: profile.collaboration_type = collaboration_type
    if project_type is not None: profile.project_type = project_type
    if location is not None: profile.location = location

    profile.save()

    return {"message": "Creator profile updated successfully"}
