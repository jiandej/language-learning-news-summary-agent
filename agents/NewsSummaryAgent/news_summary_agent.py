from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search

# News Research Agent: Its job is to use the google_search tool to find the trending news
news_research_agent = Agent(
    name="NewsResearchAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a specialized news research agent. Your only job is to use the
    google_search tool to find one latest trending english news based on the category user interested
    """,
    tools=[google_search],
    output_key="news_data", # The result of this agent will be stored in the session state with this key.
)
print("✅ research_agent created.")

# News Summarizer Agent: Its job is to summarize the text it receives.
news_summarizer_agent = Agent(
    name="NewsSummarizerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a specialized news summarizer. 
    Read the provided news: {news_data} and create a concise summary within 200 words""",
    output_key="news_summary",
)
print("✅ summarizer_agent created.")

news_summary_pipeline_agent = SequentialAgent(
    name="NewsPipelineAgent",
    sub_agents=[news_research_agent, news_summarizer_agent],
)