"""Solver, Analysis ToolPak, Power Query."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
from ..auth import get_current_user
from ..models import User
from ..services import solver as solver_svc
from ..services import stats_tools
from ..services import query_engine

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


class SolverIn(BaseModel):
    method: str = "simplex"
    objective: dict
    variables: list[dict] = []
    constraints: list[dict] = []


@router.post("/solver")
def run_solver(body: SolverIn, user: User = Depends(get_current_user)):
    return solver_svc.solve(body.model_dump())


class StatsIn(BaseModel):
    tool: str
    params: dict[str, Any] = {}


@router.post("/toolpak")
def run_toolpak(body: StatsIn, user: User = Depends(get_current_user)):
    return stats_tools.run(body.tool, body.params)


class QueryIn(BaseModel):
    table: list[dict]
    steps: list[dict]


@router.post("/query")
def run_query(body: QueryIn, user: User = Depends(get_current_user)):
    try:
        return {"rows": query_engine.run_query(body.table, body.steps)}
    except Exception as e:
        raise HTTPException(400, str(e))