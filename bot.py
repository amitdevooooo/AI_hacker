import logging
import requests
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ यहाँ अपने बोट टोकन, API KEY और ग्रुप यूज़रनेम डालें:
BOT_TOKEN = "7992369115:AAHClwij4Y1fjdTlHByn1_dwsQ5yhdsgh-4"
API_KEY = "AIzaSyAaq1cziEhGEYbhWl64zuykOROSiWFyRXQ"
GROUP_CHAT_ID = "@ijijin900"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

quiz_data = [
    {
        'question': 'भारत का पहला राष्ट्रपति कौन था?',
        'options': ['डॉ. राजेंद्र प्रसाद', 'डॉ. सर्वपल्ली', 'जवाहरलाल नेहरू', 'महात्मा गांधी'],
        'answer_index': 0
    },
    {
        'question': 'भारत की राजधानी क्या है?',
        'options': ['मुंबई', 'नई दिल्ली', 'कोलकाता', 'जयपुर'],
        'answer_index': 1
    }
]

current_quiz_index = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🙏 स्वागत है! यह Static GK + AI बोट है। /quiz से क्विज़ और /ask से AI से सवाल पूछें।")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/quiz - क्विज़ शुरू करें\n/ask <सवाल> - AI से सवाल पूछें")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_quiz_index
    question = quiz_data[current_quiz_index]
    keyboard = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(question['options'])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(question['question'], reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = int(query.data)
    question = quiz_data[current_quiz_index]
    correct = question['answer_index']
    if selected == correct:
        await query.edit_message_text("✅ सही जवाब!")
    else:
        await query.edit_message_text(f"❌ गलत! सही जवाब है: {question['options'][correct]}")

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ सवाल भी लिखिए: /ask What is AI?")
        return

    question = " ".join(context.args)
    reply = await get_ai_answer(question)
    await update.message.reply_text(reply)

async def get_ai_answer(question: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 150
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except:
        return "❗ जवाब नहीं मिल पाया, कृपया बाद में प्रयास करें।"

async def auto_quiz(app):
    global current_quiz_index
    await asyncio.sleep(10)
    while True:
        question = quiz_data[current_quiz_index]
        keyboard = [[InlineKeyboardButton(opt, callback_data=str(i))] for i, opt in enumerate(question['options'])]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=question['question'], reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"❗ Error sending quiz: {e}")
        current_quiz_index = (current_quiz_index + 1) % len(quiz_data)
        await asyncio.sleep(60)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_once(lambda context: asyncio.create_task(auto_quiz(app)), when=3)

    print("🤖 बोट शुरू हो गया!")
    app.run_polling()

if __name__ == "__main__":
    main()
