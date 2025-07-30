from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import tool
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from schema import Message, Output



if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB4UO0Z405wJR25i-UayneerVCWBAAdH1c"

if "TAVILY_API_KEY" not in os.environ:
    os.environ["TAVILY_API_KEY"] = "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"

memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

tool = [TavilySearchResults(max_results=3)]

model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )


class ScreeningAgent:
    """
    A class to manage a conversational screening agent, ensuring that
    memory and state are maintained throughout a single conversation.
    """
    def __init__(self, job_details: Message):

        self.model = model
        self.tools = tool
        self.memory = memory


        instruction = f"""
        You are an intelligent screening bot for the position of '{job_details.job_title}'.
        Your goal is to ask the candidate a series of questions based on the job description below.
        You must ask a total of {job_details.total_question} questions.

        - Start the screening with a friendly and interactive welcome message.
        - Ask one question at a time and wait for the user's response.
        - If a user tries to end the screening midway, handle it gracefully.
        - If a user provides nonsensical or clearly wrong answers multiple times, politely end the conversation and notify them.
        - Use the job description to tailor your questions and ensure they are relevant to the position.
        - Maintain a conversational tone and keep the user engaged.
        - Use the provided tools to search for relevant technical questions for the job title.
        - If the user asks for clarification or more information, provide it based on the job description.
        - Give question in proper format and new line, like "Question 1: What is your experience with...?"
        - After all questions have been answered, generate a concise summary of the candidate's responses.
        - Once screening is completed, don't start is again, just say "Screening is completed, Thank you for your time".

        Job Description:
        ---
        {job_details.job_description}
        ---
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", instruction),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])


        agent = create_tool_calling_agent(self.model, self.tools, prompt)


        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
        )

    def chat(self, user_input: str) -> str:
        """
        Invokes the agent with the user's input and returns the response.
        """
        response = self.agent_executor.invoke({"input": user_input})
        return response['output']


