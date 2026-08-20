#!/usr/bin/env python3
"""Calculate a Western geomancy shield chart from four mother figures."""

from __future__ import annotations

import argparse
import json
import re
import sys


FIGURES = {
    "via": ("Via", "道路", "1111"),
    "道路": ("Via", "道路", "1111"),
    "populus": ("Populus", "群众", "2222"),
    "群众": ("Populus", "群众", "2222"),
    "fortuna-major": ("Fortuna Maior", "大吉", "2211"),
    "fortuna-maior": ("Fortuna Maior", "大吉", "2211"),
    "大吉": ("Fortuna Maior", "大吉", "2211"),
    "fortuna-minor": ("Fortuna Minor", "小吉", "1122"),
    "小吉": ("Fortuna Minor", "小吉", "1122"),
    "acquisitio": ("Acquisitio", "获得", "2121"),
    "获得": ("Acquisitio", "获得", "2121"),
    "amissio": ("Amissio", "失去", "1212"),
    "失去": ("Amissio", "失去", "1212"),
    "conjunctio": ("Coniunctio", "结合", "2112"),
    "coniunctio": ("Coniunctio", "结合", "2112"),
    "结合": ("Coniunctio", "结合", "2112"),
    "carcer": ("Carcer", "限制", "1221"),
    "限制": ("Carcer", "限制", "1221"),
    "laetitia": ("Laetitia", "喜悦", "1222"),
    "喜悦": ("Laetitia", "喜悦", "1222"),
    "tristitia": ("Tristitia", "悲伤", "2221"),
    "悲伤": ("Tristitia", "悲伤", "2221"),
    "puella": ("Puella", "女人", "1211"),
    "女人": ("Puella", "女人", "1211"),
    "puer": ("Puer", "男人", "1121"),
    "男人": ("Puer", "男人", "1121"),
    "albus": ("Albus", "白色", "2212"),
    "白色": ("Albus", "白色", "2212"),
    "rubeus": ("Rubeus", "红色", "2122"),
    "红色": ("Rubeus", "红色", "2122"),
    "caput-draconis": ("Caput Draconis", "龙首", "2111"),
    "龙首": ("Caput Draconis", "龙首", "2111"),
    "cauda-draconis": ("Cauda Draconis", "龙尾", "1112"),
    "龙尾": ("Cauda Draconis", "龙尾", "1112"),
}

PATTERN_TO_LABEL = {}
for english, chinese, pattern in FIGURES.values():
    PATTERN_TO_LABEL[pattern] = (english, chinese)


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_figure(value: str) -> str:
    raw = value.strip()
    compact = raw.replace(" ", "").replace("/", "").replace("-", "")
    compact = compact.replace("single", "1").replace("double", "2")
    compact = compact.replace(".", "1").replace(":", "2")
    if re.fullmatch(r"[12]{4}", compact):
        return compact

    if raw in FIGURES:
        return FIGURES[raw][2]

    key = normalize_key(raw)
    if key in FIGURES:
        return FIGURES[key][2]

    raise ValueError(f"Unknown figure or pattern: {value!r}")


def add(a: str, b: str) -> str:
    return "".join("2" if x == y else "1" for x, y in zip(a, b))


def chart(mothers: list[str]) -> list[str]:
    daughters = ["".join(mother[row] for mother in mothers) for row in range(4)]
    first_niece = add(mothers[0], mothers[1])
    second_niece = add(mothers[2], mothers[3])
    third_niece = add(daughters[0], daughters[1])
    fourth_niece = add(daughters[2], daughters[3])
    right_witness = add(first_niece, second_niece)
    left_witness = add(third_niece, fourth_niece)
    judge = add(right_witness, left_witness)
    reconciler = add(judge, mothers[0])
    return mothers + daughters + [
        first_niece,
        second_niece,
        third_niece,
        fourth_niece,
        right_witness,
        left_witness,
        judge,
        reconciler,
    ]


def label(pattern: str) -> str:
    english, chinese = PATTERN_TO_LABEL.get(pattern, (f"Unknown ({pattern})", "未知"))
    return f"{chinese} / {english}"


def render_text(patterns: list[str]) -> str:
    titles = [
        "母卦1",
        "母卦2",
        "母卦3",
        "母卦4",
        "女儿卦1",
        "女儿卦2",
        "女儿卦3",
        "女儿卦4",
        "侄女卦1",
        "侄女卦2",
        "侄女卦3",
        "侄女卦4",
        "右证人",
        "左证人",
        "法官",
        "调解者",
    ]
    width = max(len(title) for title in titles)
    rows = []
    for index, (title, pattern) in enumerate(zip(titles, patterns), start=1):
        rows.append(f"{index:>2}. {title:<{width}}  {label(pattern):<24}  {pattern}")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mothers", nargs=4, help="Four mother figures by name or pattern")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    try:
        mothers = [parse_figure(value) for value in args.mothers]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    patterns = chart(mothers)
    if args.json:
        print(json.dumps({
            "figures": [
                {
                    "position": i + 1,
                    "name": label(pattern),
                    "pattern": pattern,
                }
                for i, pattern in enumerate(patterns)
            ],
        }, ensure_ascii=False, indent=2))
    else:
        print(render_text(patterns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
