import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from passlib.hash import argon2

from app.core.config import settings
from app.models.organization import Organization
from app.models.user import User

async def seed():
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Check if System org exists
        from sqlalchemy import select
        org = await session.execute(select(Organization).where(Organization.slug == "system"))
        org = org.scalar_one_or_none()
        
        if not org:
            org = Organization(
                name="System Organization",
                slug="system"
            )
            session.add(org)
            await session.commit()
            print("Created System Organization")
        
        # Check if Super Admin exists
        admin = await session.execute(select(User).where(User.email == "admin@soc-copilot.local"))
        admin = admin.scalar_one_or_none()
        
        if not admin:
            password_hash = argon2.hash("SuperSecretAdminPassword123!")
            admin = User(
                organization_id=org.id,
                email="admin@soc-copilot.local",
                username="admin",
                password_hash=password_hash,
                role="super_admin",
                display_name="Super Admin"
            )
            session.add(admin)
            await session.commit()
            print("Created Super Admin user")
        else:
            print("Super Admin already exists")

if __name__ == "__main__":
    asyncio.run(seed())
