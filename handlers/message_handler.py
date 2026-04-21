from telegram import Update
from telegram.ext import ContextTypes
from groq_helper import ask_groq

# Tracks grammar mistakes per user: { user_id: ["mistake1", ...] }
user_mistakes: dict[int, list] = {}

def save_mistake(user_id: int, mistake: str):
    if user_id not in user_mistakes:
        user_mistakes[user_id] = []
    user_mistakes[user_id].append(mistake)
    # Keep only last 20 mistakes
    if len(user_mistakes[user_id]) > 20:
        user_mistakes[user_id] = user_mistakes[user_id][-20:]

def get_mistakes(user_id: int) -> list:
    return user_mistakes.get(user_id, [])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # Reply to quiz answer
    if update.message.reply_to_message:
        previous_text = update.message.reply_to_message.text
        prompt = f"""
        The student is answering a quiz you sent them.

        Original quiz questions:
        "{previous_text}"

        Student's answers:
        "{user_text}"

        Grade their answers in simple, friendly English. 
        - If correct: celebrate briefly ✅
        - If wrong: explain why in ONE easy sentence and give the correct answer.
        - End with a short encouraging message.
        """
        reply = await ask_groq(prompt, user_id=user_id, use_history=False)

    else:
        # Normal grammar correction
        prompt = f"""
        The student sent you this message:
        "{user_text}"

        Analyze it and reply using EXACTLY this format:

        🛠️ *1. Correction*
        - Rewrite their sentence naturally and correctly.
        - Explain the mistake in ONE simple sentence. If there's no mistake, say so cheerfully!

        💬 *2. Natural Ways to Say It*
        - Give 2 casual, natural alternatives a real Canadian person would say.

        📝 *3. One Quick Tip*
        - Share one tiny grammar or vocabulary tip related to their message.

        Keep everything simple, warm, and easy to read on a phone.
        """
        reply = await ask_groq(prompt, user_id=user_id, use_history=True)

        # Extract and save mistake summary for /mistakes command
        if "mistake" in reply.lower() or "correction" in reply.lower():
            save_mistake(user_id, f'"{user_text}"')

    await update.message.reply_text(reply, parse_mode="Markdown")
