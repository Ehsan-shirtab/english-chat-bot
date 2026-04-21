from groq import Groq
from config import GROQ_API_KEY, MODEL, SYSTEM_PROMPT

client = Groq(api_key=GROQ_API_KEY)

# In-memory conversation history per user: { user_id: [ {role, content}, ... ] }
conversation_history: dict[int, list] = {}

def get_history(user_id: int) -> list:
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]

def clear_history(user_id: int):
    conversation_history[user_id] = []

async def ask_groq(prompt: str, user_id: int = None, use_history: bool = True) -> str:
    """
    Send a prompt to Groq. 
    If use_history=True and user_id is given, maintains multi-turn memory.
    """
    try:
        messages = []

        if use_history and user_id is not None:
            history = get_history(user_id)
            history.append({"role": "user", "content": prompt})
            messages = history
        else:
            messages = [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=800
        )

        reply = response.choices[0].message.content

        # Save assistant reply to history
        if use_history and user_id is not None:
            get_history(user_id).append({"role": "assistant", "content": reply})

            # Keep history from growing too large (last 20 messages)
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]

        return reply

    except Exception as e:
        print(f"Groq error: {e}")
        return "⚠️ Oops! My AI brain had a hiccup. Please try again in a second."
