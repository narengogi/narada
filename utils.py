from pathlib import Path

def get_directory(path, directory_name):
    folder_path = Path(path + directory_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path

def escape_quotes(string):
    string = string.replace("'", " ")
    string = string.replace('"', ' ')
    return string 