"""Slides-specific endpoints."""
from fastapi import APIRouter
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..auth import get_current_user
from ..models import User
router = APIRouter(prefix="/api/slides", tags=["slides"])


@router.get("/health")
def health():
    return {"ok": True}
    
class PresenterCoachIn(BaseModel):
    transcript: str
    durationSec: float
    slideCount: int


@router.post("/presenter-coach")
def presenter_coach(body: PresenterCoachIn, user: User = Depends(get_current_user)):
    """Analyze a rehearsal transcript: pace, filler words, repeated words."""
    import re
    words = re.findall(r"\b[\w']+\b", body.transcript.lower())
    total = len(words)
    wpm = (total / body.durationSec) * 60 if body.durationSec > 0 else 0
    fillers = ["um", "uh", "like", "you know", "so", "basically", "actually"]
    filler_count = {f: body.transcript.lower().count(f) for f in fillers}
    repeated = {}
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            repeated[words[i]] = repeated.get(words[i], 0) + 1
    return {
        "words": total,
        "wordsPerMinute": round(wpm, 1),
        "durationMin": round(body.durationSec / 60, 2),
        "fillers": {k: v for k, v in filler_count.items() if v},
        "repeatedAdjacent": repeated,
        "paceAssessment": (
            "slow" if wpm < 110 else
            "good" if 110 <= wpm <= 160 else
            "fast"
        ),
        "recommendations": _coach_recommendations(wpm, filler_count, repeated),
    }


def _coach_recommendations(wpm, fillers, repeated):
    rec = []
    if wpm < 110:
        rec.append("Speak a bit faster — aim for 120–150 words per minute.")
    elif wpm > 160:
        rec.append("Slow down — try pausing between key points.")
    if sum(fillers.values()) > 5:
        rec.append("Reduce filler words; try a one-second pause instead.")
    if repeated:
        rec.append("You're repeating words; try pausing or rephrasing.")
    return rec