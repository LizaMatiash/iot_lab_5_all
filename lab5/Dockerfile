# Використовуємо базовий образ Python
FROM python:3.9

# Додамо необхідні пакети для графічного інтерфейсу
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libmtdev-dev \
    xorg \
    x11-apps

# Копіюємо requirements.txt у контейнер
COPY requirements.txt /app/requirements.txt

# Встановлюємо залежності
RUN pip install -r /app/requirements.txt

# Копіюємо всі файли з локальної папки в робочий каталог образу
COPY . /app

# Задаємо робочий каталог
WORKDIR /app

# Налаштовуємо змінну середовища DISPLAY для використання X-сервера
ENV DISPLAY=:0

# Команда для запуску вашого Python-застосунку
CMD ["python", "main.py"]

