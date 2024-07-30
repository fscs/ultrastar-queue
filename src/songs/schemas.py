from sqlmodel import SQLModel


class UltrastarSongBase(SQLModel):
    title: str
    artist: str
    lyrics: str | None = None

    def __str__(self):
        repr_str = ""
        for attr in self.model_fields:
            if hasattr(self, attr):
                repr_str += f"{attr}: {getattr(self, attr)}\n"
        return "UltrastarSongBase(\n"+repr_str+")"
