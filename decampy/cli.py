import argparse
import logging
import sys
from pathlib import Path

from decampy.chapters import create_chapter


def main():
    parser = argparse.ArgumentParser(
        description="Convert DataCamp repos to the format of ines/course-starter-python"
    )
    parser.add_argument(
        "inrepo", type=str, help="Input (DataCamp) repo with chapters and slides"
    )
    parser.add_argument(
        "outdir",
        type=str,
        help="Output directory to write subdirectories chapters/, exercises/, and slides/",
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Logging level. One of {INFO, DEBUG, WARN, ERROR} (case-insensitive).",
        default="ERROR",
    )

    args = parser.parse_args()
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log}")
    logging.basicConfig(level=numeric_level, stream=sys.stdout)

    processed = {}
    # Assumes there are fewer than ten chapters. A typical course has four chapters.
    basepath_in = Path(args.inrepo)
    chapter_paths = sorted(basepath_in.glob("chapter*.md"))
    basepath_out = Path(args.outdir)
    for i, inpath in enumerate(chapter_paths):
        n_chapter = i + 1
        with open(inpath, "r") as f:
            lines = f.readlines()
            processed.update(
                create_chapter(
                    n=n_chapter, lines=lines, basepaths=(basepath_in, basepath_out)
                )
            )
        if n_chapter == 1:
            key = basepath_out.joinpath("chapters", "chapter1.md")
            processed[key] = processed[key].replace("prev: /chapter0", "prev: null", 1)
        elif n_chapter == len(chapter_paths):
            key = basepath_out.joinpath("chapters", f"chapter{n_chapter}.md")
            processed[key] = processed[key].replace(
                f"next: /chapter{n_chapter + 1}", "next: null", 1
            )

    for outpath, content in processed.items():
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with open(outpath, "w") as f:
            f.write(content)
