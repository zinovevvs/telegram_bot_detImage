import json
from datetime import datetime

DATA_FILE = "init_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def register_user(user_id):
    data = load_data()

    if str(user_id) in data:
        return False  # Пользователь уже зарегистрирован

    data[str(user_id)] = {
        "registration_date": str(datetime.now()),
        "daily_limit": 2,  # Бесплатный лимит
        "used_today": 0,
        "active_subscription": None
    }
    save_data(data)
    return True

def check_limit(user_id):
    data = load_data()

    if str(user_id) not in data:
        return False  # Пользователь не зарегистрирован

    user = data[str(user_id)]

    today = datetime.now().date()
    last_usage_date = datetime.fromisoformat(user.get("registration_date", "1970-01-01")).date()

    # Если новый день, сброс счетчика
    if last_usage_date < today:
        user["used_today"] = 0
        user["registration_date"] = str(datetime.now())

    # Проверка лимита
    if user["used_today"] < user["daily_limit"]:
        user["used_today"] += 1
        save_data(data)
        return True  # Лимит не исчерпан
    else:
        return False  # Лимит исчерпан

def update_user_limit(user_id, new_limit):
    """
    Обновляет лимит использования для указанного пользователя.
    """
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"daily_limit": new_limit}
    else:
        data[str(user_id)]['daily_limit'] = new_limit

    save_data(data)


def update_user_subscription(user_id: int, subscription_type: str) -> bool:
    """
    Обновляет данные пользователя после успешной оплаты подписки.
    """
    try:
        with open("init_data.json", "r+") as f:
            data = json.load(f)
            if str(user_id) in data:
                data[str(user_id)]["active_subscription"] = subscription_type
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                return True
        return False
    except Exception as e:
        print(f"Ошибка обновления подписки: {e}")
        return False


def update_subscription(user_id, subscription_type):
    """
    Обновляет подписку пользователя в базе данных.
    """
    data = load_data()

    if str(user_id) not in data:
        return False  # Пользователь не зарегистрирован

    data[str(user_id)]["subscription"] = subscription_type
    data[str(user_id)]["update_date"] = str(datetime.now())  # Дата обновления подписки

    # Устанавливаю лимит для разных подписок
    if subscription_type == "econom":
        data[str(user_id)]["daily_limit"] = 10
    elif subscription_type == "premium":
        data[str(user_id)]["daily_limit"] = 20
    elif subscription_type == "lux":
        data[str(user_id)]["daily_limit"] = float("inf")  # Неограниченные распознавания
    else:
        return False

    save_data(data)
    return True
