"""Generate concise Markdown documentation for Jupyter notebooks."""

import ast
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

NOTEBOOKS_DIR = ROOT / "notebooks"
DOCS_DIR = ROOT / "docs"
PACKAGE_DIR = ROOT / "src" / "multimodal_analysis"


def read_notebook(notebook_path: Path) -> list[dict]:
    """Read notebook cells."""
    with notebook_path.open("r", encoding="utf-8") as file:
        return json.load(file).get("cells", [])


def extract_markdown_cells(cells: list[dict]) -> list[str]:
    """Extract non-empty Markdown cells."""
    return [
        "".join(cell.get("source", [])).strip()
        for cell in cells
        if cell.get("cell_type") == "markdown"
        and "".join(cell.get("source", [])).strip()
    ]


def extract_headings(markdown_cells: list[str]) -> list[tuple[int, str]]:
    """Extract Markdown headings."""
    headings = []

    for cell in markdown_cells:
        for line in cell.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+)", line)

            if match:
                headings.append(
                    (len(match.group(1)), match.group(2).strip())
                )

    return headings


def find_function(
    function_name: str,
) -> tuple[Path, ast.FunctionDef | ast.AsyncFunctionDef] | None:
    """Find a function definition in the package."""
    for python_file in PACKAGE_DIR.rglob("*.py"):
        try:
            tree = ast.parse(
                python_file.read_text(encoding="utf-8")
            )
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in ast.walk(tree):
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ) and node.name == function_name:
                return python_file, node

    return None


def extract_used_functions(cells: list[dict]) -> set[str]:
    """Find package functions called by a notebook."""
    functions = set()

    for cell in cells:
        if cell.get("cell_type") != "code":
            continue

        source = "".join(cell.get("source", []))

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr
            else:
                continue

            if find_function(function_name) is not None:
                functions.add(function_name)

    return functions


def extract_aim(markdown_cells: list[str]) -> str:
    """Extract the notebook's Aim section."""
    for cell in markdown_cells:
        match = re.search(
            r"^##\s+Aim\s*\n(.*?)(?=^##\s|\Z)",
            cell,
            flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return "No `## Aim` section was found."


def render_structure(
    headings: list[tuple[int, str]],
) -> str:
    """Render notebook headings as a nested list."""
    if not headings:
        return "No Markdown headings were found."

    return "\n".join(
        f"{'  ' * (level - 1)}- {title}"
        for level, title in headings
    )


def format_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    """Create a readable function signature."""
    arguments = []

    positional = node.args.posonlyargs + node.args.args

    defaults = (
        [None] * (len(positional) - len(node.args.defaults))
        + list(node.args.defaults)
    )

    for argument, default in zip(positional, defaults):
        if default is None:
            arguments.append(argument.arg)
        else:
            arguments.append(
                f"{argument.arg}={ast.unparse(default)}"
            )

    if node.args.vararg:
        arguments.append(f"*{node.args.vararg.arg}")

    for argument, default in zip(
        node.args.kwonlyargs,
        node.args.kw_defaults,
    ):
        if default is None:
            arguments.append(argument.arg)
        else:
            arguments.append(
                f"{argument.arg}={ast.unparse(default)}"
            )

    if node.args.kwarg:
        arguments.append(f"**{node.args.kwarg.arg}")

    return f"{node.name}({', '.join(arguments)})"


def format_function_documentation(
    function_name: str,
) -> str:
    """Create concise documentation for a function."""
    result = find_function(function_name)

    if result is None:
        return ""

    file_path, node = result

    docstring = ast.get_docstring(node)

    relative_path = file_path.relative_to(ROOT)
    signature = format_signature(node)

    lines = [
        f"### `{signature}`",
        "",
        f"**Defined in:** `{relative_path}`",
        "",
    ]

    if docstring:
        lines.extend(
            [
                docstring,
                "",
            ]
        )

    return "\n".join(lines)


def generate_documentation(
    notebook_path: Path,
) -> str:
    """Generate documentation for one notebook."""
    cells = read_notebook(notebook_path)

    markdown_cells = extract_markdown_cells(cells)
    headings = extract_headings(markdown_cells)
    functions = extract_used_functions(cells)
    aim = extract_aim(markdown_cells)

    lines = [
        f"# {notebook_path.stem}",
        "",
        (
            f"**Notebook:** "
            f"[`{notebook_path.name}]"
            f"(../notebooks/{notebook_path.name})"
        ),
        "",
        "## Aim",
        "",
        aim,
        "",
        "## Notebook structure",
        "",
        render_structure(headings),
        "",
        "## Functions used",
        "",
    ]

    if not functions:
        lines.append(
            "No `multimodal_analysis` package functions detected."
        )
    else:
        for function_name in sorted(functions):
            documentation = format_function_documentation(
                function_name
            )

            if documentation:
                lines.append(documentation)

    return "\n".join(lines).strip() + "\n"


def get_changed_files() -> list[Path]:
    """Return files changed by the current push."""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "HEAD^",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return [
        ROOT / path
        for path in result.stdout.splitlines()
    ]


def get_affected_notebooks() -> set[Path]:
    """Determine which notebooks require documentation updates."""
    changed_files = get_changed_files()

    affected_notebooks = set()

    for path in changed_files:
        # A changed notebook always requires its documentation
        # to be regenerated.
        if (
            path.suffix == ".ipynb"
            and NOTEBOOKS_DIR in path.parents
        ):
            affected_notebooks.add(path)

    # Changes to package code may affect documentation of notebooks
    # that use those functions.
    package_changed = any(
        path.suffix == ".py"
        and PACKAGE_DIR in path.parents
        for path in changed_files
    )

    if package_changed:
        for notebook_path in NOTEBOOKS_DIR.glob("*.ipynb"):
            affected_notebooks.add(notebook_path)

    return affected_notebooks


def main() -> None:
    """Generate documentation for affected notebooks."""
    DOCS_DIR.mkdir(exist_ok=True)

    notebooks = get_affected_notebooks()

    if not notebooks:
        print("No notebooks require documentation updates.")
        return

    for notebook_path in sorted(notebooks):
        print(
            f"Generating documentation for "
            f"{notebook_path.name}"
        )

        documentation = generate_documentation(
            notebook_path
        )

        output_path = (
            DOCS_DIR / f"{notebook_path.stem}.md"
        )

        output_path.write_text(
            documentation,
            encoding="utf-8",
        )

        print(f"Created {output_path}")


if __name__ == "__main__":
    main()