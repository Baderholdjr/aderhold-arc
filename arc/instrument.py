"""Load the Aderhold A.R.C. instrument definition (instrument/items.yaml).

items.yaml is the single source of truth: the survey page, the scoring engine
and the reports are all generated from it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "instrument" / "items.yaml"

META_COLUMNS = ["response_id", "campaign", "submitted_date", "consent_research", "role"]


@dataclass(frozen=True)
class Item:
    id: str
    text: str
    reverse: bool
    dimension: str


@dataclass(frozen=True)
class Dimension:
    code: str
    name: str
    pillar: str
    items: tuple[Item, ...]


@dataclass
class Instrument:
    raw: dict
    dimensions: list[Dimension] = field(default_factory=list)

    @property
    def items(self) -> list[Item]:
        return [i for d in self.dimensions for i in d.items]

    @property
    def item_ids(self) -> list[str]:
        return [i.id for i in self.items]

    @property
    def pillars(self) -> list[str]:
        return [p["name"] for p in self.raw["pillars"]]

    @property
    def behavioral(self) -> list[dict]:
        return self.raw["behavioral"]

    @property
    def behavioral_keys(self) -> list[str]:
        return [b["key"] for b in self.behavioral if b["key"] != "role"]

    @property
    def scoring(self) -> dict:
        return self.raw["scoring"]

    @property
    def version(self) -> str:
        return self.raw["instrument"]["version"]

    @property
    def columns(self) -> list[str]:
        """Canonical column order for a response row (Sheet and CSV)."""
        return META_COLUMNS + self.behavioral_keys + self.item_ids + ["open_text"]

    def severity(self, index: float | None) -> str | None:
        if index is None:
            return None
        for band in self.scoring["severity"]:
            if index < band["below"]:
                return band["label"]
        return None

    def maturity(self, index: float | None) -> tuple[int, str] | tuple[None, None]:
        if index is None:
            return (None, None)
        for band in self.scoring["maturity"]:
            if index < band["below"]:
                return (band["level"], band["name"])
        return (None, None)


def load(path: str | Path = DEFAULT_PATH) -> Instrument:
    raw = yaml.safe_load(Path(path).read_text())
    dims = []
    for d in raw["dimensions"]:
        items = tuple(Item(i["id"], i["text"], bool(i["reverse"]), d["code"]) for i in d["items"])
        dims.append(Dimension(d["code"], d["name"], d["pillar"], items))
    inst = Instrument(raw=raw, dimensions=dims)
    _validate(inst)
    return inst


def _validate(inst: Instrument) -> None:
    ids = inst.item_ids
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate item ids in instrument")
    for d in inst.dimensions:
        if d.pillar not in inst.pillars:
            raise ValueError(f"Dimension {d.code} has unknown pillar {d.pillar}")
        if len(d.items) < 2:
            raise ValueError(f"Dimension {d.code} needs at least 2 items")
