import fastapi_app.django_setup
from fastapi import APIRouter, HTTPException
from creator_app.models import User, CollaboratorProfile

router = APIRouter(prefix="/collaborator", tags=["Collaborator"])

# ------------------------------
# Create / Update Collaborator Profile
# ------------------------------
@router.post("/save")
def save_collaborator_profile(
    email: str,
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
        user = User.objects.get(email=email)
    except User.DoesNotExist:
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


# ------------------------------
# Get Collaborator Profile
# ------------------------------
@router.get("/get/{email}")
def get_collaborator_profile(email: str):
    try:
        user = User.objects.get(email=email)
        profile = CollaboratorProfile.objects.get(user=user)
    except (User.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "email": email,
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


# ------------------------------
# Delete Collaborator Profile
# ------------------------------
@router.delete("/delete/{email}")
def delete_collaborator_profile(email: str):
    try:
        user = User.objects.get(email=email)
        CollaboratorProfile.objects.get(user=user).delete()
    except (User.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Collaborator profile deleted"}


# ------------------------------
# List All Collaborators
# ------------------------------
@router.get("/list")
def list_collaborators():
    profiles = CollaboratorProfile.objects.all()
    return [
        {
            "email": p.user.email,
            "name": p.name,
            "skill_category": p.skill_category,
            "location": p.location,
        }
        for p in profiles
    ]

# ------------------------------
# EDIT Collaborator Profile
# ------------------------------
@router.put("/edit")
def edit_collaborator_profile(
    email: str,
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
        user = User.objects.get(email=email)
        profile = CollaboratorProfile.objects.get(user=user)
    except (User.DoesNotExist, CollaboratorProfile.DoesNotExist):
        raise HTTPException(status_code=404, detail="Collaborator profile not found")

    # Update ONLY provided fields
    if name is not None:
        profile.name = name
    if language is not None:
        profile.language = language
    if skill_category is not None:
        profile.skill_category = skill_category
    if experience is not None:
        profile.experience = experience
    if pricing_amount is not None:
        profile.pricing_amount = pricing_amount
    if pricing_unit is not None:
        profile.pricing_unit = pricing_unit
    if availability is not None:
        profile.availability = availability
    if timing is not None:
        profile.timing = timing
    if social_link is not None:
        profile.social_link = social_link
    if portfolio_link is not None:
        profile.portfolio_link = portfolio_link
    if badges is not None:
        profile.badges = badges
    if skills_rating is not None:
        profile.skills_rating = skills_rating
    if about is not None:
        profile.about = about
    if location is not None:
        profile.location = location

    profile.save()

    return {"message": "Collaborator profile updated successfully"}
