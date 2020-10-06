Module ffmpeg_wrapper.simple
============================

Functions
---------

    
`background_filter(background_path: str, background_volume: float) ‑> str`
:   Build ffmpeg filter which create stream with infinity stream audio from chosen file.
    
    :param background_path: path to source background audio
    :param background_volume: value for volume for background audio
    :return: command for shell

    
`concat_command(build_list: List[str], volume: float) ‑> Tuple[List[str], str]`
:   Part of command for concatenate book parts to book.
    
    :param build_list: list book parts audio path
    :param volume: setting for audio volume
    :return: - tuple 0 - list files 1 - concatenate filter

    
`concat_ffmpeg_command(build_list: List[str], output_path: str, channels: int = 2, background_path: Union[str, NoneType] = None, background_volume: float = 1.0, volume: float = 1.0) ‑> str`
:   Build command for ffmpeg which concatenate book parts to book and add background audio if need.
    
    :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :return: completed ffmpeg command for shell

    
`concatenate(build_list: List[str], output_path: str, channels: int = 2, background_path: Union[str, NoneType] = None, background_volume: Union[float, NoneType] = None, volume: Union[float, NoneType] = None) ‑> Tuple[int, str, str]`
:   :param build_list: list book parts audio path
    :param output_path: path to completed audio
    :param channels: the number of channels for the completed audio
    :param background_path: path to background audio
    :param background_volume: value for volume for background audio
    :param volume: value for volume for main audio
    :return: tuple which contain return code, output and error message

    
`convert(input_info: Tuple[str, str, str], output_info: Tuple[str, str, str], bit_rate: int) ‑> Tuple[int, str, str]`
:   Convert audio to chosen format with selected bit rate.
    
    :param input_info: tuple with info about completed book (file_name, file_path, file_format,)
    :param output_info: tuple with info about completed book after convert (file_name, file_path, file_format,)
    :param bit_rate: selected bit rate value
    :return: tuple which contain return code, output and error message

    
`convert_ffmpeg_command(input_info: Tuple[str, str, str], output_info: Tuple[str, str, str], bit_rate: int) ‑> str`
:   Build command for ffmpeg which convert from source format to selected format.
    
    :param input_info: tuple which contain source audio file name, path, format
    :param output_info: tuple which contain completed audio file name, path, format
    :param bit_rate: bit rate value which will be set to result audio
    :return: completed ffmpeg command for shell

    
`duration(file_path: str) ‑> float`
:   Return duration for selected audio file in seconds.
    
    :param file_path: path to audio file
    :return: if command success complete then return audio duration else return None

    
`duration_ffmpeg_command(file_path: str) ‑> str`
:   Build command for ffmpeg which return audio file duration.
    
    :param file_path: path to audio file
    :return: completed ffmpeg command for shell

    
`execute_command(command_func: Callable, *args, **kwargs) ‑> Tuple[int, str, str]`
:   Executor for all commands. Execute command in subprocess and wait complete task.
    
    :param command_func: function will be executed in subprocess
    :param args: values which transferred to command_func
    :param kwargs: values which transferred to command_func
    :return: tuple which contain return code, output and error message

    
`silent(duration_value: float, output_path: str) ‑> Tuple[int, str, str]`
:   Create silent audio with selected duration.
    
    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: tuple which contain return code, output and error message

    
`silent_ffmpeg_command(duration_value: float, output_path: str) ‑> str`
:   Build command for ffmpeg which create silent audio with selected duration.
    
    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: completed ffmpeg command for shell

Classes
-------

`FFMPEGWrapperException(out: Union[str, NoneType] = None, er: Union[str, NoneType] = None, return_code: Union[int, NoneType] = None)`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException