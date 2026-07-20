from aiogram.fsm.state import State, StatesGroup

class DownloadMusicState(StatesGroup):
    waiting_for_url = State()


class DownloadVideoState(StatesGroup):
    waiting_for_url = State()

class TagsState(StatesGroup):
    waiting_for_audio = State()
    editing_field = State()
    editing_tags = State()
    waiting_for_cover = State()

class ImageState(StatesGroup):
    waiting_for_image = State()