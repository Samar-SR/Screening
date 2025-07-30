from typing import List, Any
from fastapi import FastAPI
from modal import ScreeningAgent
from schema import Message



app = FastAPI()




@app.post("/chat")
def chat_function(msg: Message):
    data = ScreeningAgent(msg)
    data = data.chat(msg.user_message)
    return data
