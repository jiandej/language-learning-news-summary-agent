from google.adk.agents import Agent
from google.adk.tools import google_search

key_word_agent = Agent(
    model="gemini-2.5-flash",
    name="KeyWordAgent",
    instruction="""
    You are a multilingual textbook writer, find the words in translation for learning and give a sentence as example. The standard on how to find the words as following:
    1. Filter out people's name, ex: John, Trump and Obama
    2. Filter out stop words, ex: the, a and of
    3. Filter out biased or rude word, ex: pussy
    4. Filter out pronoun, ex: I, she and him

    Find 1-3 words in translation

    Respond format as:
    1. <word> : <meaning>
    Example: <example sentence>

    2. <word> : <meaning>
    Example: <example sentence>
    """,

)