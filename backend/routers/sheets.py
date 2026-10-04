"""Sheets-specific endpoints — formula oracle, server-side evaluate (parity tests)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..auth import get_current_user
from ..models import User

router = APIRouter(prefix="/api/sheets", tags=["sheets"])


class CellVal(BaseModel):
    v: object | None = None
    f: str | None = None


class EvalIn(BaseModel):
    formulas: dict[str, str]        # ref -> "=..." (no leading = required)
    cells: dict[str, CellVal] = {}  # other cells available for reference


@router.post("/evaluate")
def evaluate(body: EvalIn, user: User = Depends(get_current_user)):
    """
    Server-side evaluator. Uses the *same* semantics as the JS engine for
    cross-checking in CI. Returns a map of ref -> computed value.
    """
    try:
        from ..services.formula_py import evaluate_formulas
    except Exception as e:
        raise HTTPException(500, f"Server evaluator unavailable: {e}")

    cells = {k: (v.model_dump(exclude_none=True)) for k, v in body.cells.items()}
    try:
        result = evaluate_formulas(body.formulas, cells)
    except Exception as e:
        raise HTTPException(400, f"Evaluation error: {e}")
    return {"values": result}