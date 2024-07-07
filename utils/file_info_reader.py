import os
from pathlib import Path
from datetime import datetime

from pathlib import Path


def get_file_stats(file_path: str | Path) -> os.stat_result:
    """
    Get the statistics of a file.

    Parameter:
        file_path (str): The path to the file.

    Returns:
        os.stat_result: The statistics of the file.

    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    file_stats = file_path.stat()
    return file_stats


def get_creation_time_from_file_stats(file_stats: os.stat_result) -> float:
    """
    Get the creation time from the file stats.

    Parameter:
        file_stats (os.stat_result): The file stats object.

    Returns:
        float: The creation time of the file.
    """
    creation_time = file_stats.st_mtime
    return creation_time


def convert_timestamp_to_readable(timestamp: float) -> str:
    """
    Convert a float timestamp to a readable datetime string.
    
    Parameter:
        timestamp (float): The float timestamp to convert.

    Returns:
        str: Readable datetime string in the format YYYY-MM-DD HH:MM:SS.
    """
    readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    return readable_date


if __name__ == "__main__":
    file_path = Path('discord1.mp3')

    if not file_path.exists():
        file_path = Path('test_fake_file')
        file_path.touch()

    file_stats = get_file_stats(file_path)
    creation_time = get_creation_time_from_file_stats(file_stats)
    readable_creation_time = convert_timestamp_to_readable(creation_time)
    
    print(f"file_stats: {file_stats}")
    print(f"creation_time: {creation_time}")
    print(f"readable_creation_time: {readable_creation_time}")