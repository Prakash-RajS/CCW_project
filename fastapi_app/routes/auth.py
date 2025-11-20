import fastapi_app.django_setup  # ✅ Load Django first

from fastapi import APIRouter
from creator_app.models import TestModel  # Now safe to import
          
router = APIRouter()

@router.get("/test-django")
def test_django():
    items = TestModel.objects.all()
    return {
        "count": items.count(),
        "items": [i.name for i in items]
    }
