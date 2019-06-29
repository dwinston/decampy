import argparse
import re
from pathlib import Path

from decampy.chapters import create_chapter


def main():
    parser = argparse.ArgumentParser(
        description="Converts DataCamp repos to the format of https://github.com/ines/course-starter-python"
    )
    parser.add_argument(
        "inrepo", type=str, help="Input (DataCamp) repo with chapters and slides"
    )
    parser.add_argument(
        "outdir",
        type=str,
        help="Output directory to write subdirectories chapters/, exercises/, and slides/",
    )

    args = parser.parse_args()

    processed = {}
    # Assumes there are fewer than ten chapters. A typical course has four chapters.
    chapter_paths = sorted(Path(args.inrepo).glob("chapter*.md"))
    basepath = Path(args.outdir)
    for i, inpath in enumerate(chapter_paths):
        n_chapter = i + 1
        with open(inpath, "r") as f:
            lines = f.readlines()
            processed.update(
                create_chapter(n=n_chapter, lines=lines, basepath=basepath)
            )
        if n_chapter == 1:
            key = basepath.joinpath("chapters", "chapter1.md")
            processed[key] = processed[key].replace("prev: /chapter0", "prev: null", 1)
        elif n_chapter == len(chapter_paths):
            key = basepath.joinpath("chapters", f"chapter{n_chapter}.md")
            processed[key] = processed[key].replace(
                f"next: /chapter{n_chapter + 1}", "next: null", 1
            )

    for outpath, content in processed.items():
        print(f"{outpath}:\n{content}")
    #    with open(outpath, "w") as f:
    #        f.write(content)
