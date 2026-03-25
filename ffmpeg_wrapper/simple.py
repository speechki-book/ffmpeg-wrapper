import subprocess
from subprocess import CalledProcessError
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union


class FFMPEGWrapperException(Exception):
    MESSAGE_DETAIL_LIMIT = 500

    def __init__(
        self,
        out: Optional[str] = None,
        er: Optional[str] = None,
        return_code: Optional[int] = None,
        command: Optional[Union[str, Sequence[str]]] = None,
    ):
        message = self._build_message(return_code=return_code, command=command, stderr=er)
        super().__init__(message)
        self.out = out
        self.er = er
        self.stdout = out
        self.stderr = er
        self.return_code = return_code
        self.command = command

    @classmethod
    def _clip_detail(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        clipped = value.strip()
        if not clipped:
            return None

        if len(clipped) > cls.MESSAGE_DETAIL_LIMIT:
            return f"{clipped[: cls.MESSAGE_DETAIL_LIMIT]}..."

        return clipped

    @staticmethod
    def _stringify_command(
        command: Optional[Union[str, Sequence[str]]],
    ) -> Optional[str]:
        if command is None:
            return None

        if isinstance(command, str):
            command_str = command
        else:
            command_str = " ".join(str(part) for part in command)

        command_str = command_str.strip()
        return command_str or None

    @classmethod
    def _build_message(
        cls,
        return_code: Optional[int],
        command: Optional[Union[str, Sequence[str]]],
        stderr: Optional[str],
    ) -> str:
        parts = [f"FFMPEG failed with exit code {return_code}"]

        command_str = cls._stringify_command(command)
        if command_str:
            parts.append(f"command: {command_str}")

        stderr_str = cls._clip_detail(stderr)
        if stderr_str:
            parts.append(f"stderr: {stderr_str}")

        return "; ".join(parts)


class FFMPEGWrapperParsingException(Exception):
    pass


def loudnorm_filter(use_normalization: bool, rms_level: float, peak: float, loudness_range_target: float) -> str:
    """
    Build ffmpeg filter which normalizes audio stream loudness.

    :param use_normalization: enable normalization
    :param rms_level: allowed root mean square of audio volume
    :param peak: allowed peak volume
    :param loudness_range_target: allowed range of loudness of audio volume
    :return: command for shell
    """

    if not use_normalization:
        return ""

    return f",loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target}"


def concat_command(
    build_list: List[str],
    volume: float,
    use_normalization: bool,
    rms_level: float,
    peak: float,
    loudness_range_target: float,
    is_short: bool,
) -> Tuple[List[str], str]:
    """
    Part of command for concatenate book parts to book.

    :param build_list: list book parts audio path
    :param volume: setting for audio volume
    :param use_normalization: enable normalization
    :param peak: allowed peak volume
    :param rms_level: allowed root mean square of audio volume
    :param loudness_range_target: allowed range of loudness of audio volume
    :param is_short: if flag is True then we add 30 second to beginning and after normalize delete it
    :return: - tuple 0 - list files 1 - concatenate filter
    """

    concat_files = []
    for part_path in build_list:
        concat_files.append("-i")
        concat_files.append(part_path)

    count = len(build_list)

    volume_filter = f",volume={volume:.1f}"

    loudnorm = loudnorm_filter(use_normalization, rms_level, peak, loudness_range_target)

    if is_short and loudnorm:
        concat_filter = f"concat=n={count}:v=0:a=1{volume_filter},adelay=30s{loudnorm},atrim=start=30[book]"
    else:
        concat_filter = f"concat=n={count}:v=0:a=1{volume_filter}{loudnorm}[book]"

    return concat_files, concat_filter


def background_filter(background_path: str, background_volume: float, is_normalize: bool = True) -> str:
    """
    Build ffmpeg filter which create stream with infinity stream audio from chosen file.

    :param background_path: path to source background audio
    :param background_volume: value for volume for background audio
    :param is_normalize: flag for normalize or not audio
    :return: command for shell
    """

    normalize = int(is_normalize)
    return (
        f"amovie={background_path}:loop=0,asetpts=N/SR/TB,volume={background_volume:.1f}[background];"
        f"[book][background]amix=duration=shortest:normalize={normalize}"
    )


def simple_concat_ffmpeg_command(
    build_list: List[str],
    output_path: str,
    channels: int = 2,
) -> List[str]:
    """
    Simple concatenate audios

    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :return: completed ffmpeg command for shell
    """

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
    ]

    for part_path in build_list:
        command.append("-i")
        command.append(part_path)

    command.extend(["-ac", f"{channels}", "-y", output_path])

    return command


def concat_ffmpeg_command(
    build_list: List[str],
    output_path: str,
    channels: int = 2,
    background_path: Optional[str] = None,
    background_volume: float = 1.0,
    volume: float = 1.0,
    sample_rate: int = 48000,
    use_normalization: bool = False,
    peak: float = -3.0,
    rms_level: float = -18.0,
    loudness_range_target: float = 18.0,
    is_normalize: bool = True,
    is_short: bool = False,
) -> List[str]:
    """
    Build command for ffmpeg which concatenate book parts to book and add background audio if need.

    :param sample_rate: sample rate
    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :param use_normalization: enable normalization
    :param peak: allowed peak volume
    :param rms_level: allowed root mean square of audio volume
    :param loudness_range_target: allowed range of loudness of audio volume
    :param is_normalize: flag for normalize or not audio
    :param is_short: if flag is True then we add 30 second to beginning and after normalize delete it
    :return: completed ffmpeg command for shell
    """

    if background_path:
        background = background_filter(background_path, background_volume, is_normalize)
        background = f";{background}"
        map_out = []
    else:
        background = ""
        map_out = ["-map", "[book]"]

    concat_files, concat_filter = concat_command(
        build_list,
        volume,
        use_normalization,
        rms_level,
        peak,
        loudness_range_target,
        is_short,
    )

    command = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    command.extend(concat_files)
    command.extend(["-filter_complex", f"{concat_filter}{background}"])
    command.extend(map_out)
    command.extend(["-ac", f"{channels}", "-ar", f"{sample_rate}", "-y", output_path])
    return command


def convert_ffmpeg_command(
    input_info: Tuple[str, str, str],
    output_info: Tuple[str, str, str],
    bit_rate: int,
) -> List[str]:
    """
    Build command for ffmpeg which convert from source format to selected format.

    :param input_info: tuple which contain source audio file name, path, format
    :param output_info: tuple which contain completed audio file name, path, format
    :param bit_rate: bit rate value which will be set to result audio
    :return: completed ffmpeg command for shell
    """

    input_file_name, input_file_path, input_file_format = input_info
    output_file_name, output_file_path, output_file_format = output_info

    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_file_path,
        "-ab",
        f"{bit_rate}k",
        "-y",
        output_file_path,
    ]


def duration_ffmpeg_command(file_path: str) -> List[str]:
    """
    Build command for ffmpeg which return audio file duration.

    :param file_path: path to audio file
    :return: completed ffmpeg command for shell
    """

    return [
        "ffprobe",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        file_path,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "csv=p=0",
    ]


def silent_ffmpeg_command(duration_value: float, output_path: str) -> List[str]:
    """
    Build command for ffmpeg which create silent audio with selected duration.

    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: completed ffmpeg command for shell
    """

    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "anullsrc",
        "-t",
        f"{duration_value:.3f}",
        "-ar",
        "48000",
        "-ac",
        "1",
        "-y",
        output_path,
    ]


def normalize_ffmpeg_command(
    input_path: str,
    output_path: str,
    peak: float,
    rms_level: float,
    loudness_range_target: float,
    sampling_frequency: int,
) -> List[str]:
    """
    Build command for ffmpeg which normalizes audio with selected level

    :param input_path: path where input file is
    :param output_path: path to output file
    :param peak: value of peak volume
    :param rms_level: value of root mean square of loudness
    :param loudness_range_target: value of target loudness range
    :param sampling_frequency: frequency of sampling in Hz, for example 44100
    :return: completed ffmpeg command for shell
    """

    return [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_path,
        "-af",
        f"loudnorm=I={rms_level}:TP={peak}:LRA={loudness_range_target}",
        "-ar",
        f"{sampling_frequency}",
        output_path,
    ]


def volume_detect_command(path_to_file: str) -> List[str]:
    return [
        "ffmpeg",
        "-i",
        path_to_file,
        "-af",
        "volumedetect",
        "-vn",
        "-sn",
        "-dn",
        "-f",
        "null",
        "/dev/null",
    ]


def execute_command(command_func: Callable, *args, **kwargs) -> Tuple[int, str, str]:
    """
    Executor for all commands. Execute command in subprocess and wait complete task.

    :param command_func: function will be executed in subprocess
    :param args: values which transferred to command_func
    :param kwargs: values which transferred to command_func
    :return: tuple which contain return code, output and error message
    """
    cwd = kwargs.pop("cwd", None)
    command = command_func(*args, **kwargs)

    try:
        process_handle = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=cwd,
        )
        out, err = process_handle.communicate()
        out_str: str = out.decode("utf-8", "ignore")
        err_str: str = err.decode("utf-8", "ignore")
        status = process_handle.returncode
    except CalledProcessError as cpe:
        stdout = getattr(cpe, "stdout", None)
        stderr = getattr(cpe, "stderr", None)
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "ignore")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "ignore")
        raise FFMPEGWrapperException(out=stdout, er=stderr, return_code=cpe.returncode, command=command)
    except OSError as exc:
        raise FFMPEGWrapperException(er=str(exc), return_code=getattr(exc, "errno", None), command=command) from exc

    return status, out_str, err_str


def concatenate(
    build_list: List[str],
    output_path: str,
    channels: int = 2,
    background_path: Optional[str] = None,
    background_volume: float = 1.0,
    volume: float = 1.0,
    sample_rate: int = 48000,
    use_normalization: bool = False,
    peak: float = -3.0,
    rms_level: float = -18.0,
    loudness_range_target: float = 18.0,
    is_normalize: bool = True,
    is_short: bool = False,
) -> Tuple[int, str, str]:
    """

    :param sample_rate: sample rate
    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :param use_normalization: enable normalization
    :param peak: value of peak volume of concatenated audio
    :param rms_level: value of root mean square of loduness in concatenated audio
    :param loudness_range_target: value of target loudness range
    :param is_normalize: flag for normalize or not audio
    :param is_short: if flag is True then we add 30 second to beginning and after normalize delete it
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
        sample_rate=sample_rate,
        use_normalization=use_normalization,
        peak=peak,
        rms_level=rms_level,
        loudness_range_target=loudness_range_target,
        is_normalize=is_normalize,
        is_short=is_short,
    )
    status, file_path, er = res
    if status:
        command = concat_ffmpeg_command(
            build_list=build_list,
            output_path=output_path,
            channels=channels,
            background_path=background_path,
            background_volume=background_volume,
            volume=volume,
            sample_rate=sample_rate,
            use_normalization=use_normalization,
            peak=peak,
            rms_level=rms_level,
            loudness_range_target=loudness_range_target,
            is_normalize=is_normalize,
            is_short=is_short,
        )
        raise FFMPEGWrapperException(file_path, er, return_code=status, command=command)

    return status, file_path, er


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
        command = convert_ffmpeg_command(input_info=input_info, output_info=output_info, bit_rate=bit_rate)
        raise FFMPEGWrapperException(out, er, return_code=status, command=command)

    return status, out, er


def duration(file_path: str) -> float:
    """
    Return duration for selected audio file in seconds.

    :param file_path: path to audio file
    :return: if command success complete then return audio duration else return None
    """

    res: Tuple[int, str, str] = execute_command(duration_ffmpeg_command, file_path=file_path)

    status, out, er = res

    if status:
        command = duration_ffmpeg_command(file_path)
        raise FFMPEGWrapperException(out, er, return_code=status, command=command)

    try:
        return float(out)
    except ValueError:
        return 0.0


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
        command = silent_ffmpeg_command(duration_value, output_path)
        raise FFMPEGWrapperException(out, er, return_code=status, command=command)

    return status, out, er


def volume_detect(path_to_file: str) -> Dict[str, float]:
    status, out, er = execute_command(volume_detect_command, path_to_file=path_to_file)
    if status:
        command = volume_detect_command(path_to_file=path_to_file)
        raise FFMPEGWrapperException(out, er, return_code=status, command=command)

    rows = (r for r in er.split("\n") if "Parsed_volumedetect" in r)
    result = {}
    try:
        for r in rows:
            if "mean_volume:" in r:
                # line looks like '[Parsed_volumedetect_0 @ 0x153e3a880] mean_volume: -16.7 dB'
                result["root_mean_square"] = float(r.split(" ")[-2])
            if "max_volume:" in r:
                # line looks like '[Parsed_volumedetect_0 @ 0x153e3a880] max_volume: -0.0 dB'
                result["max_volume"] = float(r.split(" ")[-2])
    except (
        KeyError,
        IndexError,
        AttributeError,
    ) as e:
        raise FFMPEGWrapperParsingException("Error occurred while parsing FFMPEG output") from e

    return result
