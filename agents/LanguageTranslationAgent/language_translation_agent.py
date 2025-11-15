from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool


# This is the function that the RefinerAgent will call to exit the loop.
def exit_loop():
    """Call this function ONLY when the critique is 'APPROVED', indicating the translation is finished and no more changes are needed."""
    return {"status": "approved", "message": "Translation approved. Exiting refinement loop."}
print("✅ exit_loop function created.")

# This agent runs ONCE at the beginning to create the first draft.
initial_translation_agent = Agent(
    name="InitialTranslationAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are a professional multilingual translator. Based on users' needed, translate the {news_summary} from english to the language the user ask.
    """,
    output_key="current_translation", # Stores the first draft in the state.
)
print("✅ initial_translation_agent created.")

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
print("✅ critic_agent created.")

# This agent refines the translation based on critique OR calls the exit_loop function.
refiner_agent = Agent(
    name="RefinerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a translation refiner. You have a story draft and critique.
    
    Original new summary: {news_summary}
    Translation Draft: {current_translation}
    Critique: {critique}
    
    Your task is to analyze the critique.
    - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
    - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
    
    output_key="current_translation", # It overwrites the story with the new, refined version.
    tools=[FunctionTool(exit_loop)], # The tool is now correctly initialized with the function reference.
)
print("✅ refiner_agent created.")

# The LoopAgent contains the agents that will run repeatedly: Critic -> Refiner.
translation_refinement_loop = LoopAgent(
    name="TranslationRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2, # Prevents infinite loops
)

# The root agent is a SequentialAgent that defines the overall workflow: Initial Write -> Refinement Loop.
translation_agent = SequentialAgent(
    name="TranslationPipeline",
    sub_agents=[initial_translation_agent, translation_refinement_loop],
)

