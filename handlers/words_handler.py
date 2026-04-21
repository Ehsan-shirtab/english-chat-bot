from telegram import Update
from telegram.ext import ContextTypes
from groq_helper import ask_groq

async def teach_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    prompt = """
    Teach 3 useful English words or idioms for an intermediate learner living in Canada.
    Choose words useful for daily life, casual talk, or general workplace situations.

    For EACH word use this exact format:

    🔤 *Word:* [word]
    📖 *Meaning:* [simple definition]
    🗣️ *Example:* [natural spoken sentence]
    🇮🇷 *Farsi:* [Farsi translation]

    Separate each word with a line break. Keep it phone-friendly.
    """

    reply = await ask_groq(prompt, use_history=False)
    await update.message.reply_text(reply, parse_mode="Markdown")

async def teach_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    topic = " ".join(context.args) if context.args else None

    if not topic:
        await update.message.reply_text(
            "Please tell me the topic! Example:\n*/topic job interview*\n*/topic making small talk*",
            parse_mode="Markdown"
        )
        return

    prompt = f"""
    Give the student a short, practical English mini-lesson on this topic: "{topic}"
    
    Include:
    🎯 3-5 key vocabulary words or phrases for this topic
    💬 2 example mini-dialogues showing real conversation
    💡 1 cultural tip about how Canadians handle this situation
    
    Keep it simple, practical, and fun. Easy to read on a phone.
    """

    reply = await ask_groq(prompt, use_history=False)
    await update.message.reply_text(reply, parse_mode="Markdown")

async def explain_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    word = " ".join(context.args) if context.args else None

    if not word:
        await update.message.reply_text(
            "Please give me a word! Example:\n*/explain procrastinate*\n*/explain take off*",
            parse_mode="Markdown"
        )
        return

    prompt = f"""
    Give a detailed but simple explanation of the English word/phrase: "{word}"

    Include:
    📖 *Meaning:* simple definition
    🗣️ *Formal example:* how to use it at work
    😄 *Casual example:* how to use it with friends
    ⚠️ *Common mistake:* one error learners often make with this word
    🇮🇷 *Farsi:* translation
    🔗 *Similar words:* 2 synonyms or related words

    Keep it friendly and phone-readable with emojis.
    """

    reply = await ask_groq(prompt, use_history=False)
    await update.message.reply_text(reply, parse_mode="Markdown")
