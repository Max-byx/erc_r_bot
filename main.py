import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = "https://erc-r-bot.onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = web.Application()

# ----------------------------------------
# ВОПРОСЫ ТЕСТА
# ----------------------------------------
QUESTIONS = [
    "Я беспокоюсь о том, что партнёр может меня разлюбить.",
    "Мне некомфортно, когда партнёр становится слишком близким.",
    "Мне важно получать подтверждение чувств партнёра.",
    "Я часто думаю о том, насколько я значим для партнёра.",
    "Я предпочитаю не слишком зависеть от партнёра.",
    "Я переживаю, что партнёр не так вовлечён в отношения, как я.",
    "Мне сложно полностью открываться партнёру.",
    "Я боюсь быть отвергнутым.",
    "Я чувствую себя скованно, когда партнёр слишком эмоционально близок.",
    "Мне нужно много подтверждений любви.",
    "Я ценю независимость больше, чем близость.",
    "Я переживаю, что партнёр меня оставит.",
    "Мне важно сохранять дистанцию в отношениях.",
    "Я сильно реагирую на признаки охлаждения со стороны партнёра.",
    "Мне сложно полагаться на партнёра.",
    "Я боюсь потерять партнёра.",
    "Я предпочитаю справляться с трудностями самостоятельно.",
    "Мне сложно переносить неопределённость в отношениях.",
    "Я чувствую дискомфорт, когда от меня ожидают эмоциональной близости.",
    "Я не люблю, когда партнёр слишком на меня рассчитывает.",
    "Я часто переживаю из-за отношений.",
    "Мне сложно делиться личными переживаниями.",
    "Я боюсь, что партнёр найдёт кого-то лучше.",
    "Я стараюсь не быть слишком эмоционально вовлечённым.",
    "Я нуждаюсь в постоянной эмоциональной поддержке.",
    "Я избегаю сильной привязанности.",
    "Я тревожусь, если партнёр долго не выходит на связь.",
    "Я чувствую себя неуютно в слишком близких отношениях.",
    "Мне важно сохранять автономию.",
    "Я переживаю, что могу остаться один.",
    "Я стараюсь держать эмоциональную дистанцию.",
    "Я часто сомневаюсь в чувствах партнёра.",
    "Я чувствую напряжение, когда отношения становятся слишком серьёзными.",
    "Мне важно, чтобы партнёр был рядом.",
    "Я избегаю зависимости в отношениях.",
    "Я боюсь эмоциональной потери."
]

ANXIETY_IDX = {0,2,3,5,7,9,11,13,15,17,20,22,24,26,29,31,33,35}
AVOIDANCE_IDX = {1,4,6,8,10,12,14,16,18,19,21,23,25,27,28,30,32,34}

user_answers = {}
user_index = {}

ANSWER_TEXT = {
    1: "1 — совсем не про меня",
    2: "2 — в основном не про меня",
    3: "3 — скорее не про меня",
    4: "4 — и да, и нет",
    5: "5 — скорее про меня",
    6: "6 — в основном про меня",
    7: "7 — полностью про меня"
}

# -----------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# -----------------------------
def scale_keyboard(show_back=False):
    kb = InlineKeyboardMarkup(row_width=7)
    buttons = [InlineKeyboardButton(str(i), callback_data=f"ans_{i}") for i in range(1, 8)]
    kb.add(*buttons)
    if show_back:
        kb.row(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    return kb

def interpret_attachment(anxiety, avoidance):
    result = []
    if anxiety <= 41 and avoidance <= 41:
        result.append("Ваш профиль соответствует надёжному стилю привязанности...")
    elif anxiety >= 42 and avoidance <= 41:
        result.append("Ваш профиль соответствует тревожному стилю привязанности...")
    elif anxiety <= 41 and avoidance >= 42:
        result.append("Ваш профиль соответствует избегающему стилю привязанности...")
    else:
        result.append("Ваш профиль соответствует тревожно-избегающему стилю привязанности...")
    
    result.append("\nЕсли вы хотите разобрать результат: https://t.me/mserganin")
    return "\n\n".join(result)

# -----------------------------
# ОБРАБОТЧИКИ
# -----------------------------
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    uid = message.from_user.id
    user_answers[uid] = []
    user_index[uid] = 0
    desc = "\n".join(ANSWER_TEXT[i] for i in range(1, 8))
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("Начать тест", callback_data="start_test"))
    await message.answer(f"Оцените утверждения от 1 до 7:\n\n{desc}", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "start_test")
async def start_test(call: types.CallbackQuery):
    uid = call.from_user.id
    user_index[uid] = 0
    user_answers[uid] = []
    await call.message.edit_text(f"Вопрос 1 из 36:\n\n{QUESTIONS[0]}", reply_markup=scale_keyboard(False))

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid in user_index and user_index[uid] > 0:
        user_index[uid] -= 1
        user_answers[uid].pop()
        qn = user_index[uid]
        await call.message.edit_text(f"Вопрос {qn + 1} из 36:\n\n{QUESTIONS[qn]}", 
                                     reply_markup=scale_keyboard(qn > 0))
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("ans_"))
async def answer_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid not in user_answers: user_answers[uid] = []
    
    score = int(call.data.split("_")[1])
    user_answers[uid].append(score)
    user_index[uid] += 1

    if user_index[uid] < 36:
        qn = user_index[uid]
        await call.message.edit_text(f"Вопрос {qn + 1} из 36:\n\n{QUESTIONS[qn]}", 
                                     reply_markup=scale_keyboard(True))
    else:
        anxiety = sum(user_answers[uid][i] for i in ANXIETY_IDX)
        avoidance = sum(user_answers[uid][i] for i in AVOIDANCE_IDX)
        interpretation = interpret_attachment(anxiety, avoidance)
        await call.message.answer(f"📊 Результаты:\nТревожность: {anxiety}\nИзбегание: {avoidance}\n\n{interpretation}")
        await call.message.delete()
    await call.answer()

# -----------------------------
# СЕРВЕРНАЯ ЧАСТЬ (ИСПРАВЛЕННАЯ)
# -----------------------------
async def handle_webhook(request):
    try:
        data = await request.json()
        update = types.Update(**data)
        # Установка контекста бота - РЕШАЕТ ОШИБКУ ИЗ ЛОГОВ
        Bot.set_current(bot)
        await dp.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Ошибка вебхука: {e}")
        return web.Response(status=500)

async def on_startup(app):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")

app.router.add_get('/', lambda r: web.Response(text="Alive"))
app.router.add_post('/webhook/{token}', handle_webhook)
app.on_startup.append(on_startup)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port, handle_signals=False)
