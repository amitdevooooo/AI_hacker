import logging
import requests
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from googleapiclient.discovery import build

# ✅ आपके TOKEN और API_KEY
BOT_TOKEN = "7992369115:AAHClwij4Y1fjdTlHByn1_dwsQ5yhdsgh-4"
API_KEY = "AIzaSyAaq1cziEhGEYbhWl64zuykOROSiWFyRXQ"
GROUP_ID = "@ijijin900"

# ✅ Google AI API से उत्तर लेने वाला फंक्शन
def ask_gemini(question):
    service = build("customsearch", "v1", developerKey=API_KEY)
    res = service.cse().list(q=question, cx="017576662512468239146:omuauf_lfve").execute()
    return res["items"][0]["snippet"] if "items" in res else "कोई उत्तर नहीं मिला।"

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 स्वागत है! मैं Static GK Quiz Bot हूँ। टाइप करें /quiz या /ask <सवाल>")

# ✅ Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/quiz - क्विज चालू करें\n/ask <सवाल> - कोई भी सवाल पूछें")

# ✅ Auto quiz data (current affairs style)
quiz_data = [
    {
        "question": "हाल ही में भारत के राष्ट्रपति कौन हैं?",
        "options": ["रामनाथ कोविंद", "द्रौपदी मुर्मू", "नरेंद्र मोदी", "अमित शाह"],
        "answer": "द्रौपदी मुर्मू",
    },
    {
        "question": "चंद्रयान-3 किस संस्था द्वारा लॉन्च किया गया?",
        "options": ["NASA", "ISRO", "DRDO", "SpaceX"],
        "answer": "ISRO",
    },
    {
        "question": "G20 सम्मेलन 2023 कहाँ हुआ?",
        "options": ["दिल्ली", "मुंबई", "बेंगलुरु", "चेन्नई"],
        "answer": "दिल्ली",
    },
]

# ✅ Quiz भेजने वाला function
async def send_quiz(app):
    data = random.choice(quiz_data)
    options = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in data["options"]]
    reply_markup = InlineKeyboardMarkup(options)
    await app.bot.send_message(chat_id=GROUP_ID, text=f"🧠 {data['question']}", reply_markup=reply_markup)
    app.bot_data["correct_answer"] = data["answer"]

# ✅ Auto quiz बार-बार भेजना
async def auto_quiz(app):
    while True:
        await send_quiz(app)
        await asyncio.sleep(60)  # हर 1 मिनट में भेजे

# ✅ Button click handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = query.data
    correct = context.bot_data.get("correct_answer", "")
    if selected == correct:
        await query.edit_message_text(f"✅ सही जवाब: {selected}")
    else:
        await query.edit_message_text(f"❌ गलत! सही जवाब था: {correct}")

# ✅ Ask command (AI answer)
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("कृपया कोई सवाल लिखें जैसे: /ask भारत का राष्ट्रपति कौन है?")
        return
    await update.message.reply_text("🧠 सोच रहा हूँ...")
    answer = ask_gemini(question)
    await update.message.reply_text(f"🔎 उत्तर:\n{answer}")

# ✅ Quiz command
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_quiz(context.application)

# ✅ Main Function (⚠️ FIXED version)
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(CallbackQueryHandler(button_handler))

    # ✅ FIXED JobQueue
    job_queue = app.job_queue
    job_queue.run_once(lambda context: asyncio.create_task(auto_quiz(app)), when=3)

    print("🤖 Bot चालू है!")
    app.run_polling()

if __name__ == "__main__":
    main()
