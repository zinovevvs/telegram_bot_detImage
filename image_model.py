import torch
from torchvision import models, transforms
from PIL import Image


# --- Загрузка предобученной модели ResNet ---
weights_path = "resnet50-0676ba61.pth"
imagenet_classes_path = "imagenet_classes.txt"

# Загрузка весов и классов
try:
    model = models.resnet50()
    model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    model.eval()  # Перевод модели в режим оценки
    print("Модель успешно загружена!")
except FileNotFoundError:
    print(f"Ошибка: Файл с весами модели '{weights_path}' не найден.")
    exit()
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")
    exit()

try:
    with open(imagenet_classes_path) as f:
        imagenet_classes = [line.strip() for line in f.readlines()]
    print("Классы успешно загружены!")
except FileNotFoundError:
    print(f"Ошибка: Файл с классами '{imagenet_classes_path}' не найден.")
    exit()
except Exception as e:
    print(f"Ошибка загрузки классов: {e}")
    exit()

# --- Трансформации для модели ResNet ---
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# --- Функция обработки изображения ---
def process_image(image_path: str) -> str:
    """
    Обрабатывает изображение и возвращает название распознанного объекта.
    """
    try:
        # Открытие и обработка изображения
        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0)

        # Предсказания модели
        with torch.no_grad():
            outputs = model(input_tensor)

        _, predicted_idx = outputs.max(1)

        # Возврат результата
        return imagenet_classes[predicted_idx.item()]
    except FileNotFoundError:
        return "Ошибка: Файл изображения не найден."
    except Exception as e:
        return f"Ошибка обработки изображения: {e}"


# Тест функции
# image_path = "example.jpg"  # Укажите путь к вашему изображению
# result = process_image(image_path)
# print(f"Класс изображения: {result}")