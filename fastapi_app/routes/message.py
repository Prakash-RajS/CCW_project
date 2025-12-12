from fastapi_app.django_setup import setup_django
setup_django()

from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Request, Query
from pydantic import BaseModel
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from creator_app.models import UserData, Conversation, Message

router = APIRouter(prefix="/message", tags=["Messaging"])


# -------------------------------
# Pydantic Schema
# -------------------------------
class SendMessage(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


# -------------------------------
# Helper: get or create conversation
# -------------------------------
def get_or_create_conversation(user1, user2):
    convo = Conversation.objects.filter(
        Q(user1=user1, user2=user2) |
        Q(user1=user2, user2=user1)
    ).first()

    if convo:
        return convo

    return Conversation.objects.create(user1=user1, user2=user2)


# -------------------------------
# List users (for left panel)
# -------------------------------
@router.get("/users")
def list_users(current_user_id: int = Query(...)):

    users = UserData.objects.all()
    now = timezone.now()
    result = []

    for u in users:
        if not u.id:
            continue
        if u.id == current_user_id:
            continue

        # Online if active in last 60 seconds
        online = False
        if u.last_active:
            online = (now - u.last_active) <= timedelta(seconds=60)

        # Last message preview
        convo_qs = Conversation.objects.filter(
            Q(user1_id=current_user_id, user2=u) |
            Q(user1=u, user2_id=current_user_id)
        )

        last_msg = Message.objects.filter(
            conversation__in=convo_qs
        ).order_by("-created_at").first()

        display_name = (u.first_name or "") or (u.email or f"User {u.id}")

        result.append({
            "id": u.id,
            "name": display_name,
            "online": online,
            "last_message": last_msg.content if last_msg else "",
            "last_message_time": last_msg.created_at if last_msg else None,
        })

    return result


# -------------------------------
# Typing status (UPDATED)
# -------------------------------
class TypingPayload(BaseModel):
    user_id: int
    chat_with: int      # NEW
    is_typing: bool


@router.post("/typing")
def set_typing(payload: TypingPayload):
    user = UserData.objects.filter(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # NEW — typing user + who they are typing to
    user.typing_with = payload.chat_with
    user.is_typing = payload.is_typing
    user.last_active = timezone.now()

    user.save(update_fields=["is_typing", "typing_with", "last_active"])

    return {"status": "ok"}


# -------------------------------
# Send Message (supports reply + file)
# -------------------------------
@router.post("/send")
def send_message(
    sender_id: int = Form(...),
    receiver_id: int = Form(...),
    content: str = Form(None),
    reply_to: int = Form(None),
    file: UploadFile = File(None)
):
    sender = UserData.objects.filter(id=sender_id).first()
    receiver = UserData.objects.filter(id=receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    # Update sender state
    sender.last_active = timezone.now()
    sender.is_typing = False
    sender.typing_with = None
    sender.save(update_fields=["last_active", "is_typing", "typing_with"])

    convo = get_or_create_conversation(sender, receiver)

    reply_obj = None
    if reply_to:
        reply_obj = Message.objects.filter(id=reply_to).first()

    file_path = None
    if file:
        import shutil, os
        from django.conf import settings

        folder = os.path.join(settings.MEDIA_ROOT, "message_files")
        os.makedirs(folder, exist_ok=True)

        save_path = os.path.join(folder, file.filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = f"message_files/{file.filename}"

    msg = Message.objects.create(
        conversation=convo,
        sender=sender,
        content=content,
        reply_to=reply_obj,
        file=file_path
    )

    return {
        "status": "success",
        "conversation_id": convo.id,
        "message_id": msg.id,
        "reply_to": reply_to,
        "created_at": msg.created_at
    }


# -------------------------------
# Get All Messages between 2 users
# -------------------------------
@router.get("/conversation/{user1_id}/{user2_id}")
def get_messages(request: Request, user1_id: int, user2_id: int):

    user1 = UserData.objects.filter(id=user1_id).first()
    user2 = UserData.objects.filter(id=user2_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="User not found")

    now = timezone.now()
    user1.last_active = now
    user1.save(update_fields=["last_active"])

    convo = Conversation.objects.filter(
        Q(user1=user1, user2=user2) |
        Q(user1=user2, user2=user1)
    ).first()

    if not convo:
        return {
            "conversation_id": None,
            "messages": [],
            "other_user_online": False,
            "other_user_typing": (user2.is_typing and user2.typing_with == user1_id),  # UPDATED
            "other_user_last_active": user2.last_active,
        }

    msgs = convo.messages.order_by("created_at")

    def get_file_url(file_obj):
        if not file_obj:
            return None
        return f"{request.base_url}media/{file_obj.name}"

    def get_message_type(file_obj):
        if not file_obj:
            return "text"
        ext = file_obj.name.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
            return "image"
        return "file"

    online = False
    if user2.last_active:
        online = (now - user2.last_active) <= timedelta(seconds=60)

    return {
        "conversation_id": convo.id,
        "other_user_online": online,
        "other_user_typing": (user2.is_typing and user2.typing_with == user1_id),  # UPDATED
        "other_user_last_active": user2.last_active,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender.id,
                "content": m.content,
                "file_url": get_file_url(m.file),
                "message_type": get_message_type(m.file),

                "reply_to": (
                    {
                        "id": m.reply_to.id,
                        "content": m.reply_to.content,
                        "file_url": get_file_url(m.reply_to.file),
                        "message_type": get_message_type(m.reply_to.file),
                    }
                    if m.reply_to else None
                ),

                "is_seen": m.is_seen,
                "created_at": m.created_at
            }
            for m in msgs
        ]
    }


# -------------------------------
# Mark as Seen
# -------------------------------
@router.post("/seen/{conversation_id}/{user_id}")
def mark_seen(conversation_id: int, user_id: int):

    convo = Conversation.objects.filter(id=conversation_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    viewer = UserData.objects.filter(id=user_id).first()
    if viewer:
        viewer.last_active = timezone.now()
        viewer.save(update_fields=["last_active"])

    Message.objects.filter(
        conversation=convo
    ).exclude(sender__id=user_id).update(is_seen=True)

    return {"status": "seen updated"}
