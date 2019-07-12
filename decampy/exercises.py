import logging
import re
from pathlib import Path
from typing import Tuple, Dict

from decampy.util import FileLines

exercise_types = {"videoexercise": "slides", "multiplechoiceexercise": "choice"}


def get_slides(lines: FileLines) -> str:
    """
    Get the string content for an output slides file.
    Args:
        lines (FileLines): All lines of the input slides file.

    Returns:
        str: content of output slides file.

    """
    content = "---\ntype: slides\n---\n\n"  # frontmatter
    within_slide = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if not within_slide and not line.startswith("##"):
            pass
        elif line.startswith("##"):
            within_slide = True
            title = f'# {" ".join(line.split()[1:])}'
            content += f"{title}\n"
        elif line.startswith("```yaml"):
            i += 1
            while not lines[i].startswith("```"):
                i += 1
        elif line.startswith("`@script"):
            content += f"Notes: {lines[i+1]}"
            i += 2
            while i < len(lines) and not lines[i].startswith("---"):
                content += f"{lines[i]}"
                i += 1
            if i < len(lines):
                content += f"---\n"
            within_slide = False
        elif line.startswith("`@"):  # unused metadata
            pass
        elif within_slide and line.startswith("---"):
            content += f"---\n"
            within_slide = False
        elif line.startswith("```{{"):  # unused metadata
            content += "```\n"
        elif within_slide:
            content += f"{line}"
        i += 1
    logging.debug(f"Done processing slide content")
    return content


def get_exercise(
    n: int, n_chapter: int, lines: FileLines, basepaths: Tuple[Path]
) -> Tuple[Dict[Path, str], FileLines]:
    """
    Create a mapping of file paths to generated file contents.

    Given the text (via lines) of exercise n of chapter n_chapter, generates not only this exercise's file(s), but also
    files for this exercise's slides, and a (partial) file to be inserted into the file of its host chapter.

    Returns both the path->content mapping and the lines following this exercise. If there is no exercise discernible
    from the lines given (for example, they are empty lines), returns ({}, []), i.e. reports that there is no mapping
    and there are no more lines.

    Args:
        n (int): The exercise number
        n_chapter (int): The chapter number.
        lines (FileLines): Each line of the input file.
        basepaths (Tuple[Path]): the input and output directories

    Returns:

    """
    basepath_in, basepath_out = basepaths
    chapter_path = basepath_out.joinpath("chapters", f"chapter{n_chapter}.md")
    processed = {chapter_path: ""}
    e_title, e_type = None, None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("##"):
            e_title = " ".join(line.split()[1:]).strip()
        elif line.startswith("---"):
            processed[chapter_path] += f"</exercise>\n"
            break
        elif line.startswith("```yaml"):
            i += 1
            while not lines[i].startswith("```"):
                if lines[i].startswith("type:"):
                    e_type_dc = lines[i].split()[1].lower()
                    if e_type_dc in exercise_types:
                        e_type = exercise_types[e_type_dc]
                    if e_type == "slides":
                        processed[
                            chapter_path
                        ] += f'<exercise id="{n}" title="{e_title}" type="{e_type}">\n'
                    else:
                        processed[
                            chapter_path
                        ] += f'<exercise id="{n}" title="{e_title}">\n'
                i += 1
        elif e_type == "slides" and line.startswith("`@projector_key`"):
            i += 1
            hash_ = lines[i].strip()
            slides_input_path = next(
                p
                for p in basepath_in.joinpath("slides").glob("*.md")
                if hash_ in str(p)
            )
            with open(slides_input_path) as f:
                slides_lines = f.readlines()
            slides_source = f"chapter{n_chapter}_{n}"
            slides_path = basepath_out.joinpath("slides", f"{slides_source}.md")
            processed[slides_path] = get_slides(slides_lines)
            processed[chapter_path] += f'<slides source="{slides_source}"></slides>\n'
        elif e_type == "choice" and line.startswith("`@possible_answers"):
            choices = []
            i += 1
            while lines[i].startswith("- "):
                choices.append({"answer": re.match(r"- (.+)\n", lines[i]).group(1)})
                i += 1
            while not lines[i].startswith("`@sct"):
                i += 1
            i += 2
            feedback = ""
            while not lines[i].startswith("```"):
                if not lines[i].startswith("Ex()"):
                    feedback += lines[i]
                else:
                    correct_index = (
                        int(
                            re.search(
                                r"has_chosen\(.*correct\s*=\s*(\d)", lines[i]
                            ).group(1)
                        )
                        - 1
                    )
                    choices[correct_index]["correct"] = True
                i += 1

            d = {"msgs": []}
            exec(feedback, d)
            for j, msg in enumerate(d["msgs"]):
                choices[j]["feedback"] = msg
            processed[chapter_path] += "<choice>\n"
            for choice in choices:
                if "correct" in choice:
                    processed[
                        chapter_path
                    ] += f'<opt text="{choice["answer"]}" correct="true">\n'
                else:
                    processed[chapter_path] += f'<opt text="{choice["answer"]}">\n'
                processed[chapter_path] += f'{choice["feedback"]}\n</opt>\n'
            processed[chapter_path] += "</choice>\n"
        elif e_type == "choice":
            processed[chapter_path] += line
        else:
            pass  # TODO: process non-slides exercise content
        i += 1

    logging.debug(f"Done processing exerise {n} or chapter {n_chapter}")
    return processed, lines[(i + 1) :]
