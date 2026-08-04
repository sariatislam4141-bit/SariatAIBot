import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 হ্যালো! আমি Sariat AI Bot\n\n"
        "💬 যেকোনো প্রশ্ন করুন\n"
        "🌐 ওয়েব সার্চ:\n"
        "/search আপনার প্রশ্ন"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-chat-v3.1",
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
            reply = str(result)

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("ব্যবহার:\n/search আপনার প্রশ্ন")
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
            )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "deepseek/deepseek-chat-v3.1",
            "messages": [
                {
                    "role": "user",
                    "content":
                    f"নিচের তথ্য ব্যবহার করে বাংলায় সুন্দর উত্তর দাও।\n\nপ্রশ্ন: {query}\n\nতথ্য:\n{context_text}"
                }
            ]
        }

        ai = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        ).json()

        if "choices" in ai:
            answer = ai["choices"][0]["message"]["content"]
        else:
            answer = str(ai)

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()