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

# প্রতিটি ব্যবহারকারীর জন্য আলাদা মেমোরি
memory = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 হ্যালো! আমি Sariat AI Bot.\n\n"
        "আমি AI দিয়ে আপনার প্রশ্নের উত্তর দিতে পারি। 😊"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({
        "role": "user",
        "content": user_text
    })

    # শুধু শেষ ১০টি মেসেজ রাখা
    messages = memory[user_id][-10:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": messages,
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

            memory[user_id].append({
                "role": "assistant",
                "content": reply
            })

            await update.message.reply_text(reply)

        else:
            await update.message.reply_text(f"❌ Error:\n{result}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Sariat AI Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()