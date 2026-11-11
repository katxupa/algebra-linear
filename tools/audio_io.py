"""Safe OGG writing for the tools.

libsndfile's Vorbis encoder crashes (stack overflow, no error message) when a long clip is
written in one call, so audio is always written in small blocks.
"""
import soundfile as sf

BLOCK = 4096


def write_audio(path: str, data, rate: int, fmt: str = "OGG") -> None:
    subtype = "VORBIS" if fmt == "OGG" else None
    channels = 1 if data.ndim == 1 else data.shape[1]
    with sf.SoundFile(path, "w", rate, channels, format=fmt, subtype=subtype) as f:
        for i in range(0, len(data), BLOCK):
            f.write(data[i:i + BLOCK])
