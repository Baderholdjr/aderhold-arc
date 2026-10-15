"""Generate collector/Items.gs from instrument/items.yaml.

The Apps Script survey reads its questions from this generated file, so the survey,
the Sheet columns and the scoring engine can never drift apart.
Run:  python -m arc build-collector     (CI fails if Items.gs is out of date)
"""
from __future__ import annotations

import json
from pathlib import Path

from arc.instrument import ROOT, load

OUT = ROOT / "collector" / "Items.gs"


def render() -> str:
    inst = load()
    payload = {
        "version": inst.version,
        "scale": inst.raw["instrument"]["scale"]["labels"],
        "pillars": inst.raw["pillars"],
        "dimensions": [
            {"code": d.code, "name": d.name, "pillar": d.pillar,
             "items": [{"id": i.id, "text": i.text, "leaderText": i.leader_text, "reverse": i.reverse}
                       for i in d.items]}
            for d in inst.dimensions
        ],
        "behavioral": inst.behavioral,
        "exposure": inst.raw["exposure"],
        "change": inst.raw["change"],
        "leadership": inst.raw["leadership"],
        "openQuestion": inst.raw["open_question"],
        "columns": inst.columns + ["instrument_version"],
    }
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    return ("// GENERATED FILE: do not edit by hand.\n"
            "// Source: instrument/items.yaml  ->  python -m arc build-collector\n"
            f"var ARC_INSTRUMENT = {body};\n")


def main() -> None:
    OUT.write_text(render())
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
