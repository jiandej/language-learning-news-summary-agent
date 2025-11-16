import asyncio
import sys
import os
import uuid
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from google.adk.runners import Runner

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from language_learning_news_summary_agent.agents import main_agent

USER_ID = "guest"
APP_NAME = "Language Learning News Summary Assistant"

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
        agent=main_agent.language_learning_news_summary_agent, app_name=APP_NAME, session_service=session_service
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