import uuid
from typing import AsyncGenerator, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.chat import InvestigationChat
from app.modules.ai.service import LLMService
from app.modules.ai.prompt_manager import PromptManager
from app.modules.ai.context_builder import ContextBuilder

class ChatEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.llm_service = LLMService()
        self.prompt_manager = PromptManager()
        self.context_builder = ContextBuilder(session)

    async def get_history(self, investigation_id: uuid.UUID) -> List[Dict[str, str]]:
        stmt = select(InvestigationChat).where(
            InvestigationChat.investigation_id == investigation_id
        ).order_by(InvestigationChat.created_at.asc())
        
        history = (await self.session.execute(stmt)).scalars().all()
        return [{"role": h.role, "content": h.content} for h in history]

    async def chat_stream(self, investigation_id: uuid.UUID, user_message: str) -> AsyncGenerator[str, None]:
        # Save user message
        user_chat = InvestigationChat(
            id=uuid.uuid4(),
            investigation_id=investigation_id,
            role="user",
            content=user_message
        )
        self.session.add(user_chat)
        await self.session.commit()
        
        # Build context
        context = await self.context_builder.build_context(investigation_id)
        history = await self.get_history(investigation_id)
        
        context["chat_history"] = history
        prompt = self.prompt_manager.render("chat.md.j2", context)
        
        assistant_content = ""
        async for chunk in self.llm_service.chat_stream(prompt):
            assistant_content += chunk
            yield chunk
            
        # Save assistant message
        assistant_chat = InvestigationChat(
            id=uuid.uuid4(),
            investigation_id=investigation_id,
            role="assistant",
            content=assistant_content
        )
        self.session.add(assistant_chat)
        await self.session.commit()
