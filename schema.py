from pydantic import BaseModel,Field
from typing import Optional

class Message(BaseModel):
    job_description: str
    job_title: str
    total_question: int = 4
    user_message: str = Field(default="Start the screening", description="User's input message to the AI agent")


class Output(BaseModel):
    response: str