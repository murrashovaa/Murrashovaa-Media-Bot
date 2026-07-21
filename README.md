# 🎵 Murrashovaa Media Bot

Telegram-бот для загрузки, конвертации и обработки медиафайлов.

**Murrashovaa Media Bot** — это универсальный инструмент для работы с музыкой, видео и изображениями прямо внутри Telegram.

---

# 🚀 Возможности

## 🎵 Скачать музыку

Поддерживаемые источники:

- YouTube
- SoundCloud

Функции:

- загрузка аудио по ссылке;
- автоматическая конвертация в MP3;
- отправка готового файла прямо в Telegram;
- очистка временных файлов после обработки.

---

## 🎬 Скачать видео

Поддерживаемые источники:

- YouTube
- TikTok
- Instagram

Функции:

- загрузка видео;
- сохранение в MP4;
- отправка файла пользователю.

---

## 🏷 Редактирование тегов

Работа с музыкальными метаданными:

- название трека;
- исполнитель;
- альбом;
- жанр;
- год выпуска;
- номер трека;
- обложка.

Поддержка:

- ID3-тегов;
- добавления изображений в аудиофайлы.

---

## ✂️ Удаление фона

Обработка изображений с помощью AI:

- загрузка изображения;
- удаление фона;
- получение PNG-файла с прозрачностью.

Используется для:

- создания обложек;
- обработки изображений.

---

# 🏗 Архитектура проекта

```
media_bot/

├── telegram_bot/
│   ├── bot.py
│   ├── handlers.py
│   ├── keyboards.py
│   └── states.py
│
├── downloader/
│   ├── music.py
│   └── video.py
│
├── services/
│   └── downloader_service.py
│
├── audio/
│   ├── analyzer.py
│   ├── converter.py
│   └── normalize.py
│
├── tags/
│   ├── parser.py
│   ├── editor.py
│   ├── metadata.py
│   └── cover.py
│
├── image/
│   └── remove_background.py
│
├── database/
│   ├── database.py
│   └── users.py
│
├── config/
│   └── settings.py
│
├── requirements.txt
├── Dockerfile
├── .env
├── .gitignore
└── README.md
```

---

# 🛠 Технологии

## Backend

- Python 3.12
- aiogram 3
- asyncio

## Работа с медиа

- yt-dlp
- FFmpeg
- Mutagen

## Изображения

- Pillow
- rembg

## Работа с данными

- SQLAlchemy
- PostgreSQL

## Deployment

- Docker
- Linux
- CI/CD

---

# ⚙️ Установка

## 1. Клонирование проекта

```bash
git clone <repository_url>

cd media_bot
```

---

## 2. Создание виртуального окружения

Используется Python 3.12:

```bash
python3.12 -m venv venv
```

Активация:

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## 4. Установка FFmpeg

macOS:

```bash
brew install ffmpeg
```

Проверка:

```bash
ffmpeg -version
```

---

## 5. Настройка переменных окружения

Создать файл:

```
.env
```

Добавить:

```env
BOT_TOKEN=your_telegram_bot_token

DATABASE_URL=sqlite:///database.db

STORAGE_PATH=storage
```

---

## 6. Запуск

Из корня проекта:

```bash
python -m telegram_bot.bot
```

После запуска бот будет доступен в Telegram.

---

# 📱 Интерфейс бота

Главное меню:

```
🎵 Скачать музыку     🎬 Скачать видео

🏷 Редактировать теги ✂️ Удалить фон
```

---

# 📂 Хранение файлов

Временные файлы используются только во время обработки:

```
storage/

└── temp/
```

После успешной отправки пользователю временные файлы удаляются.

---

# 🔄 Архитектура обработки

## Загрузка музыки

```
Telegram
    |
    ↓
Пользователь отправляет ссылку
    |
    ↓
FSM состояние
    |
    ↓
Downloader Service
    |
    ↓
yt-dlp
    |
    ↓
FFmpeg
    |
    ↓
MP3
    |
    ↓
Telegram
```

---

# 📌 Текущий статус проекта

## v0.5-alpha

Готово:

✅ Создана архитектура проекта  
✅ Настроено Python-окружение  
✅ Telegram Bot на aiogram 3  
✅ Главное меню с кнопками  
✅ FSM состояния  
✅ YouTube downloader  
✅ SoundCloud downloader  
✅ Конвертация аудио в MP3  
✅ Отправка файлов в Telegram  
✅ Очистка временного хранилища  

---

В разработке:

⬜ YouTube video downloader  
⬜ TikTok downloader  
⬜ Instagram downloader  
⬜ Audio metadata editor  
⬜ ID3 tags management  
⬜ Cover management  
⬜ AI background removal  
⬜ Docker deployment  
⬜ Production environment  

---

# 🧩 План развития

## v0.6

Видео:

- YouTube → MP4
- TikTok → MP4
- Instagram → MP4


## v0.7

Музыкальные теги:

- чтение ID3;
- изменение метаданных;
- добавление обложек.


## v0.8

AI обработка изображений:

- удаление фона;
- подготовка изображений для обложек.


## v1.0

Production:

- Docker;
- сервер;
- PostgreSQL;
- CI/CD;
- мониторинг.

---

# 👩‍💻 Author

**Murrashovaa**

Media Toolkit Bot — Telegram инструмент для работы с медиафайлами.
