"""Monta a versão do relatório com o código-fonte exigido no apêndice.

Execute novamente depois de qualquer alteração em docs/RELATORIO.md,
src/scheduler.py ou scripts/run_benchmarks.py.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "RELATORIO.md"
OUTPUT = ROOT / "docs" / "RELATORIO_COM_CODIGO.md"
SOURCES = (
    ("Apêndice A — Núcleo dos algoritmos", ROOT / "src" / "scheduler.py", "python"),
    (
        "Apêndice B — Automação dos experimentos",
        ROOT / "scripts" / "run_benchmarks.py",
        "python",
    ),
)
MARKER = "## Apendice A - Codigo-fonte"


def main() -> None:
    report = REPORT.read_text(encoding="utf-8")
    if MARKER not in report:
        raise RuntimeError(f"Marcador não encontrado em {REPORT}: {MARKER}")

    body = report.split(MARKER, maxsplit=1)[0].rstrip()
    appendices = []

    for title, source_path, language in SOURCES:
        code = source_path.read_text(encoding="utf-8").rstrip()
        relative_path = source_path.relative_to(ROOT).as_posix()
        appendices.append(
            f"## {title}\n\n"
            f"Arquivo: `{relative_path}`.\n\n"
            f"```{language}\n{code}\n```"
        )

    generated_notice = (
        "<!-- Arquivo gerado por scripts/montar_relatorio.py. "
        "Edite docs/RELATORIO.md e execute o script novamente. -->"
    )
    output = f"{generated_notice}\n\n{body}\n\n" + "\n\n".join(appendices) + "\n"
    OUTPUT.write_text(output, encoding="utf-8", newline="\n")
    print(f"Relatório completo gerado em {OUTPUT}")


if __name__ == "__main__":
    main()
