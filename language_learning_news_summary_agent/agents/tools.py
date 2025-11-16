from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

# Define scope levels for state keys (following best practices)
USER_NAME_SCOPE_LEVELS = ("temp", "user", "app")


# This demonstrates how tools can write to session state using tool_context.
# The 'user:' prefix indicates this is user-specific data.
def save_userinfo(
    tool_context: ToolContext, user_name: str, preferredLanguage: str, interestedNewsCategory: str
) -> Dict[str, Any]:
    """
    Tool to record and save user name and country in session state.

    Args:
        user_name: The username to store in session state
        country: The name of the user's country
    """
    # Write to session state using the 'user:' prefix for user data
    tool_context.state["user:name"] = user_name
    tool_context.state["user:preferredLanguage"] = preferredLanguage
    tool_context.state["user:interestedNewsCategory"] = interestedNewsCategory


    return {"status": "success"}


# This demonstrates how tools can read from session state.
def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Tool to retrieve user name and country from session state.
    """
    # Read from session state
    user_name = tool_context.state.get("user:name", "Username not found")
    preferredLanguage = tool_context.state.get("user:preferredLanguage", "preferredLanguage not found")
    interestedNewsCategory = tool_context.state.get("user:interestedNewsCategory", "interestedNewsCategory not found")

    return {
        "status": "success",
        "user_name": user_name,
        "preferredLanguage": preferredLanguage,
        "interestedNewsCategory": interestedNewsCategory
        }