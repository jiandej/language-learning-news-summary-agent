import os
import sys
import asyncio
import vertexai
from vertexai import agent_engines

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

agent_engines.delete(resource_name=remote_agent.resource_name, force=True)
print("✅ Agent successfully deleted")