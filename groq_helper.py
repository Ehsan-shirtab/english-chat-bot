import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are Aria — a warm, funny Canadian friend who also happens to be 
a great English teacher.

Your friend is an intermediate English learner from Iran living in 
Victoria, Canada.

Your personality:
- You are genuinely curious about their life and remember details they share
- You react like a real friend — with warmth, humour, and interest
- You correct their English gently, like a friend would, never like a teacher
- You make corrections feel helpful not embarrassing
- You use simple natural English at B1/B2 level
- You use emojis naturally but not too many

Golden rule: Friend first, teacher second. Always.
"""

client = Groq(api_key=GROQ_API_KEY)

conversation_history: dict[int, list] = {}
user_mode: dict[int, str] = {}
user_memory: dict[int, list] = {}


def get_mode(user_id: int) -> str:
    return user_mode.get(user_id, "correct")


def set_mode(user_id: int, mode: str):
    user_mode[user_id] = mode


def get_history(user_id: int) -> list:
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]


def clear_history(user_id: int):
    conversation_history[user_id] = []
    user_memory[user_id] = []


def get_memory(user_id: int) -> list:
    return user_memory.get(user_id, [])


def add_memory(user_id: int, fact: str):
    if user_id not in user_memory:
        user_memory[user_id] = []
    if fact not in user_memory[user_id]:
        user_memory[user_id].append(fact)
    if len(user_memory[user_id]) > 30:
        user_memory[user_id] = user_memory[user_id][-30:]


def build_memory_context(user_id: int) -> str:
    memory = get_memory(user_id)
    if not memory:
        return ""
    facts = "\n".join(f"- {f}" for f in memory)
    return f"\nWhat you already know about this person:\n{facts}\n"


def _extract_memory(user_message: str, user_id: int):
    try:
        extract_prompt = f"""Read this message and extract any personal facts about the person.
Only extract clear facts like name, job, city, hobby, family, nationality, age, goals.
If there are no clear personal facts reply with exactly: NONE

Message: "{user_message}"

Reply with one fact per line, very short, like:
- Lives in Victoria BC
- Works as a nurse
- Has a daughter

Reply NONE if no personal facts found."""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": extract_prompt}],
            max_tokens=100
        )
        result = response.choices[0].message.content.strip()

        if result and result.upper() != "NONE":
            for line in result.split("\n"):
                line = line.strip().lstrip("-").strip()
                if line and len(line) > 3:
                    add_memory(user_id, line)

    except Exception as e:
        print(f"Memory extract error: {e}")


async def ask_groq(
    prompt: str,
    user_id: int = None,
    use_history: bool = True,
    mode: str = "correct"
) -> str:
    try:
        system = SYSTEM_PROMPT

        if user_id is not None:
            memory_context = build_memory_context(user_id)
            if memory_context:
                system = system + memory_context

        messages = []
        if use_history and user_id is not None:
            history = get_history(user_id)
            history.append({"role": "user", "content": prompt})
            messages = history
        else:
            messages = [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=800
        )

        reply = response.choices[0].message.content

        if use_history and user_id is not None:
            get_history(user_id).append({"role": "assistant", "content": reply})
            if len(conversation_history[user_id]) > 20:
                conversation_history[user_id] = conversation_history[user_id][-20:]

        if mode == "chat" and user_id is not None:
            _extract_memory(prompt, user_id)

        return reply

    except Exception as e:
        print(f"Groq error: {e}")
        return "⚠️ Oops! Something went wrong. Please try again!"
