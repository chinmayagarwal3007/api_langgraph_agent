INTENT_PROMPT = """
You are an API assistant.

Conversation so far:
{chat_history}

User input:
{user_input}

Classify intent into one of:
- chat
- api_call
- explain_previous

Return ONLY the intent.
"""
