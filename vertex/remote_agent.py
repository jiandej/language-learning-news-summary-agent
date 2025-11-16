import os
import sys
import asyncio
import vertexai
from vertexai import agent_engines

USER_ID = "guest"
APP_NAME = "Language Learning News Summary Assistant"

# Initialize Vertex AI
vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=sys.argv[1])

# Get the most recently deployed agent
agents_list = list(agent_engines.list())
if agents_list:
    remote_agent = agents_list[0]  # Get the first (most recent) agent
    client = agent_engines
    print(f"✅ Connected to deployed agent: {remote_agent.resource_name}")
else:
    print("❌ No agents found. Please deploy first.")




# Helper function for send user prompt to agent and display user query and agent response properly
async def conversation(user_query: str, remote_agent):
    # Display query
    print(f"\n👤 User: {user_query}")
    print(f"\n🤖 Agent:")
    print("-" * 60)

    async for item in remote_agent.async_stream_query(
        message=user_query,
        user_id=USER_ID,
    ):
        if 'content' in item and 'parts' in item['content'] and len(item['content']['parts']) != 0:
            print(item['content']['parts'][0]['text'])
    print("-" * 60)

async def main():
    sys.stdout.reconfigure(encoding='utf-8')
    while True:
        # user query
        user_query = input("Prompt: ")
        # Check if user wants to exit
        if user_query.lower() == 'exit':
            print("Goodbye!")
            break
        
        await conversation(user_query=user_query, remote_agent=remote_agent)

# Run the async function using asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())