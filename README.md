Wrapper for FFMPEG. This is MVP. At this moment wrapper can concatenate audio, create silent audio, get audio duration, convert audio.


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
---

## API Reference

### Concatenate

```python
from ffmpeg_wrapper import concatenate
from typing import List

build_list: List[str] = ["1.wav", "2.wav", "3.wav", "4.wav"]
output_path: str = "complete_book.wav"
background_path: str = "background.wav"
background_volume: float = 0.3
volume: float = 2.0


status, out, er = concatenate(
    build_list=build_list,
    output_path=output_path,
    background_path=background_path,
    volume=volume
)
```

Executed command:

```shell script
ffmpeg -y -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex \
concat=n=4:v=0:a=1,volume=2.0[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest \
-ac 2 complete_book.wav
```

---

### Convert

```python
from ffmpeg_wrapper import convert
from typing import Tuple

input_info: Tuple[str, str, str] = ("complete_book.wav", "/tmp/complete_book.wav", "wav",)
output_info: Tuple[str, str, str] = ("converted_book.mp3", "/tmp/converted_book.mp3", "mp3",)
bit_rate: int = 256

status, out, er = convert(
    input_info,
    output_info,
    bit_rate
)
```

Executed command:

```shell script
ffmpeg -i /tmp/complete_book.wav -b:a 256 /tmp/converted_book.mp3
```


---


### Silent Audio

```python
from ffmpeg_wrapper import silent

duration_value: float = 0.85
output_path: str = "/tmp/pause.wav"

status, out, er = silent(duration_value, output_path)
```

Executed command:

```shell script
ffmpeg -f lavfi -i anullsrc -t 0.850 -ar 48000 -ac 1 /tmp/pause.wav
```


---

### Duration Audio

```python
from ffmpeg_wrapper import duration

file_path: str = "/tmp/audio.wav"

duration = duration(file_path)
```

Executed command:

```shell script
ffprobe -i /tmp/audio.wav -show_entries format=duration -v quiet -of csv="p=0" 
```
