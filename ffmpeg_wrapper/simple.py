import subprocess
from subprocess import CalledProcessError
from typing import List, Optional, Tuple, Callable


class FFMPEGWrapperException(Exception):
    def __init__(
        self,
        out: Optional[str] = None,
        er: Optional[str] = None,
        return_code: Optional[int] = None,
    ):
        msg_args = [f"FFMPEG failed with exit code {return_code}"]
        super().__init__(self, *msg_args)
        self.out = out
        self.er = er


def concat_command(
    build_list: List[str], volume: float
) -> Tuple[List[str], str]:
    """
    Part of command for concatenate book parts to book.

    :param build_list: list book parts audio path
    :param volume: setting for audio volume
    :return: - tuple 0 - list files 1 - concatenate filter
    """

    concat_files = [f"-i {part_path}" for part_path in build_list]
    count = len(build_list)

    volume_filter = f",volume={volume:.1f}"

    concat_filter = f"concat=n={count}:v=0:a=1{volume_filter}[book]"

    return concat_files, concat_filter


def background_filter(background_path: str, background_volume: float) -> str:
    """
    Build ffmpeg filter which create stream with infinity stream audio from chosen file.

    :param background_path: path to source background audio
    :param background_volume: value for volume for background audio
    :return: command for shell
    """

    return (
        f"amovie={background_path}:loop=0,asetpts=N/SR/TB,volume={background_volume:.1f}[background];"
        f"[book][background]amix=duration=shortest"
    )


def concat_ffmpeg_command(
    build_list: List[str],
    output_path: str,
    channels: int = 2,
    background_path: Optional[str] = None,
    background_volume: float = 1.0,
    volume: float = 1.0,
) -> str:
    """
    Build command for ffmpeg which concatenate book parts to book and add background audio if need.

    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :return: completed ffmpeg command for shell
    """

    concat_files, concat_filter = concat_command(build_list, volume)
    if background_path:
        background = background_filter(background_path, background_volume)
        background = f";{background}"
    else:
        background = ""

    command = " ".join(
        ["ffmpeg", "-y"]
        + concat_files
        + [
            "-filter_complex",
            f'"{concat_filter}{background}"',
            "-ac",
            f"{channels}",
            output_path,
        ]
    )

    return command


def convert_ffmpeg_command(
    input_info: Tuple[str, str, str],
    output_info: Tuple[str, str, str],
    bit_rate: int,
) -> str:
    """
    Build command for ffmpeg which convert from source format to selected format.

    :param input_info: tuple which contain source audio file name, path, format
    :param output_info: tuple which contain completed audio file name, path, format
    :param bit_rate: bit rate value which will be set to result audio
    :return: completed ffmpeg command for shell
    """

    input_file_name, input_file_path, input_file_format = input_info
    output_file_name, output_file_path, output_file_format = output_info

    command = [
        "ffmpeg",
        "-i",
        input_file_path,
        "-b:a",
        f"{bit_rate}",
        output_file_path,
    ]
    return " ".join(command)


def duration_ffmpeg_command(file_path: str) -> str:
    """
    Build command for ffmpeg which return audio file duration.

    :param file_path: path to audio file
    :return: completed ffmpeg command for shell
    """

    return f"""ffprobe -i {file_path} -show_entries format=duration -v quiet -of csv="p=0" """


def silent_ffmpeg_command(duration_value: float, output_path: str) -> str:
    """
    Build command for ffmpeg which create silent audio with selected duration.

    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: completed ffmpeg command for shell
    """

    return f"ffmpeg -f lavfi -i anullsrc -t {duration_value:.3f} -ar 48000 -ac 1 {output_path}"


def execute_command(
    command_func: Callable, *args, **kwargs
) -> Tuple[int, str, str]:
    """
    Executor for all commands. Execute command in subprocess and wait complete task.

    :param command_func: function will be executed in subprocess
    :param args: values which transferred to command_func
    :param kwargs: values which transferred to command_func
    :return: tuple which contain return code, output and error message
    """
    try:
        process_handle = subprocess.Popen(
            command_func(*args, **kwargs),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        out, err = process_handle.communicate()
        out_str: str = out.decode("utf-8")
        err_str: str = err.decode("utf-8")
        status = process_handle.returncode
    except CalledProcessError as cpe:
        raise FFMPEGWrapperException(return_code=cpe.returncode)

    return status, out_str, err_str


def concatenate(
    build_list: List[str],
    output_path: str,
    channels: int = 2,
    background_path: Optional[str] = None,
    background_volume: Optional[float] = None,
    volume: Optional[float] = None,
) -> Tuple[int, str, str]:
    """

    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :return: tuple which contain return code, output and error message
    """

    res: Tuple[int, str, str] = execute_command(
        concat_ffmpeg_command,
        build_list=build_list,
        output_path=output_path,
        channels=channels,
        background_path=background_path,
        background_volume=background_volume,
        volume=volume,
    )

    status, out, er = res

    if status:
        raise FFMPEGWrapperException(out, er, return_code=status)

    return status, out, er


def convert(
    input_info: Tuple[str, str, str],
    output_info: Tuple[str, str, str],
    bit_rate: int,
) -> Tuple[int, str, str]:
    """
    Convert audio to chosen format with selected bit rate.

    :param input_info: tuple with info about completed book (file_name, file_path, file_format,)
    :param output_info: tuple with info about completed book after convert (file_name, file_path, file_format,)
    :param bit_rate: selected bit rate value
    :return: tuple which contain return code, output and error message
    """

    res: Tuple[int, str, str] = execute_command(
        convert_ffmpeg_command,
        input_info=input_info,
        output_info=output_info,
        bit_rate=bit_rate,
    )

    status, out, er = res

    if status:
        raise FFMPEGWrapperException(out, er, return_code=status)

    return status, out, er


def duration(file_path: str) -> float:
    """
    Return duration for selected audio file in seconds.

    :param file_path: path to audio file
    :return: if command success complete then return audio duration else return None
    """

    res: Tuple[int, str, str] = execute_command(
        duration_ffmpeg_command, file_path=file_path
    )

    status, out, er = res

    if status:
        raise FFMPEGWrapperException(out, er, return_code=status)

    return float(out)


def silent(duration_value: float, output_path: str) -> Tuple[int, str, str]:
    """
    Create silent audio with selected duration.

    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: tuple which contain return code, output and error message
    """

    res: Tuple[int, str, str] = execute_command(
        silent_ffmpeg_command,
        duration_value=duration_value,
        output_path=output_path,
    )

    status, out, er = res

    if status:
        raise FFMPEGWrapperException(out, er, return_code=status)

    return status, out, er
