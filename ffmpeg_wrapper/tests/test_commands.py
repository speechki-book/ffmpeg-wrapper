from ffmpeg_wrapper.simple import (
    concat_ffmpeg_command,
    convert_ffmpeg_command,
    duration_ffmpeg_command,
    silent_ffmpeg_command,
)


def test_concatenate_command():
    build_list = ["1.wav", "2.wav", "3.wav", "4.wav"]
    output_path = "complete_book.wav"
    background_path = "background.wav"
    background_volume = 0.3
    volume = 2.0

    test_command = """ffmpeg -y -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex "concat=n=4:v=0:a=1,volume=2.0[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest" -ac 2 complete_book.wav"""

    command = concat_ffmpeg_command(
        build_list=build_list,
        output_path=output_path,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
    )
    print(command)
    assert command == test_command


def test_convert_command():
    input_info = (
        "complete_book.wav",
        "/tmp/complete_book.wav",
        "wav",
    )
    output_info = (
        "converted_book.mp3",
        "/tmp/converted_book.mp3",
        "mp3",
    )
    bit_rate: int = 256

    test_command = (
        """ffmpeg -i /tmp/complete_book.wav -b:a 256 /tmp/converted_book.mp3"""
    )

    command = convert_ffmpeg_command(
        input_info=input_info, output_info=output_info, bit_rate=bit_rate
    )

    assert command == test_command


def test_duration_command():
    file_path: str = "/tmp/audio.wav"

    test_command = """ffprobe -i /tmp/audio.wav -show_entries format=duration -v quiet -of csv="p=0" """

    command = duration_ffmpeg_command(file_path)

    assert command == test_command


def test_silent_command():
    duration_value: float = 0.85
    output_path: str = "/tmp/pause.wav"

    test_command = (
        "ffmpeg -f lavfi -i anullsrc -t 0.850 -ar 48000 -ac 1 /tmp/pause.wav"
    )

    command = silent_ffmpeg_command(duration_value, output_path)

    assert command == test_command
