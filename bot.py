import os
import asyncio
import requests
import json
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
FAL_KEY = os.getenv("FAL_KEY")
MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_memory():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 হ্যালো! আমি Sariat AI Bot.\n\n"
        "💬 আমাকে যেকোনো প্রশ্ন করুন।\n"
        "🌐 ওয়েব সার্চ করতে লিখুন:\n"
        "/search আপনার প্রশ্ন"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    memory = load_memory()
    user_id = str(update.effective_user.id)

    if user_id not in memory:
        memory[user_id] = {}

    if "আমার নাম" in user_text:
        name = user_text.replace("আমার নাম", "").strip()
        memory[user_id]["name"] = name
        save_memory(memory)
        await update.message.reply_text(
            f"ধন্যবাদ! 😊 আপনার নাম {name} মনে রাখলাম।"
        )
        return

    if "আমার নাম কী" in user_text:
        if "name" in memory[user_id]:
            await update.message.reply_text(
                f"আপনার নাম {memory[user_id]['name']} 😊"
            )
        else:
            await update.message.reply_text(
                "আমি এখনও আপনার নাম জানি না।"
            )
        return

    text = user_text.lower()
    # Greeting
    if any(x in text for x in [
        "আসসালামু আলাইকুম",
        "assalamu alaikum",
        "as-salamu alaykum"
    ]):
        await update.message.reply_text(
            "ওয়ালাইকুমুস সালাম ওয়া রাহমাতুল্লাহি ওয়া বারাকাতুহ। 🤍"
        )
        return

    if any(x in text for x in [
        "হ্যালো",
        "হাই",
        "hello",
        "hi"
    ]):
        await update.message.reply_text(
            "হ্যালো! 😊 কীভাবে সাহায্য করতে পারি?"
        )
        return

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "তুমি Sariat AI নামে একটি বাংলা AI Assistant। "
                    "সবসময় ভদ্র, সহায়ক ও সংক্ষিপ্তভাবে উত্তর দেবে।"
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
            reply = f"❌ Error:\n{result}"

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text(
            "ব্যবহার:\n/search আপনার প্রশ্ন"
        )
        return

    try:
        tavily_response = requests.post(
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
        )

        tavily = tavily_response.json()

        context_text = ""

        for item in tavily.get("results", []):
            context_text += (
                f"Title: {item.get('title')}\n"
                f"Content: {item.get('content')}\n\n"
            )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "deepseek/deepseek-chat:free",
            "messages": [
                {
                    "role": "system",
                    "content": "নিচের ওয়েব তথ্য ব্যবহার করে বাংলায় সংক্ষেপে উত্তর দাও।",
                },
                {
                    "role": "user",
                    "content": f"প্রশ্ন: {query}\n\nওয়েব তথ্য:\n{context_text}",
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
        await update.message.reply_text(f"❌ Error: {e}")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "🖼️ ব্যবহার:\n/image একটি সুন্দর পাহাড়"
            )
            return

        prompt = " ".join(context.args)

        await update.message.reply_text("🎨 ছবি তৈরি হচ্ছে...")

        try:
            headers = {
                "Authorization": f"Key {FAL_KEY}",
                "Content-Type": "application/json",
            }

            payload = {
            "prompt": prompt
        }

            response = requests.post(
            "https://fal.run/fal-ai/flux/dev",
            headers=headers,
            json=payload,
            timeout=120,
            )

        result = response.json()

        if "images" in result:
            image_url = result["images"][0]["url"]
            await update.message.reply_photo(photo=image_url)
        else:
            await update.message.reply_text(f"❌ Error:\n{result}")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("image", image))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("🤖 Sariat AI Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()
