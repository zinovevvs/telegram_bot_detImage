from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import asyncio
from payments_methods import router as payment_router
from handlers import router as handlers_router
from aiogram.fsm.storage.memory import MemoryStorage
import os
from payments_methods import send_invoice

# --- Настройки бота ---
API_TOKEN = ""
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# --- Основная клавиатура ---
buttons = [
    [KeyboardButton(text="Старт бота")], [KeyboardButton(text="Выбор подписки")],
    [KeyboardButton(text="Зарегистрироваться")]
]
keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
# --- Клавиатура подписок ---
subscription_buttons = [
    [KeyboardButton(text="Эконом - 10 распознований"), KeyboardButton(text="Премиум - 20 распознований"),
     KeyboardButton(text="Люкс - неограничено")],
    [KeyboardButton(text="Назад")]
]
subscription_keyboard = ReplyKeyboardMarkup(keyboard=subscription_buttons, resize_keyboard=True)

@router.message(F.text.in_(["Эконом - 10 распознований", "Премиум - 20 распознований", "Люкс - неограничено"]))
async def handle_subscription_choice(message: Message):
    """
    Обработчик выбора подписки. Отправляет счет на оплату.
    """
    user_id = message.from_user.id

    subscription_map = {
        "Эконом - 10 распознований": "Эконом",
        "Премиум - 20 распознований": "Премиум",
        "Люкс - неограничено": "Люкс"
    }

    subscription_type = subscription_map.get(message.text)

    if subscription_type:
        await send_invoice(message, subscription_type=subscription_type)
    else:
        await message.answer("Ошибка: Неверный выбор подписки.")


@router.message(F.text == "Выбор подписки")
async def cmd_select_subscription(message: Message):
    await message.answer("Выберите подписку:", reply_markup=subscription_keyboard)

@router.message(F.text == "Назад")
async def cmd_back_to_main(message: Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=keyboard)

@router.message(F.Command("start"))
@router.message(F.text == "Старт бота")
async def cmd_start(message: Message):
    await message.answer("Бот запущен. Выберите опцию на клавиатуре ниже:", reply_markup=keyboard)

@router.message(F.Command("restart"))
async def cmd_restart(message: Message):
    await message.answer("Бот успешно перезапущен.", reply_markup=keyboard)

async def main():
    print("Запуск бота...")

    # Регистрация маршрутов
    dp.include_router(router)
    dp.include_router(payment_router)
    dp.include_router(handlers_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    os.makedirs("images", exist_ok=True)
    asyncio.run(main())