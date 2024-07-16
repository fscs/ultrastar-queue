from .schemas import SongInQueue


class QueueClosedError(Exception):

    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(self.msg)


class QueueController:

    def __init__(self):
        self._queue: list[SongInQueue] = []
        self._processed_songs: list[SongInQueue] = []
        self._queue_is_open: bool = True

    def get_queue(self) -> list[SongInQueue]:
        return self._queue.copy()

    def get_processed_songs(self) -> list[SongInQueue]:
        return self._processed_songs.copy()

    def add_song_at_end(self, song: SongInQueue):
        if not self._queue_is_open:
            raise QueueClosedError("Queue is closed. Can't add any more songs.")
        self._queue.append(song)
        return song

    def add_song_at_index(self, song: SongInQueue, index: int):
        if not self._queue_is_open:
            raise QueueClosedError("Queue is closed. Can't add any more songs.")
        self._queue.insert(index, song)
        return song

    def mark_first_song_as_processed(self):
        try:
            removed = self._queue.pop(0)
        except IndexError:
            raise IndexError("Queue is empty")
        self._processed_songs.append(removed)
        return removed

    def remove_song_by_index(self, index: int):
        try:
            removed = self._queue.pop(index)
        except IndexError:
            raise IndexError
        return removed

    def move_song_from_to(self, from_index: int, to_index: int):
        try:
            moved = self._queue.pop(from_index)
        except IndexError:
            raise IndexError
        self._queue.insert(to_index, moved)

    def clear_queue(self) -> None:
        self._queue.clear()

    def close_queue(self) -> None:
        self._queue_is_open = False

    def open_queue(self) -> None:
        self._queue_is_open = True
