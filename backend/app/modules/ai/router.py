import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

from app.modules.ai.reasoning import AttackAnalyzer, EvidenceExplainer, ContainmentPlanner
from app.modules.ai.chat import ChatEngine
from app.modules.ai.report import ReportGenerator
from app.modules.ai.schemas import (
    AttackAnalysisResult,
    RecommendationsResult,
    ExplanationResult
)

router = APIRouter(prefix="/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str

@router.post("/analyze", response_model=AttackAnalysisResult)
async def analyze_attack(
    investigation_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analyzer = AttackAnalyzer(db)
    return await analyzer.analyze(investigation_id)

@router.post("/chat")
async def chat(
    investigation_id: uuid.UUID = Query(...),
    request: ChatRequest = ...,  # type: ignore
    stream: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    engine = ChatEngine(db)
    if stream:
        return StreamingResponse(engine.chat_stream(investigation_id, request.message), media_type="text/event-stream")
    else:
        # For non-streaming, collect all chunks
        content = ""
        async for chunk in engine.chat_stream(investigation_id, request.message):
            content += chunk
        return {"role": "assistant", "content": content}

@router.get("/report")
async def get_report(
    investigation_id: uuid.UUID = Query(...),
    format: str = Query("markdown"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    generator = ReportGenerator(db)
    report_data = await generator.generate_technical_report(investigation_id)
    if format == "json":
        return report_data
    return PlainTextResponse(generator.render_markdown(report_data))

@router.get("/explain", response_model=ExplanationResult)
async def explain_evidence(
    investigation_id: uuid.UUID = Query(...),
    evidence_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    explainer = EvidenceExplainer(db)
    return await explainer.explain(investigation_id, evidence_id)

@router.get("/recommend", response_model=RecommendationsResult)
async def recommend_actions(
    investigation_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    planner = ContainmentPlanner(db)
    return await planner.plan(investigation_id)
