from pathlib import Path
from typing import Tuple, Dict

from decampy.util import FileLines


def get_exercise(
    n: int, n_chapter: int, lines: FileLines
) -> Tuple[Dict[Path, str], FileLines]:
    """
    Create a mapping of file paths to generated file contents.

    Given the text (via lines) of exercise n of chapter n_chapter, generates not only this exercise's file(s), but also
    files for this exercise's slides, and a (partial) file to be inserted into the file of its host chapter.

    Returns both the path->content mapping and the lines following this exercise. If there is no exercise discernible
    from the lines given (for example, they are empty lines), returns ({}, []), i.e. reports that there is no mapping
    and there are no more lines.

    Args:
        n:
        n_chapter:
        lines:

    Returns:

    """
    # TODO implement
    return {}, []
