from google.adk.agents import Agent
import vertexai
import os
from agents.agent import language_learning_news_summary_agent


vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

root_agent = language_learning_news_summary_agent