import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.ai.service import LLMService
from app.modules.ai.prompt_manager import PromptManager
from app.modules.ai.context_builder import ContextBuilder
from app.modules.ai.schemas import (
    AttackAnalysisResult,
    RootCauseAnalysisResult,
    RecommendationsResult,
    ExplanationResult
)

class BaseReasoningModule:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_service = LLMService()
        self.prompt_manager = PromptManager()
        self.context_builder = ContextBuilder(session)

class AttackAnalyzer(BaseReasoningModule):
    async def analyze(self, investigation_id: uuid.UUID) -> AttackAnalysisResult:
        context = await self.context_builder.build_context(investigation_id)
        prompt = self.prompt_manager.render("attack_analysis.md.j2", context)
        return await self.llm_service.analyze_structured(prompt, AttackAnalysisResult)  # type: ignore

class RootCauseAnalyzer(BaseReasoningModule):
    async def analyze(self, investigation_id: uuid.UUID) -> RootCauseAnalysisResult:
        context = await self.context_builder.build_context(investigation_id)
        # Assuming we have a root_cause_analysis.md.j2 template (reusing attack_analysis here for demo purposes if not created)
        # Let's assume it exists or we use a hardcoded one for now
        prompt = self.prompt_manager.render("root_cause_analysis.md.j2", context)
        return await self.llm_service.analyze_structured(prompt, RootCauseAnalysisResult)  # type: ignore

class ContainmentPlanner(BaseReasoningModule):
    async def plan(self, investigation_id: uuid.UUID) -> RecommendationsResult:
        context = await self.context_builder.build_context(investigation_id)
        prompt = self.prompt_manager.render("recommendations.md.j2", context)
        return await self.llm_service.analyze_structured(prompt, RecommendationsResult)  # type: ignore

class RemediationPlanner(BaseReasoningModule):
    async def plan(self, investigation_id: uuid.UUID) -> RecommendationsResult:
        context = await self.context_builder.build_context(investigation_id)
        prompt = self.prompt_manager.render("recommendations.md.j2", context)
        return await self.llm_service.analyze_structured(prompt, RecommendationsResult)  # type: ignore

class EvidenceExplainer(BaseReasoningModule):
    async def explain(self, investigation_id: uuid.UUID, evidence_id: uuid.UUID) -> ExplanationResult:
        context = await self.context_builder.build_context(investigation_id)
        context["target_evidence_id"] = str(evidence_id)
        # Using a generic explanation prompt
        prompt = self.prompt_manager.render("explain.md.j2", context)
        return await self.llm_service.analyze_structured(prompt, ExplanationResult)  # type: ignore
