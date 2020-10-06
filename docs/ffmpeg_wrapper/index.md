Module ffmpeg_wrapper
=====================

Sub-modules
-----------
* ffmpeg_wrapper.simple
* ffmpeg_wrapper.tests

Functions
---------

    
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

    
`duration(file_path: str) ‑> float`
:   Return duration for selected audio file in seconds.
    
    :param file_path: path to audio file
    :return: if command success complete then return audio duration else return None

    
`silent(duration_value: float, output_path: str) ‑> Tuple[int, str, str]`
:   Create silent audio with selected duration.
    
    :param duration_value: duration for silent audio
    :param output_path: path to result
    :return: tuple which contain return code, output and error message