import asyncio
import sys
import os
import uuid
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from google.adk.runners import Runner
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types
from tools import save_userinfo, retrieve_userinfo
from news_summary_agent import new_summary_and_translation_agent

USER_ID = "guest"
APP_NAME = "Language Learning News Summary Assistant"

# retry setup
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Define the root agent
language_learning_news_summary_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="LanguageLearningNewsSummaryRootAgent",
    instruction="""
    You are a helpful language learning assistant that provide latest trending news in the world for user to learn specific languages by providing:
     - title and news summary, title and new summary translation, and the keywords with examples to learn.

    Following the steps to generate the learning material for user:
    1. If the user doesn't ask for learning language,respond to say I'm a language learning assisant. please tell me which language you would like to learn:
    2. Identify the language user want to learn and the news category the user interested in and use save_userinfo to save the user preferences.
    3. If the user doesn't provide preferred language and category, use retrieve_userinfo to find the user preferences,
       if there is no data, use Celebrity as news category as Celebrity and chinese as language 
    4. You must call new_summary_and_translation_agent to get the latest news summary of that category and its translation
    5. Response for user must having followings sections:
       a. news summary with titile
       b. news summary translation
       c. the keywords with examples propoerly
    """,
    tools=[
        AgentTool(new_summary_and_translation_agent),
        save_userinfo,
        retrieve_userinfo
   ]
)

# Helper function for send user prompt to agent and display user query and agent response properly
async def conversation(user_query: str, runner: Runner, session_id: str):
    user_content = types.Content(parts=[types.Part(text=user_query)])

    # Display query
    print(f"\n👤 User: {user_query}")
    print(f"\n🤖 Agent:")
    print("-" * 60)

    # Run the agent asynchronously
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=user_content
    ):
        # Print final response only (skip intermediate events)
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(part.text)
    print("-" * 60)

async def main():
    sys.stdout.reconfigure(encoding='utf-8')

    # Use DatabaseSessionService for persistent sessions
    db_url = "sqlite:///language_learning_new_summary_agent_data.db"  # Local SQLite file
    session_service = DatabaseSessionService(db_url=db_url)

    # Create a session with unique session ID
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )

    # Create runner for the root agent
    # The runner manages the agent execution and session state
    runner = Runner(
        agent=language_learning_news_summary_agent, app_name=APP_NAME, session_service=session_service
    )

    while True:
        # user query
        user_query = input("Prompt: ")
        # Check if user wants to exit
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        
        await conversation(
            user_query=user_query,
            runner=runner,
            session_id=session_id)

# Run the async function using asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())