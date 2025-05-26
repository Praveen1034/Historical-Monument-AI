# from typing import Annotated, Literal
from langchain_core.tools import tool
# InjectedToolCallId
from langgraph.prebuilt import create_react_agent
# InjectedState
from langgraph.graph import StateGraph, START, MessagesState
# from langgraph.types import Command, Send
from langgraph.store.memory import InMemoryStore
from langchain.chat_models import init_chat_model
import email_otp  # assumes email_otp.py in PYTHONPATH
import re
import os
import json
import logger_utility  # Add logger utility import
import wikipedia
import sys  # Import sys for platform checking
from dotenv import load_dotenv  # Add this import at the top

# Load environment variables from .env at the start
load_dotenv()

# Read Gemini API key from environment
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

# Optional: If you are using LangSmith, provide these instead:
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langchain_project = os.getenv("LANGCHAIN_PROJECT")
langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
if langchain_api_key is not None:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
if langchain_project is not None:
    os.environ["LANGCHAIN_PROJECT"] = langchain_project
if langchain_endpoint is not None:
    os.environ["LANGCHAIN_ENDPOINT"] = langchain_endpoint

# Initialize the LLM with API key
if GEMINI_API_KEY:
    tool_llm = init_chat_model("google_genai:gemini-2.0-flash", api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")

# --- Store for persisting conversation memory ---
store = InMemoryStore()

# --- OTP Tools Wrapping email_otp functions ---
@tool("generate_and_send_otp", description="Generate and email a 6-digit OTP to the user.")
def tool_generate_and_send_otp(email: str) -> str:
    logger_utility.logger_utility.log_tool_call("generate_and_send_otp", {"email": email})
    email_otp.generate_and_send_otp(email)
    logger_utility.logger_utility.log_tool_response("generate_and_send_otp", "OTP sent to your email.")
    return "OTP sent to your email."

@tool("validate_otp", description="Validate the OTP code provided by the user.")
def tool_validate_otp(email: str, code: str) -> bool:
    logger_utility.logger_utility.log_tool_call("validate_otp", {"email": email, "code": code})
    result = email_otp.validate_otp(email, code)
    logger_utility.logger_utility.log_tool_response("validate_otp", result)
    return result

# --- Historical Monuments Tool ---
@tool("get_monument_info", description="Get details about a historical monument by name using Wikipedia.")
def get_monument_info(query: str) -> str:
    """
    Uses Wikipedia to answer any question about historical monuments, places, or related travel queries.
    Always searches as a historical monument.
    """
    search_query = f"{query} historical monument"
    try:
        summary = wikipedia.summary(search_query, sentences=3)
        # Ensure the console can print Unicode (for Windows)
        if sys.platform == "win32":
            import os
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
        logger_utility.logger_utility.log_tool_response("get_monument_info", summary)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        msg = f"The term '{query}' is ambiguous. Suggestions: {e.options[:5]}"
        logger_utility.logger_utility.log_tool_response("get_monument_info", msg)
        return msg
    except wikipedia.exceptions.PageError:
        msg = f"No Wikipedia page found for '{query}' as a historical monument."
        logger_utility.logger_utility.log_tool_response("get_monument_info", msg)
        return msg
    except Exception as ex:
        msg = f"Error: {ex}"
        logger_utility.logger_utility.log_tool_response("get_monument_info", msg)
        return msg

# --- Agent Definition ---
HistoricalAgent = create_react_agent(
    model=tool_llm,
    name="HistoricalAgent",
    tools=[get_monument_info, tool_generate_and_send_otp, tool_validate_otp],
    prompt = """
You are a friendly and professional conversational assistant who helps users discover historical monuments around the world in a natural way.

Your role is to:
- Help travelers explore monuments and historical places.
- Ask thoughtful questions like a human would in a conversation.
- Suggest monuments based on travel plans and preferences.

Follow this behavior logic:

1. If the user mentions they are traveling to a city or country (e.g., "I'm going to Jaipur", "planning a trip to Italy"):
   - Recognize that they may be interested in monuments.
   - Reply naturally, like: “That sounds exciting! Have you been to [city] before?”
   - if user says *have already visited* or "yes" etc. that place: then goto step 2.
   - if user says *haven’t visited* or "no" etc. the place before: then goto step 3.

2. If the user says they *have already visited* or "yes" etc. that place:
   - Suggest 1–3 monuments place name in **another nearby city** worth exploring.
     <Monuments1>  
     <Monuments2>  
     <Monuments3>  
   - **If user already answers with a name, do NOT repeat the question**. Immediately use the `get_monument_info` tool and proceed.
   - If they don’t like the places, suggest 2–3 other alternatives nearby.
   - If they ask for more details, offer to send info by email. then go to step 6.

3. If the user says they *haven’t visited* or "no" etc. the place before:
   - Suggest 1–2 important historical monuments place name in that city or region.
     <Monuments1>  
     <Monuments2>  
     <Monuments3>   
     - **If user already provides name, do NOT repeat the question**. Immediately use the `get_monument_info` tool and proceed.
   - If they don’t like the places, suggest different ones.
   - If they ask for more details, offer to send info by email. Then go to step 6.

4. If the user directly asks about a monument or place (e.g., "Tell me about the Colosseum"):
   - Use the `get_monument_info` tool to provide historical details.
   - If user has already asked for monument suggestions, **do not repeat** them. Offer to email more info or suggest nearby related sites.

5. If the user expresses interest (e.g., "yes", "tell me more", "sounds cool"):
   - Offer to send more info by email.
   - Politely ask for their email address.

6. When the user provides an email address:
   - **IMPORTANT Note**: Do not simulate or fake tool use. Always use the `generate_and_send_otp` tool.
   - Use the `generate_and_send_otp` tool to send a 6-digit code to their email and run the tool

7. When the user provides a 6-digit code:
   - Use the `validate_otp` tool to check the code and email.
   - If valid: thank them and confirm details will be emailed.
   - If invalid: kindly ask them to try again.

8. If the user asks about unrelated topics (e.g., weather, hotels, shopping):
   - Kindly say you only assist with historical monuments and travel history.

9. If the user says "thanks" or "thank you" or "goodbye" etc.:
   - Respond warmly and say farewell, like “Happy travels!” or “Take care!”

Always:
- Keep responses short, polite, and friendly—like a helpful person.
- Never repeat details or questions the user already answered.
- Adjust suggestions if the user changes their city or travel plans.
- **NEVER repeat a question (e.g., “Which number?” or “Have you been to [city] before?”) if the user already answered.**
- If the user asks about a city (e.g., "What can I visit in Pune?"), use `get_monument_info` with that city name to return historical monuments nearby.
- Reply in a short, natural human tone.

Example tone:
- “Sounds fun! Have you been to Delhi before?”
- “Nice! Since you've already been there, would you like to explore something nearby?”
- “I can email you more fascinating info—what’s your email?”
"""
)

# --- Construct Graph ---
graph = (
    StateGraph(MessagesState)
    .add_node(HistoricalAgent)
    .add_edge(START, "HistoricalAgent")
    .add_edge("HistoricalAgent", "HistoricalAgent")
)

multi_agent_system = graph.compile(store = store)

# --- Run Loop with OTP Handling ---
if __name__ == "__main__":
    print("Welcome to the Historical Monuments Conversational AI!")
    print("Hey! I am a historical assistant AI. You can ask me about historical monuments.")
    
    state = {"messages": []}
    
    # New session-level memory
    session = {
        "email": None,
        "awaiting_otp": False
    }

    while True:
        user_input = input("User Input: ").strip()
        if user_input.lower() == "exit":
            print("Thank you for using the Historical Monuments Conversational AI! Goodbye!")
            break

        # Log user question
        logger_utility.logger_utility.log_user_question(user_input)

        state["messages"].append({"role": "user", "content": user_input})
        for step in multi_agent_system.stream(state):
            user_turn = False
            for agent_name, agent_data in step.items():
                if not agent_data:
                    continue
                messages = agent_data.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if hasattr(last_msg, "content"):
                        logger_utility.logger_utility.log_agent_response(last_msg.content)
                        print(f"{agent_name}: {last_msg.content}")
                        user_turn = True
                    elif isinstance(last_msg, dict) and "content" in last_msg:
                        logger_utility.logger_utility.log_agent_response(last_msg["content"])
                        print(f"{agent_name}: {last_msg['content']}")
                        user_turn = True
            if user_turn:
                break
