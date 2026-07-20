from aiogram.fsm.state import State, StatesGroup


class DownloadMusicState(StatesGroup):
    waiting_for_url = State()


class DownloadVideoState(StatesGroup):
    waiting_for_url = State()