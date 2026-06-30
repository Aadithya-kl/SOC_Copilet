import uuid
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.service import LLMService
from app.modules.ai.prompt_manager import PromptManager
from app.modules.ai.context_builder import ContextBuilder

class ReportSection(BaseModel):
    title: str
    content: str

class TechnicalReport(BaseModel):
    summary: str = Field(..., description="High-level summary of the incident")
    attack_vector: str = Field(..., description="Detailed description of initial access and attack chain")
    impact: str = Field(..., description="Impact of the attack")
    mitre_techniques: List[str] = Field(..., description="List of observed MITRE techniques")
    recommendations: List[str] = Field(..., description="Actionable recommendations")

class ReportGenerator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_service = LLMService()
        self.prompt_manager = PromptManager()
        self.context_builder = ContextBuilder(session)

    async def generate_technical_report(self, investigation_id: uuid.UUID) -> TechnicalReport:
        context = await self.context_builder.build_context(investigation_id)
        prompt = self.prompt_manager.render("technical_report.md.j2", context)
        
        # Generates structured intermediate object
        report_data = await self.llm_service.analyze_structured(prompt, TechnicalReport)
        return report_data  # type: ignore
        
    def render_markdown(self, report: TechnicalReport) -> str:
        md = "# Technical Incident Report\n\n"
        md += f"## Executive Summary\n{report.summary}\n\n"
        md += f"## Attack Vector & Chain\n{report.attack_vector}\n\n"
        md += f"## Impact\n{report.impact}\n\n"
        md += "## MITRE ATT&CK Techniques\n"
        for tech in report.mitre_techniques:
            md += f"- {tech}\n"
        md += "\n## Recommendations\n"
        for rec in report.recommendations:
            md += f"- {rec}\n"
            
        return md
