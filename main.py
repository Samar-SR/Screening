from typing import List, Any

from fastapi import FastAPI
from modal import chatting
from pydantic import BaseModel

app = FastAPI()


class Message(BaseModel):
    job_description: str
    job_title: str
    total_question: int = 4


class Output(BaseModel):
    response: str


@app.post("/chat")
def chat_function(msg: Message):
    data = chatting(msg)
    data = Output(**data)
    return data
