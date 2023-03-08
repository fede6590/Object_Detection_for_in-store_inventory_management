import os

def walkdir(folder):
    """
    Walk through all the files in a directory and its subfolders.
    Parameters
    ----------
    folder : str
        Path to the folder you want to walk.
    Returns
    -------
        For each file found, yields a tuple having the path to the file
        and the file name.
    """
    for dirpath, _, files in os.walk(folder):
        for filename in files:
            yield (dirpath, filename)
