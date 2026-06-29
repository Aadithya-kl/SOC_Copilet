import uuid
import redis.asyncio as redis
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.modules.investigation.pipeline import InvestigationPipeline

engine = create_async_engine(str(settings.DATABASE_URL))
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def run_investigation(ctx, investigation_id: uuid.UUID):
    async with async_session() as session:
        pipeline = InvestigationPipeline(session, ctx['redis_client'])
        await pipeline.run(investigation_id)

async def startup(ctx):
    ctx['redis_client'] = redis.Redis.from_url(settings.REDIS_URL)
    ctx['db_engine'] = engine

async def shutdown(ctx):
    await ctx['redis_client'].close()
    await ctx['db_engine'].dispose()

class WorkerSettings:
    functions = [run_investigation]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown

