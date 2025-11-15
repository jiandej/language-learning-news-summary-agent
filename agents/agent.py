import asyncio
import os
import sys
import uuid
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.tools import AgentTool
from google.genai import types
from NewsSummaryAgent.news_summary_agent import news_summary_pipeline_agent
from LanguageTranslationAgent.language_translation_agent import translation_agent
from KeyWordAgent.key_word_agent import key_word_agent
from tools import save_userinfo, retrieve_userinfo

GOOGLE_API_KEY = "AIzaSyC1_RlTq1cia4qU-0CqqB4rewk6XMyEK_k"
USER_ID = "guest"
APP_NAME = "Language Learning News Summary Assistant"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY 

# retry setup
retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Define the root agent
root_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="LanguageLearningNewsSummaryRootAgent",
    description="A helpful assistant of language learning for user to provide latest trending news.",
    instruction="""
    You are a language learning assistant that provide latest trending news for user to learn specific languages. When user ask about the learning material:
    
    1. Identify the language user want to learn and the news category the user interested in and use save_userinfo to save the user preferences
    2. If the user doesn't provide preferred language and category, use retrieve_userinfo to find the user preferences, if there is no data, use default category as Celebrity
    3. You must call news_summary_pipeline_agent to get the latest news summary
    4. You must call translation_agent to get the translation of the news summary and get translation
    5. You must call key_word_agent to get the key words showed in the translation.
    6. Respond user by providing:
       a. news summary
       b. translation
       c. key words with meaning in English and example sentence of words
    
    """,
    tools=[
        AgentTool(news_summary_pipeline_agent),
        AgentTool(translation_agent),
        # AgentTool(key_word_agent),
        save_userinfo,
        retrieve_userinfo
        ]
)

async def main():
    sys.stdout.reconfigure(encoding='utf-8')

    # Use DatabaseSessionService for persistent sessions
    db_url = "sqlite:///my_agent_data.db"  # Local SQLite file
    session_service = DatabaseSessionService(db_url=db_url)

    # Create a session with unique session ID
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session_id
    )
    # Create runner for the root agent
    # The runner manages the agent execution and session state
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )

    # user query
    user_query = "I want to learn chinese, give me the political news."
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

# Run the async function using asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())