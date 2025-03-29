from pydantic import BaseModel
from typing import List, Literal

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    # Optional fields can be added here (e.g., temperature, max_tokens)
    # Ensure they are handled in the main.py chat_stream endpoint if added.
    # temperature: Optional[float] = None
    # max_tokens: Optional[int] = None
