def format_metadata(data: dict) -> str:
    return (
        "🎧 <b>Информация о треке</b>\n\n"
        f"🎵 <b>Название:</b> "
        f"{data.get('title') or 'Не указано'}\n"
        f"👤 <b>Исполнитель:</b> "
        f"{data.get('artist') or 'Не указан'}\n"
        f"💿 <b>Альбом:</b> "
        f"{data.get('album') or 'Не указан'}\n"
        f"📅 <b>Год:</b> "
        f"{data.get('year') or 'Не указан'}\n"
        f"🎸 <b>Жанр:</b> "
        f"{data.get('genre') or 'Не указан'}\n\n"
        f"🖼 <b>Обложка:</b> "
        f"{'Загружена' if data.get('cover') else 'Отсутствует'}"
    )
