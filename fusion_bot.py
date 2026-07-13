import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- ТВОИ ДАННЫЕ (УЖЕ ВСТАВЛЕНЫ) ---
TOKEN = "8813591285:AAFviC_uOYTB-4x9HaEDrZRQUtCaOya1RrY"
ADMIN_ID = 1431254201

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- ВОПРОСЫ (ТОЛЬКО НАПРАВЛЕНИЯ, БЕЗ РОЛЕЙ) ---
QUESTIONS = [
    {
        "q": "Что для тебя важнее всего в творческом проекте?",
        "options": [
            ("Атмосфера и настроение", "music"),
            ("Чёткая структура и драматургия", "theatre"),
            ("Красота деталей и визуальная эстетика", "dpi"),
            ("Энергия и движение", "dance"),
            ("Звучание и ритм", "music"),
        ],
    },
    {
        "q": "Как ты чаще всего выражаешь эмоции?",
        "options": [
            ("Через тело и пластику", "dance"),
            ("Через голос и интонации", "music"),
            ("Через создание предметов, рисунков, форм", "dpi"),
            ("Через образы и перевоплощения", "theatre"),
            ("Через музыку или ритм", "music"),
        ],
    },
    {
        "q": "Что тебя вдохновляет больше всего?",
        "options": [
            ("Живая музыка и звуки вокруг", "music"),
            ("Люди, их истории и эмоции", "theatre"),
            ("Красота природы, тканей, материалов", "dpi"),
            ("Театральные постановки и кино", "theatre"),
            ("Движение, танец, хореография", "dance"),
        ],
    },
    {
        "q": "Какой формат работы тебе ближе?",
        "options": [
            ("Работа в команде над общим действом", "theatre"),
            ("Сольное выступление или самовыражение", "music"),
            ("Создание визуального или материального объекта", "dpi"),
            ("Работа над атмосферой и светом", "theatre"),
            ("Импровизация на ходу", "dance"),
        ],
    },
    {
        "q": "Что ты хочешь создавать или развивать в первую очередь?",
        "options": [
            ("Музыку, песни, мелодии", "music"),
            ("Сценические образы, характеры, истории", "theatre"),
            ("Визуал, костюмы, декорации, фактуры", "dpi"),
            ("Танец, пластику, движение", "dance"),
        ],
    },
]

user_answers = {}
casting_data = {}
casting_users = {}

direction_map_ru = {
    "vocal": "🎵 Вокал",
    "dance": "💃 Танец",
    "theatre": "🎭 Театр",
    "dpi": "🎨 ДПИ",
    "music": "🎶 Музыка",
}

# --- /START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎯 Пройти тест", callback_data="start_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🔥 **Добро пожаловать в «Фьюжн»!**\n\n"
        "Мы — студия, где музыка, вокал, танец, театр "
        "и декоративно-прикладное искусство сплавляются в единое целое.\n\n"
        "Нажми на кнопку, чтобы пройти творческий тест и понять, "
        "какое направление откликается именно тебе.\n\n"
        "Займёт не больше 2 минут!"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_answers[user_id] = []
    await ask_question(update, context, 0)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index: int):
    question = QUESTIONS[q_index]
    keyboard = [
        [InlineKeyboardButton(text, callback_data=f"{q_index}|{value}")]
        for text, value in question["options"]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"**Вопрос {q_index + 1} из {len(QUESTIONS)}**\n\n{question['q']}"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data.split("|")
    q_index = int(data[0])
    answer = data[1]

    user_answers.setdefault(user_id, []).append(answer)

    if q_index + 1 < len(QUESTIONS):
        await ask_question(update, context, q_index + 1)
    else:
        await show_result(update, context, user_id)


async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    answers = user_answers.get(user_id, [])
    scores = {"music": 0, "dance": 0, "theatre": 0, "dpi": 0}
    for a in answers:
        if a in scores:
            scores[a] += 1

    max_score = max(scores.values())
    best = [key for key, val in scores.items() if val == max_score]

    direction_text = {
        "music": "🎵 **Музыка и вокал** — твой мир звуков и ритмов!",
        "dance": "💃 **Танец и пластика** — ты выражаешь себя через движение!",
        "theatre": "🎭 **Театр и драматургия** — ты создаёшь миры и истории!",
        "dpi": "🎨 **Декоративно-прикладное искусство** — ты видишь красоту в деталях!",
    }

    result_text = "✨ **Твои результаты:**\n\n"
    for key, val in scores.items():
        emoji = {"music": "🎵", "dance": "💃", "theatre": "🎭", "dpi": "🎨"}[key]
        name = direction_text[key].split("—")[0].strip()
        result_text += f"{emoji} {name}: {val}/5\n"

    result_text += "\n" + direction_text[best[0]]
    if len(best) > 1:
        result_text += "\n\n🌟 У тебя несколько сильных сторон! В «Фьюжн» мы приветствуем сочетание жанров."

    # Отправка админу
    try:
        admin_message = (
            f"📩 **Новый результат теста!**\n\n"
            f"👤 Пользователь: {update.effective_user.first_name} (@{update.effective_user.username or 'нет'})\n"
            f"🆔 ID: {user_id}\n\n"
            f"📊 **Баллы:**\n"
            f"🎵 Музыка: {scores['music']}/5\n"
            f"💃 Танец: {scores['dance']}/5\n"
            f"🎭 Театр: {scores['theatre']}/5\n"
            f"🎨 ДПИ: {scores['dpi']}/5\n\n"
            f"🏆 **Рекомендация:** {direction_text[best[0]]}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Не удалось отправить админу: {e}")

    # Кнопка кастинга
    keyboard = [[InlineKeyboardButton("🎭 Подать заявку на кастинг", callback_data="casting_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    final_text = result_text + "\n\n👇 Хочешь стать частью «Фьюжн»? Нажми на кнопку!"

    if update.callback_query:
        await update.callback_query.edit_message_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)

    user_answers.pop(user_id, None)


# ==================== КАСТИНГ ====================

async def casting_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    casting_data[user_id] = {}
    
    keyboard = [
        [InlineKeyboardButton("✅ Да, соглашаюсь", callback_data="casting_consent_yes")],
        [InlineKeyboardButton("❌ Нет, не соглашаюсь", callback_data="casting_consent_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📋 **Кастинг в студию «Фьюжн»**\n\n"
        "Перед заполнением анкеты нам нужно твоё согласие на обработку персональных данных.\n\n"
        "Ты соглашаешься?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def casting_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "casting_consent_no":
        await query.edit_message_text("😔 Понимаем. Если передумаешь — возвращайся!", parse_mode="Markdown")
        casting_data.pop(user_id, None)
        return
    
    casting_data[user_id]["consent"] = True
    await query.edit_message_text(
        "📝 **Шаг 1 из 3: ФИО**\n\n"
        "Напиши свои **фамилию, имя и отчество**.\n\n"
        "Просто напиши сообщение в этот чат 👇",
        parse_mode="Markdown"
    )
    context.user_data["waiting_for"] = "full_name"


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    waiting_for = context.user_data.get("waiting_for")
    
    if waiting_for == "full_name":
        casting_data.setdefault(user_id, {})["full_name"] = text
        context.user_data["waiting_for"] = "age"
        await update.message.reply_text(
            "📝 **Шаг 2 из 3: Возраст**\n\n"
            "Сколько тебе лет?\n\n"
            "Напиши число в сообщении 👇",
            parse_mode="Markdown"
        )
    
    elif waiting_for == "age":
        if not text.isdigit():
            await update.message.reply_text("⚠️ Напиши число.")
            return
        casting_data.setdefault(user_id, {})["age"] = text
        await ask_direction(update, context, user_id)
    
    else:
        await update.message.reply_text("Используй /start")


async def ask_direction(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
    if user_id is None:
        user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🎵 Вокал", callback_data="direction_vocal")],
        [InlineKeyboardButton("💃 Танец", callback_data="direction_dance")],
        [InlineKeyboardButton("🎭 Театр", callback_data="direction_theatre")],
        [InlineKeyboardButton("🎨 ДПИ", callback_data="direction_dpi")],
        [InlineKeyboardButton("🎶 Музыка", callback_data="direction_music")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "📝 **Шаг 3 из 3: Твоё направление**\n\n"
            "Какая сфера тебе ближе всего?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "📝 **Шаг 3 из 3: Твоё направление**\n\n"
            "Какая сфера тебе ближе всего?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def ask_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    direction = query.data.replace("direction_", "")
    casting_data[user_id]["direction"] = direction
    
    keyboard = [
        [InlineKeyboardButton("🌱 Нет опыта", callback_data="exp_none")],
        [InlineKeyboardButton("🌿 До 1 года", callback_data="exp_beginner")],
        [InlineKeyboardButton("🌳 1-3 года", callback_data="exp_intermediate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📝 **Финальный шаг: Опыт**\n\n"
        "Какой у тебя опыт в выбранной сфере?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def finish_casting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    experience = query.data.replace("exp_", "")
    casting_data[user_id]["experience"] = experience
    data = casting_data.get(user_id, {})
    
    direction_map = {
        "vocal": "🎵 Вокал",
        "dance": "💃 Танец",
        "theatre": "🎭 Театр",
        "dpi": "🎨 ДПИ",
        "music": "🎶 Музыка",
    }
    
    experience_map = {
        "none": "🌱 Нет опыта",
        "beginner": "🌿 До 1 года",
        "intermediate": "🌳 1-3 года",
    }
    
    direction_key = data.get("direction", "")
    
    admin_message = (
        f"📩 **НОВАЯ ЗАЯВКА НА КАСТИНГ!**\n\n"
        f"👤 ФИО: {data.get('full_name', '—')}\n"
        f"📅 Возраст: {data.get('age', '—')}\n"
        f"🎭 Направление: {direction_map.get(direction_key, '—')}\n"
        f"📊 Опыт: {experience_map.get(data.get('experience', ''), '—')}\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{update.effective_user.username or 'нет'}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")
        await query.edit_message_text(
            "✅ **Заявка отправлена!**\n\n"
            "Спасибо! Мы свяжемся с тобой в ближайшее время.",
            parse_mode="Markdown"
        )
        
        if user_id not in casting_users:
            casting_users[user_id] = direction_key
        
    except Exception as e:
        await query.edit_message_text("⚠️ Что-то пошло не так, попробуй позже.")
        print(f"Ошибка: {e}")
    
    casting_data.pop(user_id, None)
    context.user_data.pop("waiting_for", None)


# ==================== РАССЫЛКА ПО НАПРАВЛЕНИЯМ ====================

async def send_casting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У тебя нет доступа.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "⚠️ Использование:\n"
            "`/send_casting [направление] [дата и время]`\n\n"
            "Направления:\n"
            "• вокал\n"
            "• танец\n"
            "• театр\n"
            "• дпи\n"
            "• музыка\n"
            "• все\n\n"
            "Примеры:\n"
            "`/send_casting вокал 25 июля, 18:00`\n"
            "`/send_casting все 30 июля, 12:00`",
            parse_mode="Markdown"
        )
        return
    
    direction_input = args[0].lower()
    date_time = " ".join(args[1:])
    
    direction_map_input = {
        "вокал": "vocal",
        "танец": "dance",
        "театр": "theatre",
        "дпи": "dpi",
        "музыка": "music",
        "все": "all",
    }
    
    direction_key = direction_map_input.get(direction_input)
    if not direction_key:
        await update.message.reply_text(
            "⚠️ Неизвестное направление.\n\n"
            "Доступные: вокал, танец, театр, дпи, музыка, все"
        )
        return
    
    users_to_send = []
    if direction_key == "all":
        users_to_send = list(casting_users.items())
    else:
        users_to_send = [(uid, d) for uid, d in casting_users.items() if d == direction_key]
    
    if not users_to_send:
        await update.message.reply_text(f"📭 Нет заявок на направление «{direction_input}».")
        return
    
    await update.message.reply_text(f"📤 Начинаю рассылку {len(users_to_send)} пользователям...")
    
    success = 0
    fail = 0
    
    direction_emoji = {
        "vocal": "🎵",
        "dance": "💃",
        "theatre": "🎭",
        "dpi": "🎨",
        "music": "🎶",
    }
    
    direction_name_ru = {
        "vocal": "Вокал",
        "dance": "Танец",
        "theatre": "Театр",
        "dpi": "ДПИ",
        "music": "Музыка",
    }
    
    for user_id, user_direction in users_to_send:
        try:
            emoji = direction_emoji.get(user_direction, "🎭")
            dir_name = direction_name_ru.get(user_direction, "")
            
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🎬 **Приглашение на кастинг!**\n\n"
                    f"{emoji} Направление: **{dir_name}**\n"
                    f"📅 Дата и время: **{date_time}**\n\n"
                    f"Ждём тебя в студии «Фьюжн»! 🔥"
                ),
                parse_mode="Markdown"
            )
            success += 1
        except Exception as e:
            fail += 1
            print(f"Не удалось отправить {user_id}: {e}")
    
    await update.message.reply_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не доставлено: {fail}"
    )


# ==================== ЗАПУСК ====================

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send_casting", send_casting))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="start_quiz"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^\d+\|"))
    app.add_handler(CallbackQueryHandler(casting_start, pattern="casting_start"))
    app.add_handler(CallbackQueryHandler(casting_consent, pattern="casting_consent_"))
    app.add_handler(CallbackQueryHandler(ask_experience, pattern="exp_"))
    app.add_handler(CallbackQueryHandler(finish_casting, pattern="finish_casting"))
    app.add_handler(CallbackQueryHandler(ask_direction, pattern="direction_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
