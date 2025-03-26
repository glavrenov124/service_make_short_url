from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app import schemas, crud, models
import uvicorn
from app.redis_client import redis
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from app.database import get_db

from app.auth import get_current_user, hash_password, create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm

import os
import subprocess
import time
from dotenv import load_dotenv


app = FastAPI()

@app.post("/register", response_model=schemas.UserOut)
async def register(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = models.User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}



@app.delete("/links/cleanup")
async def cleanup_expired_links(db: AsyncSession = Depends(get_db)):
    count = await crud.delete_expired_links(db)
    return {"detail": f"{count} expired links deleted"}

@app.post("/links/shorten", response_model=schemas.LinkOut)
async def shorten_link(
    link: schemas.LinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  
):
    try:
        db_link = await crud.create_short_link(db, link, owner_id=current_user.id)  
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_link


@app.get("/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    cached_url = await redis.get(short_code)
    if cached_url:
        link = await crud.get_link_by_code(db, short_code)
        if link:
            await crud.update_link_stats(db, link)
        return RedirectResponse(url=cached_url)

    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Link expired")

    await redis.set(short_code, link.original_url)
    await crud.update_link_stats(db, link)
    return RedirectResponse(url=link.original_url)


@app.get("/links/{short_code}/stats", response_model=schemas.LinkStats)
async def get_link_statistics(short_code: str, db: AsyncSession = Depends(get_db)):
    link = await crud.get_link_stats(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@app.delete("/links/{short_code}")
async def delete_link(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this link")

    await crud.delete_link(db, link)
    return {"message": "Link deleted successfully"}


@app.put("/links/{short_code}")
async def update_link(short_code: str, link_in: schemas.LinkCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    link = await crud.get_link_by_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your link")
    
    updated = await crud.update_original_url(db, short_code, str(link_in.original_url))
    await redis.delete(short_code)
    return updated

@app.get("/links/search", response_model=List[schemas.LinkOut])
async def search_link(original_url: str, db: AsyncSession = Depends(get_db)):
    links = await crud.search_by_original_url(db, original_url)
    if not links:
        raise HTTPException(status_code=404, detail="Links not found")
    return links

@app.get("/links/expired", response_model=List[schemas.LinkOut])
async def get_expired_links(db: AsyncSession = Depends(get_db)):
    return await crud.get_expired_links(db)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)