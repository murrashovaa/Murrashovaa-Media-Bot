# Murrashovaa Media Bot

Telegram-бот для скачивания, конвертации и обработки медиафайлов.

Бот позволяет скачивать аудио и видео, редактировать MP3-метаданные,
добавлять обложки и удалять фон с изображений прямо внутри Telegram.

Проект поддерживает локальный запуск и развёртывание на сервере через
Docker.

---

# Возможности

## 🎵 Скачать музыку

Поддерживаемые источники: - Hitmo/Hitmos поиск по названию - YouTube -
SoundCloud - TikTok - Instagram

Функции: - поиск песни по названию с нумерованным списком вариантов; -
скачивание выбранного трека; - скачивание аудио по ссылке; - конвертация в
MP3; - отправка файла пользователю; - очистка временных файлов.

## 🎬 Скачать видео

Поддерживаемые источники: - YouTube - TikTok - Instagram

Функции: - скачивание видео; - подготовка MP4 для Telegram; - сохранение
пропорций; - сжатие больших файлов под лимиты Telegram Bot API.

## 🏷 Редактирование тегов

Поддерживается: - просмотр ID3-метаданных; - изменение названия,
исполнителя, альбома, года и жанра; - добавление и замена обложки.

## ✂️ Удаление фона

Поддерживаемые форматы: - JPG - PNG - WEBP - HEIC

Используется: - rembg; - alpha matting; - Segment Anything как fallback.

---

# Архитектура

    Telegram Users
           |
           v
    Telegram Bot (aiogram)
           |
           v
    Docker Container
           |
           v
    Yandex Cloud VM
           |
           +----------------+
           |                |
           v                v
       Xray Proxy       Media Processing
       VLESS Reality    yt-dlp/rembg/SAM
           |
           v
    Telegram API

----

# Структура проекта

    media_bot/
    ├── config/
    ├── downloader/
    │   ├── music.py
    │   ├── search.py
    │   └── video.py
    ├── image/
    ├── services/
    ├── tags/
    ├── telegram_bot/
    ├── models/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    └── README.md

---

# Технологии

-   Python 3.12
-   aiogram 3
-   Docker
-   Docker Compose
-   requests
-   yt-dlp
-   FFmpeg
-   Mutagen
-   Pillow
-   rembg
-   Segment Anything
-   Xray (VLESS Reality)

---

# Настройка

Создать файл `.env`:

``` env
BOT_TOKEN=your_token
ADMIN_IDS=
STORAGE_PATH=storage/temp
STORAGE_CLEANUP_MAX_AGE_HOURS=12
VIDEO_MAX_HEIGHT=1080
YTDLP_COOKIES_FILE=storage/cookies/youtube.txt
```

Секреты не хранятся в Git.

---

# Локальный запуск

Установка зависимостей:

``` bash
pip install -r requirements.txt
```

Запуск:

``` bash
python -m telegram_bot.bot
```

---

# Запуск через Docker

Сборка:

``` bash
docker build -t media-bot .
```

Запуск:

``` bash
docker-compose up -d
```

Проверка:

``` bash
docker ps
```

Логи:

``` bash
docker logs -f media-bot
```

Остановка:

``` bash
docker-compose down
```

---

# Серверный деплой

Проект разворачивается на Linux VM.

Используется:

-   Docker для приложения;
-   docker-compose для управления контейнером;
-   systemd для Xray;
-   VLESS Reality для доступа к Telegram API.

Xray предоставляет локальный SOCKS5-прокси:

    127.0.0.1:1080

Конфигурация Xray не хранится в репозитории.

---

# Безопасность

В Git не добавляются:

-   `.env`;
-   Telegram Bot Token;
-   Xray/VLESS конфигурации;
-   cookies YouTube;
-   приватные ключи.

---

# Статус проекта

Готово:

-   Telegram-бот на aiogram;
-   скачивание аудио и видео;
-   обработка MP3-тегов;
-   добавление обложек;
-   удаление фона изображений;
-   Docker-развёртывание;
-   серверный запуск 24/7;
-   проксирование Telegram API через Xray.

---

# Автор

**Murrashovaa**

Murrashovaa Media Bot - Telegram-инструмент для работы с медиафайлами.
