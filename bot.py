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
        "🤖 হ্যালো! আমি Sariat AI Bot.\n\nআমাকে যেকোনো প্রশ্ন করুন।\n\n🌐 ওয়েব সার্চ করতে লিখুন:\n/search আপনার প্রশ্ন"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": [
            {"role": "user", "content": user_text}
        ]
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
            reply = f"❌ Error:\n{result}"

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("ব্যবহার:\n/search আপনার প্রশ্ন")
        return

    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "query": query,
        "search_depth": "basic",
        "max_results": 3,
    }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=data,
            timeout=30,
        )

        result = response.json()

        if "results" not in result:
            await update.message.reply_text(str(result))
            return

        text = "🌐 Web Search Results\n\n"

        for item in result["results"]:
            text += f"🔹 {item['title']}\n"
            text += f"{item['url']}\n\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()