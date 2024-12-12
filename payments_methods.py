from aiogram import Router, F
from aiogram.types import Message
from data_manager import update_user_limit, check_limit
from aiogram.types import LabeledPrice, PreCheckoutQuery

router = Router()

PRICES = {
    "Эконом": [LabeledPrice(label="Эконом", amount=50000)],  # 500 рублей
    "Премиум": [LabeledPrice(label="Премиум", amount=100000)],  # 1000 рублей
    "Люкс": [LabeledPrice(label="Люкс", amount=150000)]  # 1500 рублей
}

# --- Отправка счета ---
async def check_user_registered(user_id: int) -> bool:
    """
    Проверяет, есть ли пользователь в init_data.json, используя user_id.
    """
    user_data = check_limit(user_id)
    return user_data is not None

async def send_invoice(message: Message, subscription_type: str):
    """
    Отправляет счет на оплату указанной подписки.
    """
    user_id = message.from_user.id

    # Проверка решистрации пользователя
    if not await check_user_registered(user_id):
        await message.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь.")
        return

    if subscription_type in PRICES:
        try:
            # Отправка счета для оплаты
            await message.answer_invoice(


                title=f"Подписка {subscription_type}",
                description=f"Оплата подписки: {subscription_type}.",
                payload=subscription_type,
                provider_token="",
                currency="RUB",
                prices=PRICES[subscription_type],
                start_parameter="subscription-payment",
            )
        except Exception as e:
            await message.answer(f"Ошибка отправки счета: {e}")
    else:
        await message.answer("Ошибка: Такой подписки не существует.")


# --- Обработка предоплаты ---
@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --- Обработка успешной оплаты ---
async def handle_payment_success(user_id, subscription_type):
    """
    Обрабатывает успешную оплату, устанавливая лимит в зависимости от тарифа.
    """
    # Определение зависимости подписки
    if subscription_type == "Эконом":
        new_limit = 10
    elif subscription_type == "Премиум":
        new_limit = 20
    elif subscription_type == "Люкс":
        new_limit = float("inf")
    else:
        new_limit = 0

    update_user_limit(user_id, new_limit)

@router.message(F.successful_payment)
async def handle_successful_payment(message: Message):
    """
    Обработчик события успешной оплаты.
    """
    try:
        user_id = message.from_user.id
        subscription_type = message.successful_payment.invoice_payload

        await handle_payment_success(user_id, subscription_type)

        await message.answer(f"✅ Подписка '{subscription_type}' успешно активирована! Ваш лимит обновлен.")

    except (KeyError, ValueError) as error:
        await message.answer(f"❌ Ошибка при обработке платежа: {error}")
        print(error)