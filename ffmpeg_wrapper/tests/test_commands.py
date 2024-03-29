from ffmpeg_wrapper.simple import (
    concat_ffmpeg_command,
    convert_ffmpeg_command,
    duration_ffmpeg_command,
    silent_ffmpeg_command,
    normalize_ffmpeg_command,
)


BUILD_LIST = ["1.wav", "2.wav", "3.wav", "4.wav"]
OUTPUT_PATH = "complete_book.wav"


def test_concatenate_command():
    background_path = "background.wav"
    background_volume = 0.3
    volume = 2.0

    test_command = """ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=2.0[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest:normalize=1 -ac 2 -ar 48000 -y complete_book.wav"""

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
    )

    assert " ".join(command) == test_command


def test_short_concatenate_command():
    background_path = "background.wav"
    background_volume = 0.3
    volume = 2.0

    test_command = """ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=2.0[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest:normalize=1 -ac 2 -ar 48000 -y complete_book.wav"""

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
        is_short=True,
    )

    assert " ".join(command) == test_command


def test_concatenate_loudnorm_command():
    background_path = "background.wav"
    background_volume = 0.3
    volume = 2.0
    use_normalization = True
    peak = -4
    rms_level = -20
    loudness_range_target = -20

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
        use_normalization=use_normalization,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
    )

    test_command = f"""ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=2.0,loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target}[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest:normalize=1 -ac 2 -ar 48000 -y complete_book.wav"""

    assert " ".join(command) == test_command


def test_short_concatenate_loudnorm_command():
    background_path = "background.wav"
    background_volume = 0.3
    volume = 2.0
    use_normalization = True
    peak = -4
    rms_level = -20
    loudness_range_target = -20

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
        use_normalization=use_normalization,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
        is_short=True,
    )

    test_command = f"""ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=2.0,adelay=30s,loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target},atrim=start=30[book];amovie=background.wav:loop=0,asetpts=N/SR/TB,volume=0.3[background];[book][background]amix=duration=shortest:normalize=1 -ac 2 -ar 48000 -y complete_book.wav"""

    assert " ".join(command) == test_command


def test_simple_concatenate_command():
    use_normalization = True
    peak = -4
    rms_level = -20
    loudness_range_target = -20

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        use_normalization=use_normalization,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
    )

    test_command = f"""ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=1.0,loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target}[book] -map [book] -ac 2 -ar 48000 -y complete_book.wav"""
    assert " ".join(command) == test_command


def test_short_simple_concatenate_command():
    use_normalization = True
    peak = -4
    rms_level = -20
    loudness_range_target = -20

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        use_normalization=use_normalization,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
        is_short=True,
    )

    test_command = f"""ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=1.0,adelay=30s,loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target},atrim=start=30[book] -map [book] -ac 2 -ar 48000 -y complete_book.wav"""
    assert " ".join(command) == test_command


def test_simple_concatenate_loudnorm_command():

    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
    )

    test_command = """ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=1.0[book] -map [book] -ac 2 -ar 48000 -y complete_book.wav"""

    assert " ".join(command) == test_command


def test_short_simple_concatenate_loudnorm_command():
    command = concat_ffmpeg_command(
        build_list=BUILD_LIST,
        output_path=OUTPUT_PATH,
        is_short=True,
    )

    test_command = """ffmpeg -hide_banner -loglevel error -i 1.wav -i 2.wav -i 3.wav -i 4.wav -filter_complex concat=n=4:v=0:a=1,volume=1.0[book] -map [book] -ac 2 -ar 48000 -y complete_book.wav"""

    assert " ".join(command) == test_command


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
        """ffmpeg -hide_banner -loglevel error -i /tmp/complete_book.wav -ab 256k -y /tmp/converted_book.mp3"""
    )

    command = convert_ffmpeg_command(input_info=input_info, output_info=output_info, bit_rate=bit_rate)

    assert " ".join(command) == test_command


def test_duration_command():
    file_path: str = "/tmp/audio.wav"

    test_command = (
        "ffprobe -hide_banner -loglevel error -i /tmp/audio.wav -show_entries format=duration -v quiet -of csv=p=0"
    )

    command = duration_ffmpeg_command(file_path)

    assert " ".join(command) == test_command


def test_silent_command():
    duration_value: float = 0.85
    output_path: str = "/tmp/pause.wav"

    test_command = (
        "ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc -t 0.850 -ar 48000 -ac 1 -y /tmp/pause.wav"
    )

    command = silent_ffmpeg_command(duration_value, output_path)

    assert " ".join(command) == test_command


def test_normalize_command():
    input_path = "a.wav"
    output_path = "b.wav"
    peak = -3.0
    rms_level = -18.0
    loudness_range_target = 18
    sampling_frequency = 44100

    command = normalize_ffmpeg_command(
        input_path=input_path,
        output_path=output_path,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
        sampling_frequency=sampling_frequency,
    )

    expected_command = (
        "ffmpeg -hide_banner -loglevel error -i a.wav -af loudnorm=I=-18.0:TP=-3.0:LRA=18 -ar 44100 b.wav"
    )

    assert " ".join(command) == expected_command
