from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PubSubMessageSchema(BaseModel):
    short_code: str
    original_url: str
    timestamp: datetime
    action_type: str
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)