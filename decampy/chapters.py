import logging
import re
from pathlib import Path
from typing import Dict, Tuple

from decampy.exercises import get_exercise
from decampy.util import FileLines


def get_frontmatter(n: int, lines: FileLines) -> Tuple[str, FileLines]:
    """
    Given the input lines of chapter n, extract and format the output frontmatter block.

    Returns both the output frontmatter block and the lines following this block.

    Args:
        n (int): The chapter number.
        lines (FileLines): Lines of the input chapter

    Returns:
        Tuple[str, FileLines]: a tuple of the output frontmatter block, and the lines remaining.
    """
    frontmatter = """\
---
title: {title}
description: {description}
prev: {prev}
next: {next}
type: chapter
id: {n}
---
"""
    title = None
    description = None
    in_block = False
    next_line_i = None
    for i, line in enumerate(lines):
        if line.startswith("--"):
            if not in_block:
                in_block = True
                continue
            else:
                next_line_i = i + 1
                break
        if in_block:
            if line.startswith("title:"):
                title = re.search(r"title:(.+)", line).group(1).strip()
            elif line.startswith("description:"):
                description = re.search(r"description:(.+)", line).group(1).strip()
    return (
        frontmatter.format(
            n=n,
            prev=f"/chapter{n - 1}",
            next=f"/chapter{n + 1}",
            title=title,
            description=description,
        ),
        lines[next_line_i:],
    )


def create_chapter(n: int, lines: FileLines, basepaths: Tuple[Path]) -> Dict[Path, str]:
    """
    Given the text (via lines) of chapter n, create a mapping of file paths to generated file contents.

    Generates not only this chapter's file, but also files for this chapter's exercises and slides.

    Args:
        n (int): The chapter number.
        lines (FileLines): Each line of the input file.
        basepaths (Tuple[Path]): the input and output directories

    Returns:
        Dict[Path,str]: A mapping of intended file paths to intended file contents.

    """
    basepath_in, basepath_out = basepaths
    frontmatter, lines_remaining = get_frontmatter(n, lines)
    n_exercise = 1
    chapter_path = basepath_out.joinpath("chapters", f"chapter{n}.md")
    processed = {chapter_path: frontmatter}
    while lines_remaining:
        processed_exercise, lines_remaining = get_exercise(
            n=n_exercise, n_chapter=n, lines=lines_remaining, basepaths=basepaths
        )
        processed[chapter_path] += processed_exercise.pop(chapter_path, "")
        processed.update(processed_exercise)
        n_exercise += 1
    logging.debug(f"Done processing chapter {n}")
    return processed
