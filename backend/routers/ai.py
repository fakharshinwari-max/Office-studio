"""AI proxy — Writer/Sheets/Slides Copilot actions."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import User, AIUsage
from ..services.ai_provider import chat
from ..config import get_settings

router = APIRouter(prefix="/api/ai", tags=["ai"])
settings = get_settings()


class AIRequest(BaseModel):
    app: str                       # word | sheets | slides
    action: str                    # summarize | rewrite | translate | ...
    context: str = ""              # selection / data user chose to send
    options: dict = {}             # extra params (tone, language, etc.)


SYSTEM_PROMPTS = {
    "word": "You are a writing assistant inside a word processor. Be concise and correct.",
    "sheets": "You are a spreadsheet assistant. Return valid Excel formulas or plain tabular text.",
    "slides": "You are a presentation assistant. Return clean bullet points and short titles.",
}


@router.get("/status")
def ai_status():
    configured = bool(settings.ai_api_key) or settings.ai_provider == "ollama"
    return {
        "enabled": settings.enable_ai,
        "configured": configured,
        "provider": settings.ai_provider if configured else "none",
    }


@router.post("/{app}/{action}")
async def ai_action(app: str, action: str, body: AIRequest,
                    user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not settings.enable_ai:
        raise HTTPException(503, "AI features are disabled on this server.")

    if app not in SYSTEM_PROMPTS:
        raise HTTPException(400, f"Unknown app: {app}")

    prompt = _build_prompt(app, action, body.context, body.options)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[app]},
        {"role": "user", "content": prompt},
    ]

    try:
        result = await chat(messages, max_tokens=800, temperature=0.7)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"AI request failed: {e}")

    usage = AIUsage(user_id=user.id, app=app, action=action,
                    tokens_in=result.get("tokens_in", 0),
                    tokens_out=result.get("tokens_out", 0))
    db.add(usage); db.commit()

    return {"text": result["text"], "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0)}


def _build_prompt(app: str, action: str, context: str, options: dict) -> str:
    ctx = context[:8000]     # cap
    if app == "word":
        if action == "summarize":   return f"Summarize the following text in 3 sentences:\n\n{ctx}"
        if action == "rewrite":     return f"Rewrite the following text to be clearer and more concise:\n\n{ctx}"
        if action == "expand":      return f"Expand the following text with more detail:\n\n{ctx}"
        if action == "tone":        return f"Rewrite the following text in a {options.get('tone', 'professional')} tone:\n\n{ctx}"
        if action == "fix":         return f"Fix grammar and spelling in the following text. Return only the corrected text:\n\n{ctx}"
        if action == "translate":   return f"Translate the following text to {options.get('to', 'Spanish')}. Return only the translation:\n\n{ctx}"
        if action == "continue":    return f"Continue the following text naturally:\n\n{ctx}"
        if action == "outline":     return f"Create an outline of headings for this topic:\n\n{ctx}"
        if action == "table":       return f"Convert the following text into a markdown table:\n\n{ctx}"
    if app == "sheets":
        if action == "formula":     return f"Write an Excel formula for: {ctx}\nReply with only the formula starting with =."
        if action == "explain":     return f"Explain in plain English what this Excel formula does:\n{ctx}"
        if action == "clean":       return f"Suggest data-cleaning steps for this dataset. Reply as a bulleted list:\n{ctx}"
        if action == "chart":       return f"Recommend a chart type for this data and explain why in 2 sentences:\n{ctx}"
        if action == "insights":    return f"Analyze this data and give 3-5 key insights:\n{ctx}"
    if app == "slides":
        if action == "deck":        return f"Create a slide outline (title + 5-10 bullets per slide) for:\n\n{ctx}"
        if action == "rewrite":     return f"Rewrite these bullet points to be shorter and punchier:\n\n{ctx}"
        if action == "notes":       return f"Write speaker notes for these slides:\n\n{ctx}"
        if action == "theme":       return f"Suggest a theme (colors + font) for a presentation about:\n\n{ctx}"
    return f"Assist with this request: {action}\n\n{ctx}"