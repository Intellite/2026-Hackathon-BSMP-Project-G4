from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app import db
from app.models.conversation import Conversation, ConversationMessage
from app.services.ai_service import AIService

from app.utils.survey_gating import survey_required


mentor_bp = Blueprint("mentor", __name__, url_prefix="/mentor")


@mentor_bp.get("/")
@login_required
@survey_required
def index() -> str:
    conversations = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template("mentor/index.html", conversations=conversations)


@mentor_bp.post("/chat")
@login_required
@survey_required
def chat() -> tuple[str, int] | tuple[dict, int]:
    payload = request.get_json(force=True)
    conversation_id = payload.get("conversation_id")
    message = payload.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    if conversation_id:
        conversation = db.session.get(Conversation, int(conversation_id))
    else:
        conversation = Conversation(user_id=current_user.id, title="New chat")
        db.session.add(conversation)
        db.session.flush()

    user_msg = ConversationMessage(
        conversation_id=conversation.id, role="user", content=message
    )
    db.session.add(user_msg)
    db.session.flush()

    ai = AIService()
    assistant_text = ai.chat_with_mentor(
        {
            "student_profile": {
                "name": current_user.name,
                "grade_level": current_user.grade_level,
                "school": current_user.school,
                "interests": current_user.interests,
                "career_goals": current_user.career_goals,
                "skills": current_user.skills,
                "activities": current_user.activities,
                "gpa": current_user.gpa,
            },
            "message": message,
        }
    )

    assistant_msg = ConversationMessage(
        conversation_id=conversation.id, role="assistant", content=assistant_text
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify(
        {
            "conversation_id": conversation.id,
            "reply": assistant_text,
        }
    )
