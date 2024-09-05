from datetime import timedelta


class QueueBaseSettings:
    TIME_BETWEEN_SAME_SONG: timedelta = timedelta(minutes=60)
    MAX_TIMES_SONG_CAN_BE_SUNG: int = 2
    QUEUE_IS_OPEN: bool = True
    TIME_BETWEEN_SONG_SUBMISSIONS: timedelta = timedelta(minutes=60)
