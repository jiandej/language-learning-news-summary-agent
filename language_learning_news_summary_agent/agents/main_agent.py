from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types
from .tools import save_userinfo, retrieve_userinfo
from .news_summary_agent import new_summary_and_translation_agent

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
    3. You must follow the followling steps (4)(5)(6) to complete the user request:
    4. If the user doesn't provide preferred language and category, use retrieve_userinfo to find the user preferences,
       if there is no data, use Celebrity as news category as Celebrity and chinese as language 
    5. You must call new_summary_and_translation_agent to get the latest news summary of that category and its translation
    6. Respond to user the title and news summary, its translation and the keywords with examples propoerly
    """,
    tools=[
        AgentTool(new_summary_and_translation_agent),
        save_userinfo,
        retrieve_userinfo
   ]
)