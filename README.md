# Historical Monuments Conversational AI

A conversational AI assistant that helps users discover and learn about historical monuments around the world. The assistant interacts in a natural, friendly way, suggests monuments based on travel plans, and can send additional information via email with OTP-based verification. The app features a modern chat UI built with Streamlit.

This project is deployed on Streamlit: [https://historical-monument-ai-gnwdgysvzjooxekwwh3ntn.streamlit.app/](https://historical-monument-ai-gnwdgysvzjooxekwwh3ntn.streamlit.app/)

## Features
- **Conversational AI**: Natural, context-aware dialogue about historical monuments and travel plans.
- **Monument Information**: Fetches details about monuments using Wikipedia.
- **Personalized Suggestions**: Recommends monuments based on user travel interests.
- **Email Integration**: Sends additional information to users via email after OTP verification.
- **OTP Verification**: Secure email delivery using one-time password (OTP) authentication.
- **Logging**: All interactions and tool calls are logged for traceability.
- **Modern UI**: WhatsApp-style chat interface using Streamlit.

## Project Structure
- `streamlit_app.py`: Streamlit web app with chat UI.
- `Agent.py`: Main conversational agent logic, tool integrations, and dialogue flow.
- `email_otp.py`: Email sending and OTP generation/validation utilities.
- `logger_utility.py`: Logging utility for user questions, tool calls, and responses.
- `requirements.txt`: Python dependencies.
- `log/`: Log files for each run.
- `.env`: Environment variables (email credentials, API keys, etc.).

## Setup Instructions

### 1. Clone the Repository
```powershell
git clone <repo-url>
cd "Conversational AI Demo"
```

### 2. Install Dependencies
It is recommended to use a virtual environment.
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following (see sample below):
```
USER_EMAIL=your_email@gmail.com
USER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
GEMINI_API_KEY=your_gemini_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
```
- For Gmail, you may need to generate an [App Password](https://support.google.com/accounts/answer/185833?hl=en).
- Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 4. Run the Streamlit App
```powershell
streamlit run streamlit_app.py
```
The app will open in your browser. Start chatting about historical monuments!

### 5. (Optional) Run the Agent in Console
```powershell
python Agent.py
```

## Usage
- Ask about monuments, e.g., "Tell me about the Colosseum" or "I'm planning a trip to Jaipur".
- The assistant will suggest monuments and can send more info to your email after OTP verification.
- All chat and tool interactions are logged in the `log/` directory.

## Security Notes
- **Never share your `.env` file or credentials.**
- OTPs are stored in memory and expire after 5 minutes.

## Dependencies
- Streamlit
- langchain, langgraph, langsmith
- google-generativeai
- wikipedia
- python-dotenv
- smtplib, imaplib

See `requirements.txt` for the full list.

## License
MIT License (add your license here)

## Acknowledgments
- [LangChain](https://github.com/langchain-ai/langchain)
- [Google Generative AI](https://ai.google/discover/gemini/)
- [Wikipedia API](https://pypi.org/project/wikipedia/)

---
*Happy travels and monument discoveries!*
