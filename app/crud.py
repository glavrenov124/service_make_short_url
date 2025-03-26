import random
import string
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timedelta
from app import models, schemas
from typing import List
from app.redis_client import redis
from sqlalchemy.exc import SQLAlchemyError

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_short_link(db: AsyncSession, link_in: schemas.LinkCreate, owner_id: int) -> models.Link:
    if link_in.custom_alias:
        result = await db.execute(
            select(models.Link).where(models.Link.custom_alias == link_in.custom_alias)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Custom alias already taken")
        short_code = link_in.custom_alias
    else:
        while True:
            short_code = generate_short_code()
            result = await db.execute(
                select(models.Link).where(models.Link.short_code == short_code)
            )
            if not result.scalar_one_or_none():
                break

    original_url_str = str(link_in.original_url)

    expires_at = link_in.expires_at if link_in.expires_at else datetime.utcnow() + timedelta(days=30)  

    db_link = models.Link(
        original_url=original_url_str,
        short_code=short_code,
        custom_alias=link_in.custom_alias,
        owner_id=owner_id,
        expires_at=expires_at, 
    )

    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link


async def get_link_by_code(db: AsyncSession, short_code: str) -> Optional[models.Link]:
    result = await db.execute(
        select(models.Link).where(
            or_(
                models.Link.short_code == short_code,
                models.Link.custom_alias == short_code
            )
        )
    )
    return result.scalar_one_or_none()

async def update_link_stats(db: AsyncSession, link: models.Link):
    link.access_count += 1
    link.last_accessed = datetime.utcnow()
    await db.commit()

async def get_link_stats(db: AsyncSession, short_code: str) -> Optional[models.Link]:
    result = await db.execute(
        select(models.Link).where(
            or_(
                models.Link.short_code == short_code,
                models.Link.custom_alias == short_code
            )
        )
    )
    return result.scalar_one_or_none()

async def delete_link(db: AsyncSession, short_code: str) -> bool:
    try:
        result = await db.execute(
            select(models.Link).where(
                or_(
                    models.Link.short_code == short_code,
                    models.Link.custom_alias == short_code
                )
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await db.delete(link)
            await db.commit()
            return True
        return False
    except SQLAlchemyError:
        await db.rollback()
        return False

async def update_original_url(db: AsyncSession, short_code: str, new_url: str) -> Optional[models.Link]:
    result = await db.execute(
        select(models.Link).where(
            or_(
                models.Link.short_code == short_code,
                models.Link.custom_alias == short_code
            )
        )
    )
    link = result.scalar_one_or_none()
    if link:
        link.original_url = new_url
        await db.commit()
        await db.refresh(link)
        return link
    return None

async def search_by_original_url(db: AsyncSession, original_url: str) -> List[models.Link]:
    result = await db.execute(
        select(models.Link).where(models.Link.original_url == original_url)
    )
    return result.scalars().all()

async def get_expired_links(db: AsyncSession) -> List[models.Link]:
    now = datetime.utcnow()
    result = await db.execute(
        select(models.Link).where(models.Link.expires_at != None, models.Link.expires_at < now)
    )
    return result.scalars().all()

async def delete_expired_links(db: AsyncSession) -> int:
    now = datetime.utcnow()
    result = await db.execute(
        select(models.Link).where(models.Link.expires_at != None, models.Link.expires_at < now)
    )
    expired_links = result.scalars().all()
    count = 0

    for link in expired_links:
        await redis.delete(link.short_code) 
        await db.delete(link)
        count += 1

    await db.commit()
    return count