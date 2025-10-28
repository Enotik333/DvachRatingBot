import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === НАСТРОЙКИ ===
TOKEN = "8284745407:AAFqGY7YtN4-pWe-75yEUor1o1cWcsrKG8w"  # примерный токен
DATA_FILE = "data.json"
UP_WORDS = ["+", "ап", "двачую", "согласен", "поддерживаю"]
DOWN_WORDS = ["сажа"]

# === ХРАНЕНИЕ ДАННЫХ ===
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === ОБРАБОТКА СООБЩЕНИЙ ===
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    data = load_data()

    # Проверяем, является ли сообщение ответом
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = str(target_user.id)
        target_name = target_user.first_name
        data.setdefault(target_id, {"name": target_name, "score": 0})

        # Повышаем рейтинг
        if any(word in text.split() for word in UP_WORDS):
            data[target_id]["score"] += 1
            save_data(data)
            await update.message.reply_text(f"👍 {target_name}, твой рейтинг: {data[target_id]['score']}")

        # Понижаем рейтинг
        elif any(word in text.split() for word in DOWN_WORDS):
            data[target_id]["score"] -= 1
            save_data(data)
            await update.message.reply_text(f"👎 {target_name}, твой рейтинг: {data[target_id]['score']}")

# === КОМАНДЫ ===
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.message.from_user.id)
    score = data.get(user_id, {}).get("score", 0)
    await update.message.reply_text(f"💬 Твой рейтинг: {score}")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    if not data:
        await update.message.reply_text("Пока никто не апался 😅")
        return
    top_users = sorted(data.values(), key=lambda x: x["score"], reverse=True)
    text = "🏆 Топ пользователей:\n"
    for i, user in enumerate(top_users[:10], start=1):
        text += f"{i}. {user['name']} — {user['score']}\n"
    await update.message.reply_text(text)

# === ЗАПУСК ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
app.add_handler(CommandHandler("me", me))
app.add_handler(CommandHandler("top", top))

print("🤖 Бот запущен...")
app.run_polling()
