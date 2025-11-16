from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import google_search, FunctionTool

# This is the function that the RefinerAgent will call to exit the loop.
def exit_loop():
    """Call this function ONLY when the critique is 'APPROVED', indicating the translation is finished and no more changes are needed."""
    return {"status": "approved", "message": "Translation approved. Exiting refinement loop."}

# News Research Agent: Its job is to use the google_search tool to find the trending news
news_research_agent = Agent(
    name="NewsResearchAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a specialized news research agent. Your only job is to use the
    google_search tool to find one latest trending english news based on the category user interested,
    don't use the language user want to learn for search.
    Output the news title and content
    """,
    tools=[google_search],
    output_key="news_data", # The result of this agent will be stored in the session state with this key.
)

# News Summarizer Agent: Its job is to summarize the text it receives.
news_summarizer_agent = Agent(
    name="NewsSummarizerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a specialized news summarizer. 
    Read the provided news: {news_data} and create a concise summary between 100 to 300 words and keeps the title with format as:
    Title: <title>
    Summary: <Summary>
    """,
    output_key="news_summary",
)

# This agent runs ONCE at the beginning to create the first draft.
initial_translation_agent = Agent(
    name="InitialTranslationAgent",
    model="gemini-2.5-flash-lite",
    instruction="""
    You are a professional multilingual translator. Based on users' needed, translate the {news_summary} from english to the language the user ask.
    """,
    output_key="current_translation", # Stores the first draft in the state.
)

# This agent's only job is to provide feedback or the approval signal. It has no tools.
critic_agent = Agent(
    name="CriticAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a constructive translation critic. Review the translation provided below.
    Translation: {current_translation}
    
    Evaluate the translation quality, including the syntax and semitic.
    - If the translation is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
    - Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
    output_key="critique", # Stores the feedback in the state.
)

# This agent refines the translation based on critique OR calls the exit_loop function.
refiner_agent = Agent(
    name="RefinerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a translation refiner. You have a story draft and critique.
    
    Original new summary: {news_summary}
    Translation Draft: {current_translation}
    Critique: {critique}
    
    Your task is to analyze the critique.
    - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and output exactly same as {current_translation}.
    - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
    
    output_key="current_translation", # It overwrites the story with the new, refined version.
    tools=[FunctionTool(exit_loop)], # The tool is now correctly initialized with the function reference.
)

# The LoopAgent contains the agents that will run repeatedly: Critic -> Refiner.
translation_refinement_loop = LoopAgent(
    name="TranslationRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2, # Prevents infinite loops
)

key_word_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="KeyWordAgent",
    instruction="""
    You are a multilingual textbook writer, find 5 words in summary of translation for learning and give a sentence as example. The standard on how to find the words as following:
    1. Filter out people's name, ex: John, Trump and Obama
    2. Filter out stop words, ex: the, a and of
    3. Filter out biased or rude word, ex: pussy
    4. Filter out pronoun, ex: I, she and him

    1. The word and example sentence are written as the language user want to learn
    2. The meaning is written as English

    Respond format as:
    1. <word> : <meaning>
    Example: <example sentence>

    2. <word> : <meaning>
    Example: <example sentence>
    """,
    output_key="keywords"
)

output_agent = Agent(
    name="OutputAgent",
    model="gemini-2.5-flash",
    instruction="""
    You must keep the  {news_summary}, {current_translation} and {keywords} in response:
    Return {news_summary}, {current_translation} and {keywords} with format:
    News Summary:
    {news_summary}

    Translation with <Language user enter>
    {current_translation}
    Keywords:
    {keywords}
    """,
)


# News Research -> News Summarizer -> News Translation -> Translation refine loop
new_summary_and_translation_agent = SequentialAgent(
    name="TranslationPipeline",
    sub_agents=[
        news_research_agent,
        news_summarizer_agent,
        initial_translation_agent,
        translation_refinement_loop,
        key_word_agent,
        output_agent],
)