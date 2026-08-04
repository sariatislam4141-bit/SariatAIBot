import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 হ্যালো! আমি Sariat AI Bot.\n\n"
        "💬 আমাকে যেকোনো প্রশ্ন করুন।\n"
        "🌐 ওয়েব সার্চ করতে লিখুন:\n"
        "/search আপনার প্রশ্ন"
    )
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    text = user_text.lower()

    # Greeting
    if any(x in text for x in ["আসসালামু আলাইকুম", "assalamu alaikum", "as-salamu alaykum"]):
        await update.message.reply_text(
            "ওয়ালাইকুমুস সালাম ওয়া রাহমাতুল্লাহি ওয়া বারাকাতুহ। 🤍"
        )
        return

    if any(x in text for x in ["হাই", "hello", "hi", "হ্যালো"]):
        await update.message.reply_text(
            "হ্যালো! 😊 কীভাবে সাহায্য করতে পারি?"
        )
        return

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-chat-v3.1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "তুমি Sariat AI নামে একটি বাংলা AI Assistant। "
                    "সবসময় ভদ্র, সহায়ক ও সংক্ষিপ্তভাবে উত্তর দেবে। "
                    "ব্যবহারকারীর ধর্ম না জেনে কোনো ধর্মীয় সম্ভাষণ ব্যবহার করবে না।"
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
    }
try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        result = response.json()

        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]
        else:
            reply = str(result)

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Sariat AI Bot চলছে...")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())