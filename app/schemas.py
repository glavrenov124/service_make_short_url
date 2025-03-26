from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime, timedelta

class LinkBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkOut(BaseModel):
    short_code: str
    original_url: str
    custom_alias: Optional[str]
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class LinkStats(BaseModel):
    original_url: HttpUrl
    short_code: str
    custom_alias: Optional[str]
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: Optional[datetime]

    class Config:
        from_attributes = True

class LinkUpdate(BaseModel):
    original_url: HttpUrl

class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = Field(
        default=None,
        example=(datetime.utcnow() + timedelta(days=1)).replace(microsecond=0).isoformat()
    )

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str