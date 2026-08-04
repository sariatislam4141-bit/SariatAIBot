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
    if "আসসালামু আলাইকুম" in text or "assalamu alaikum" in text:
        await update.message.reply_text(
            "ওয়ালাইকুমুস সালাম ওয়া রাহমাতুল্লাহি ওয়া বারাকাতুহ। 🤍"
        )
        return

    if "নমস্কার" in text:
        await update.message.reply_text(
            "নমস্কার! 😊 কীভাবে সাহায্য করতে পারি?"
        )
        return

    if (
        "হ্যালো" in text
        or "হাই" in text
        or "hello" in text
        or "hi" in text
    ):
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
                    "সবসময় ভদ্র, সহায়ক ও সংক্ষিপ্তভাবে উত্তর দেবে। "
                    "ব্যবহারকারীর ধর্ম বা ব্যক্তিগত পরিচয় না জেনে "
                    "'নমস্কার' বা কোনো ধর্মীয় সম্ভাষণ ব্যবহার করবে না। "
                    "নিরপেক্ষভাবে 'হ্যালো' ব্যবহার করবে।"
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
    }try:
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
        await update.message.reply_text(f"❌ {e}")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = " ".join(context.args)

    if not query:
        await update.message.reply_text(
            "ব্যবহার:\n/search আপনার প্রশ্ন"
        )
        return

    try:
        tavily = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {TAVILY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "query": query,
                "search_depth": "advanced",
                "max_results": 5,
            },
            timeout=30,
        ).json()

        context_text = ""

        for item in tavily.get("results", []):
            context_text += (
                f"শিরোনাম: {item.get('title')}\n"
                f"তথ্য: {item.get('content')}\n\n"
            )headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [
                {
                    "role": "system",
                    "content": "তুমি Sariat AI। নিচের ওয়েব সার্চের তথ্য ব্যবহার করে সংক্ষিপ্ত, সঠিক ও বাংলায় উত্তর দাও।",
                },
                {
                    "role": "user",
                    "content": f"প্রশ্ন: {query}\n\nওয়েব তথ্য:\n{context_text}",
                },
            ],
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )

        result = response.json()

        if "choices" in result:
            answer = result["choices"][0]["message"]["content"]
        else:
            answer = str(result)

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))

    # Normal chat
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("🤖 Sariat AI Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()