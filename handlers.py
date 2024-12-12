from aiogram import Router, F, Bot
from aiogram.types import Message
from image_model import process_image
from data_manager import check_limit, register_user
import aiohttp
import ssl
import certifi

router = Router()

# --- FSM для регистрации ---
@router.message(F.text == "Зарегистрироваться")
async def cmd_register(message: Message):
    user_id = message.from_user.id
    is_registered = register_user(user_id)

    if is_registered:
        await message.answer("✅ Вы успешно зарегистрированы!")
    else:
        await message.answer("❌ Вы уже зарегистрированы.")


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    user_id = message.from_user.id

    # --- Проверка лимита ---
    if not check_limit(user_id):
        await message.answer(
            "❌ Вы исчерпали свой дневной лимит на обработку изображений. "
            "Оформите подписку для доступа без ограничений.")
        return

    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        local_file_path = f"images/{photo.file_unique_id}.jpg"
        full_url = f"https://api.telegram.org/file/bot{""}/{file_path}"
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, ssl=ssl_context) as response:
                if response.status == 200:
                    with open(local_file_path, "wb") as f:
                        f.write(await response.read())
                else:
                    raise Exception(f"Ошибка при скачивании файла, статус: {response.status}")

        result = process_image(local_file_path)
        if result:
            await message.answer(f"На изображении распознан объект: {result}")
        else:
            await message.answer("❌ Объект на изображении не распознан.")
    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке изображения.")
        print(f"Ошибка обработки изображения: {e}")