import fastapi_app.django_setup

from typing import Optional
from django.db.models import Q
from fastapi import APIRouter, HTTPException, Query

from creator_app.models import UserData, CollaboratorProfile

router = APIRouter(prefix="/collaborator", tags=["Collaborator"])


# ------------------------------------------------
# FILTER COLLABORATORS  (ADDED — NOTHING REMOVED)
# ------------------------------------------------
@router.get("/search")
def search_collaborators(
    search: Optional[str] = None,
    skill_category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    experience: Optional[str] = None,
    language: Optional[str] = None,
    availability: Optional[str] = None
):
    profiles = CollaboratorProfile.objects.all()

    if search:
        profiles = profiles.filter(
            Q(name__icontains=search) |
            Q(skill_category__icontains=search)
        )

    if skill_category:
        profiles = profiles.filter(skill_category__iexact=skill_category)

    if location:
        profiles = profiles.filter(location__icontains=location)

    if min_price is not None:
        profiles = profiles.filter(pricing_amount__gte=min_price)

    if max_price is not None:
        profiles = profiles.filter(pricing_amount__lte=max_price)

    if experience:
        profiles = profiles.filter(experience__iexact=experience)

    if language:
        profiles = profiles.filter(language__icontains=language)

    if availability:
        profiles = profiles.filter(availability__iexact=availability)

    return [
        {
            "id": p.id,
            "email": p.user.email,
            "name": p.name,
            "skill_category": p.skill_category,
            "pricing": f"{p.pricing_amount} {p.pricing_unit}",
            "location": p.location,
            "experience": p.experience,
            "language": p.language,
            "availability": p.availability,
            "social_link": p.social_link,
            "portfolio_link": p.portfolio_link,
        }
        for p in profiles
    ]


# ------------------------------------------------
# Create / Update Collaborator Profile (USER ID VERSION)
# ------------------------------------------------
@router.post("/save/{user_id}")
def save_collaborator_profile(
    user_id: int,
    name: str,
    language: str,
    skill_category: str,
    experience: str,
    pricing_amount: float | None = None,
    pricing_unit: str | None = None,
    availability: str | None = None,
    timing: str | None = None,
    social_link: str | None = None,
    portfolio_link: str | None = None,
    badges: str | None = None,
    skills_rating: int | None = None,
    about: str | None = None,
    location: str | None = None,
):
    try:
        user = UserData.objects.get(id=user_id)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    profile, created = CollaboratorProfile.objects.update_or_create(
        user=user,
        defaults={
            "name": name,
            "language": language,
            "skill_category": skill_category,
            "experience": experience,
            "pricing_amount": pricing_amount,
            "pricing_unit": pricing_unit,
            "availability": availability,
            "timing": timing,
            "social_link": social_link,
            "portfolio_link": portfolio_link,
            "badges": badges,
            "skills_rating": skills_rating,
            "about": about,
            "location": location,
        },
    )

    user.role = "collaborator"
    user.save()

    return {"message": "Collaborator profile saved", "created": created}


# ------------------------------------------------
# Get Collaborator Profile by USER ID
# ------------------------------------------------
@router.get("/get/{user_id}")
def get_collaborator_profile(user_id: int):
    try:
        user = UserData.objects.get(id=user_id)
        profile = CollaboratorProfile.objects.get(user=user)
    except (UserData.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "user_id": user_id,
        "email": user.email,
        "name": profile.name,
        "language": profile.language,
        "skill_category": profile.skill_category,
        "experience": profile.experience,
        "pricing_amount": profile.pricing_amount,
        "pricing_unit": profile.pricing_unit,
        "availability": profile.availability,
        "timing": profile.timing,
        "social_link": profile.social_link,
        "portfolio_link": profile.portfolio_link,
        "badges": profile.badges,
        "skills_rating": profile.skills_rating,
        "about": profile.about,
        "location": profile.location,
    }


# ------------------------------------------------
# List All Collaborators
# ------------------------------------------------
@router.get("/list")
def list_collaborators():
    profiles = CollaboratorProfile.objects.all()
    return [
        {
            "user_id": p.user.id,
            "email": p.user.email,
            "name": p.name,
            "skill_category": p.skill_category,
            "location": p.location,
        }
        for p in profiles
    ]


# ------------------------------------------------
# Delete Collaborator Profile by USER ID
# ------------------------------------------------
@router.delete("/delete/{user_id}")
def delete_collaborator_profile(user_id: int):
    try:
        user = UserData.objects.get(id=user_id)
        CollaboratorProfile.objects.get(user=user).delete()
    except (UserData.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Collaborator profile deleted"}


# ------------------------------------------------
# Edit Collaborator Profile (USER ID VERSION)
# ------------------------------------------------
@router.put("/edit/{user_id}")
def edit_collaborator_profile(
    user_id: int,
    name: str | None = None,
    language: str | None = None,
    skill_category: str | None = None,
    experience: str | None = None,
    pricing_amount: float | None = None,
    pricing_unit: str | None = None,
    availability: str | None = None,
    timing: str | None = None,
    social_link: str | None = None,
    portfolio_link: str | None = None,
    badges: str | None = None,
    skills_rating: int | None = None,
    about: str | None = None,
    location: str | None = None,
):
    try:
        user = UserData.objects.get(id=user_id)
        profile = CollaboratorProfile.objects.get(user=user)
    except (UserData.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Collaborator profile not found")

    if name is not None: profile.name = name
    if language is not None: profile.language = language
    if skill_category is not None: profile.skill_category = skill_category
    if experience is not None: profile.experience = experience
    if pricing_amount is not None: profile.pricing_amount = pricing_amount
    if pricing_unit is not None: profile.pricing_unit = pricing_unit
    if availability is not None: profile.availability = availability
    if timing is not None: profile.timing = timing
    if social_link is not None: profile.social_link = social_link
    if portfolio_link is not None: profile.portfolio_link = portfolio_link
    if badges is not None: profile.badges = badges
    if skills_rating is not None: profile.skills_rating = skills_rating
    if about is not None: profile.about = about
    if location is not None: profile.location = location

    profile.save()

    return {"message": "Collaborator profile updated successfully"}
