from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

QUESTION_BANK = ROOT / "bank" / "problem-bank.tex"

# Add all source qmd files that contain \useproblem{}
SOURCE_FILES = sorted((ROOT / "2023/weeks").glob("**/*_source.qmd"))

def load_problem_bank(path):
    text = path.read_text(encoding="utf-8")

    pattern = re.compile(
        r"%<\*(?P<key>[^>]+)>\s*(?P<body>.*?)\s*%</(?P=key)>",
        re.DOTALL,
    )

    problems = {}
    for match in pattern.finditer(text):
        key = match.group("key").strip()
        body = match.group("body").strip()

        # Remove LaTeX problem environment if present
        body = re.sub(r"\\begin\{problem\}\s*", "", body)
        body = re.sub(r"\s*\\end\{problem\}", "", body)

        problems[key] = body.strip()

    return problems

def replace_problems(text, problems):
    pattern = re.compile(r"\\useproblem\{([^}]+)\}")

    def repl(match):
        key = match.group(1).strip()
        if key not in problems:
            return f"**ERROR: Problem `{key}` not found in problem-bank.tex.**"
        return problems[key]

    return pattern.sub(repl, text)

def main():
    problems = load_problem_bank(QUESTION_BANK)

    for source in SOURCE_FILES:
        output = Path(str(source).replace("_source.qmd", ".qmd"))

        text = source.read_text(encoding="utf-8")
        new_text = replace_problems(text, problems)

        output.write_text(new_text, encoding="utf-8")
        print(f"Generated {output.relative_to(ROOT)}")

if __name__ == "__main__":
    main()