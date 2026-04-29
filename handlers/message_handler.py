from telegram import Update
from telegram.ext import ContextTypes
from groq_helper import ask_groq, get_mode

user_mistakes: dict[int, list] = {}


def save_mistake(user_id: int, mistake: str):
    if user_id not in user_mistakes:
        user_mistakes[user_id] = []
    user_mistakes[user_id].append(mistake)
    if len(user_mistakes[user_id]) > 20:
        user_mistakes[user_id] = user_mistakes[user_id][-20:]


def get_mistakes(user_id: int) -> list:
    return user_mistakes.get(user_id, [])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    mode = get_mode(user_id)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    # Quiz answer
    if update.message.reply_to_message:
        previous_text = update.message.reply_to_message.text
        prompt = f"""
The student is answering a quiz you sent them.
Original quiz:
"{previous_text}"
Student answers:
"{user_text}"
Grade their answers simply and kindly.
Celebrate correct answers. Explain wrong ones in one sentence.
End with encouragement.
"""
        reply = await ask_groq(
            prompt, user_id=user_id, use_history=False, mode="correct"
        )
        await update.message.reply_text(reply, parse_mode="Markdown")
        return

    if mode == "chat":
        # Friend + correction combined
        prompt = f"""
The student sent you this message:
"{user_text}"

You are their Canadian friend AND their gentle English tutor at the same time.

Reply in EXACTLY this format:

First write a warm friendly reply like a real friend would.
Be genuinely interested, ask a follow up question, share your reaction.
2 to 4 sentences, natural and conversational.

Then write this separator on its own line:
─────────────────

Then write EXACTLY this:

✏️ *Quick Fix:*
[If there is a grammar mistake: rewrite the sentence correctly and explain in ONE simple sentence.]
[If there is NO mistake: write "Perfect sentence! Nothing to fix 🎉"]

💬 *Natural Ways to Say It:*
[2 short alternatives a real Canadian would say]

📝 *Quick Tip:*
[One tiny grammar or vocabulary tip related to their message]

Rules:
- Friendly reply FIRST always
- Correction AFTER the separator always
- Never skip correction even if sentence is perfect
- Keep it simple, warm, and phone friendly
"""
        reply = await ask_groq(
            prompt, user_id=user_id, use_history=True, mode="chat"
        )

    else:
        # Correction only mode
        prompt = f"""
The student sent you this message:
"{user_text}"

Analyze it and reply using EXACTLY this format:

🛠️ *1. Correction*
- Rewrite their sentence naturally and correctly.
- Explain the mistake in ONE simple sentence. If no mistake, say so cheerfully!

💬 *2. Natural Ways to Say It*
- Give 2 casual natural alternatives a real Canadian would say.

📝 *3. One Quick Tip*
- Share one tiny grammar or vocabulary tip related to their message.

Keep everything simple, warm, and easy to read on a phone.
"""
        reply = await ask_groq(
            prompt, user_id=user_id, use_history=True, mode="correct"
        )

    if "mistake" in reply.lower() or "fix" in reply.lower():
        save_mistake(user_id, f'"{user_text}"')

    await update.message.reply_text(reply, parse_mode="Markdown")
