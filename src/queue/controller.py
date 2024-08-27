from datetime import datetime, timedelta

from src.database.models import UltrastarSong
from .exceptions import QueueEmptyError, QueueIndexError
from .schemas import SongInQueue, ProcessedSong


class QueueController:

    def __init__(self):
        self._time_between_same_song: timedelta = timedelta(minutes=60)
        self._max_times_song_can_be_sung: int = 2
        self._queue: list[SongInQueue] = []
        self._processed_songs: list[ProcessedSong] = []
        self._queue_is_open: bool = True

    @property
    def queue(self) -> list[SongInQueue]:
        return self._queue.copy()

    @property
    def processed_songs(self) -> list[ProcessedSong]:
        return self._processed_songs.copy()

    @property
    def time_between_same_song(self) -> timedelta:
        return self._time_between_same_song

    @time_between_same_song.setter
    def time_between_same_song(self, time_between_same_song: timedelta) -> None:
        if time_between_same_song.total_seconds() < 0:
            raise ValueError("Time between songs cannot be negative")
        self._time_between_same_song = time_between_same_song

    @property
    def max_times_song_can_be_sung(self) -> int:
        return self._max_times_song_can_be_sung

    @max_times_song_can_be_sung.setter
    def max_times_song_can_be_sung(self, value: int) -> None:
        if value == 0:
            raise ValueError("Number cannot be zero")
        elif value < 0:
            raise ValueError("Number cannot be negative")
        self._max_times_song_can_be_sung = value

    def is_queue_open(self) -> bool:
        return self._queue_is_open

    def add_song_at_end(self, song: SongInQueue):
        self._queue.append(song)
        return song

    def add_song_at_index(self, song: SongInQueue, index: int):
        self._queue.insert(index, song)
        return song

    def mark_first_song_as_processed(self):
        try:
            removed: SongInQueue = self._queue.pop(0)
        except IndexError as exc:
            raise QueueEmptyError() from exc
        self._processed_songs.append(ProcessedSong(song=removed.song, processed_at=datetime.now()))
        return removed

    def mark_song_at_index_as_processed(self, index: int):
        try:
            removed: SongInQueue = self._queue.pop(index)
        except IndexError as exc:
            raise QueueEmptyError() from exc
        self._processed_songs.append(ProcessedSong(song=removed.song, processed_at=datetime.now().replace(microsecond=0)))
        return removed

    def remove_song_by_index(self, index: int):
        try:
            removed = self._queue.pop(index)
        except IndexError as exc:
            raise QueueIndexError() from exc
        return removed

    # how would somebody expect this to work?
    def move_song_from_to(self, from_index: int, to_index: int):
        try:
            moved = self._queue.pop(from_index)
        except IndexError as exc:
            raise QueueIndexError() from exc
        self._queue.insert(to_index, moved)

    def clear_queue(self) -> None:
        self._queue.clear()

    def clear_processed_songs(self) -> None:
        self._processed_songs.clear()

    def close_queue(self) -> None:
        self._queue_is_open = False

    def open_queue(self) -> None:
        self._queue_is_open = True

    def clear_queue_controller(self) -> None:
        self.clear_queue()
        self.clear_processed_songs()
        self.open_queue()

    def is_song_in_queue(self, song: UltrastarSong) -> bool:
        return song in [song_in_queue.song for song_in_queue in self._queue]

    def is_song_in_processed_songs(self, song: UltrastarSong) -> bool:
        return song in [processed_song.song for processed_song in self._processed_songs]

    def _get_processed_songs_by_song(self, song: UltrastarSong) -> list[ProcessedSong]:
        return [processed_song for processed_song in self._processed_songs if processed_song.song == song]

    def time_until_end_of_queue(self) -> timedelta:
        time_until_end = timedelta(seconds=0)
        for song_in_queue in self._queue:
            time_until_end += (song_in_queue.song.audio_duration
                               if song_in_queue.song.audio_duration is not None
                               else timedelta(seconds=0))

        return time_until_end

    def _song_last_sung_at(self, song: UltrastarSong) -> datetime | None:
        processed_songs = self._get_processed_songs_by_song(song)
        processed_songs.sort(key=lambda processed_song: processed_song.processed_at)

        return processed_songs[-1].processed_at if processed_songs else None

    def will_time_between_songs_have_passed_until_end_of_queue(self, song: UltrastarSong) -> bool:
        last_sung_at = self._song_last_sung_at(song)
        if last_sung_at is None:
            return True
        return datetime.now() + self.time_until_end_of_queue() - self._time_between_same_song > last_sung_at

    def _song_sung_x_times(self, song: UltrastarSong) -> int:
        return len(self._get_processed_songs_by_song(song))

    def has_song_been_sung_max_times(self, song: UltrastarSong) -> bool:
        return self._song_sung_x_times(song) >= self._max_times_song_can_be_sung
