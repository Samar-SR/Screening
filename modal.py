from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
import getpass
import os
from datetime import datetime
from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
from typing import  Sequence
def curernt_date_time():
    return datetime.now()


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB4UO0Z405wJR25i-UayneerVCWBAAdH1c"

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


#@tool(description="You are a meeting scheduler")
#def add_event_to_calendar(data: str, name: str) -> str:
#    return f"Your meeting is scheduled for {data}"
#
#
tools = [GenAITool(google_search={})]


def chatting(message):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    instruction = f"""
    You are a intelligent screening bot. You have to have to ask user question and respond accordinglly. 
    User can try to finish screening midway handle it properly. 
    Handle cases when user giving wrong answers multiple time and finish conversation by notifying user.
    Start screening with a interactive message. Below are the details on which you have to generate questions
    job description is {message.job_description } ,  job title is { message.job_title }  
    total questions are { message.total_question }  and generate a summary after the sceening ends at the end"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(model, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=[GenAITool(google_search={})],
        memory=memory,  # Pass the memory to the executor
        verbose=True  # Add verbose to see the agent's thought process
    )

    return agent_executor.invoke({"input": message}, )
