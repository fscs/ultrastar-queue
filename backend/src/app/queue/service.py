from datetime import datetime, timedelta

from .config import QueueBaseSettings
from .exceptions import NotAValidNumberError
from .schemas import QueueEntry, ProcessedQueueEntry
from ..songs.models import UltrastarSong


class QueueService:

    def __init__(self):
        self._time_between_same_song: timedelta = QueueBaseSettings.TIME_BETWEEN_SAME_SONG
        self._max_times_song_can_be_sung: int = QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG
        self._queue_is_open: bool = QueueBaseSettings.QUEUE_IS_OPEN
        self._time_between_song_submissions: timedelta = QueueBaseSettings.TIME_BETWEEN_SONG_SUBMISSIONS
        self._queue: list[QueueEntry] = []
        self._processed_entries: list[ProcessedQueueEntry] = []

    @property
    def queue(self) -> list[QueueEntry]:
        return self._queue.copy()

    @property
    def processed_entries(self) -> list[ProcessedQueueEntry]:
        return self._processed_entries.copy()

    @property
    def time_between_same_song(self) -> timedelta:
        return self._time_between_same_song

    @time_between_same_song.setter
    def time_between_same_song(self, interval: timedelta) -> None:
        if interval.total_seconds() < 0:
            raise NotAValidNumberError("Time between songs cannot be negative")
        self._time_between_same_song = interval

    @property
    def max_times_song_can_be_sung(self) -> int:
        return self._max_times_song_can_be_sung

    @max_times_song_can_be_sung.setter
    def max_times_song_can_be_sung(self, value: int) -> None:
        if value == 0:
            raise NotAValidNumberError("Number cannot be zero")
        elif value < 0:
            raise NotAValidNumberError("Number cannot be negative")
        self._max_times_song_can_be_sung = value

    @property
    def time_between_song_submissions(self) -> timedelta:
        return self._time_between_song_submissions

    @time_between_song_submissions.setter
    def time_between_song_submissions(self, interval: timedelta) -> None:
        if interval.total_seconds() < 0:
            raise NotAValidNumberError("Time between song submissions cannot be negative")
        self._time_between_song_submissions = interval

    @property
    def queue_is_open(self) -> bool:
        return self._queue_is_open

    @queue_is_open.setter
    def queue_is_open(self, value: bool) -> None:
        self._queue_is_open = value

    def add_entry_at_end(self, entry: QueueEntry) -> QueueEntry:
        self._queue.append(entry)
        return entry

    def mark_entry_at_index_as_processed(self, index: int) -> QueueEntry:
        removed: QueueEntry = self._queue.pop(index)
        self._processed_entries.append(ProcessedQueueEntry(song=removed.song,
                                                           singer=removed.singer,
                                                           processed_at=datetime.now().replace(microsecond=0) +
                                                                        timedelta(hours=2)))
        return removed

    def remove_entry_by_index(self, index: int) -> QueueEntry:
        removed = self._queue.pop(index)
        return removed

    def move_entry_from_index_to_index(self, from_index: int, to_index: int) -> QueueEntry:
        if from_index < to_index:
            to_index = to_index - 1
        moved = self._queue.pop(from_index)
        self._queue.insert(to_index, moved)
        return moved

    def clear_queue(self) -> None:
        self._queue.clear()

    def clear_processed_entries(self) -> None:
        self._processed_entries.clear()

    def clear_queue_service(self) -> None:
        self.clear_queue()
        self.clear_processed_entries()
        self.queue_is_open = True

    def is_song_in_queue(self, song: UltrastarSong) -> bool:
        return song in [entry.song for entry in self._queue]

    def is_song_in_processed_entries(self, song: UltrastarSong) -> bool:
        return song in [entry.song for entry in self._processed_entries]

    def _get_processed_entries_by_song(self, song: UltrastarSong) -> list[ProcessedQueueEntry]:
        return [entry for entry in self._processed_entries if entry.song == song]

    def time_until_end_of_queue(self) -> timedelta:
        time_until_end = timedelta(seconds=0)
        for entry in self._queue:
            time_until_end += (entry.song.audio_duration
                               if entry.song.audio_duration is not None
                               else timedelta(seconds=0))

        return time_until_end

    def _song_last_sung_at(self, song: UltrastarSong) -> datetime | None:
        processed_entries = self._get_processed_entries_by_song(song)
        processed_entries.sort(key=lambda processed_entry: processed_entry.processed_at)

        return processed_entries[-1].processed_at if processed_entries else None

    def will_time_between_songs_have_passed_until_end_of_queue(self, song: UltrastarSong) -> bool:
        last_sung_at = self._song_last_sung_at(song)
        if last_sung_at is None:
            return True
        return datetime.now() + self.time_until_end_of_queue() - self._time_between_same_song > last_sung_at

    def _song_sung_x_times(self, song: UltrastarSong) -> int:
        return len(self._get_processed_entries_by_song(song))

    def has_song_been_sung_max_times(self, song: UltrastarSong) -> bool:
        return self._song_sung_x_times(song) >= self._max_times_song_can_be_sung
