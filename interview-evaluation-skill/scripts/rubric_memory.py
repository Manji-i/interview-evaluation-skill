#!/usr/bin/env python3
import argparse
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from tempfile import NamedTemporaryFile

try:
    import fcntl
except ImportError:
    fcntl = None

RATINGS = ["NH", "H-", "H", "H+", "MH"]
CATEGORIES = ["professional_ability", "soft_quality"]
ROOT = Path(__file__).resolve().parents[1]
MEMORY_ENV_VAR = "INTERVIEW_EVALUATION_RUBRICS_PATH"


def resolve_memory_path():
    configured = os.environ.get(MEMORY_ENV_VAR)
    if configured:
        return Path(configured).expanduser().resolve()
    return ROOT / "memory" / "rubrics.json"


MEMORY_PATH = resolve_memory_path()
LOCK_PATH = MEMORY_PATH.with_name(f".{MEMORY_PATH.name}.lock")


def now():
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def slugify(value):
    slug = re.sub(r"[^\w]+", "_", value.lower(), flags=re.UNICODE).strip("_")
    return slug or "dimension"


def default_memory():
    return {
        "version": 1,
        "updated_at": None,
        "rating_scale": {
            "NH": "clearly below hiring bar",
            "H-": "near bar but materially risky",
            "H": "meets hiring bar",
            "H+": "clearly above bar",
            "MH": "exceptional strong hire signal",
        },
        "categories": {
            "professional_ability": {"display_name": "专业能力", "dimensions": {}},
            "soft_quality": {"display_name": "软素质", "dimensions": {}},
        },
        "templates": {},
    }


@contextmanager
def memory_lock():
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file, fcntl.LOCK_UN)


def load_memory():
    if not MEMORY_PATH.exists():
        return default_memory()
    try:
        with MEMORY_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except JSONDecodeError:
        backup_path = MEMORY_PATH.with_name(f"{MEMORY_PATH.name}.broken.{timestamp_slug()}")
        MEMORY_PATH.replace(backup_path)
        return default_memory()
    for category in CATEGORIES:
        data.setdefault("categories", {}).setdefault(
            category,
            {
                "display_name": "专业能力" if category == "professional_ability" else "软素质",
                "dimensions": {},
            },
        )
        data["categories"][category].setdefault("dimensions", {})
    data.setdefault("templates", {})
    return data


def save_memory(data):
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now()
    with NamedTemporaryFile("w", encoding="utf-8", dir=MEMORY_PATH.parent, delete=False) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
        tmp_path = Path(f.name)
    tmp_path.replace(MEMORY_PATH)


def parse_levels(raw):
    if not raw:
        return {}
    levels = json.loads(raw)
    if not isinstance(levels, dict):
        raise SystemExit("--levels-json must be a JSON object")
    invalid = sorted(set(levels) - set(RATINGS))
    if invalid:
        raise SystemExit(f"invalid rating keys: {', '.join(invalid)}")
    return {rating: str(levels.get(rating, "")) for rating in RATINGS}


def parse_dimensions(raw):
    if not raw:
        raise SystemExit("--dimensions-json is required")
    dimensions = json.loads(raw)
    if not isinstance(dimensions, list):
        raise SystemExit("--dimensions-json must be a JSON array")
    normalized = []
    for item in dimensions:
        if not isinstance(item, dict):
            raise SystemExit("each dimension must be a JSON object")
        category = item.get("category")
        name = item.get("name")
        if category not in CATEGORIES:
            raise SystemExit(f"dimension category must be one of: {', '.join(CATEGORIES)}")
        if not name:
            raise SystemExit("dimension name is required")
        normalized.append({"category": category, "name": str(name)})
    return normalized


def find_dimension(dimensions, name):
    target = slugify(name)
    if target in dimensions:
        return target
    lower = name.lower()
    for key, value in dimensions.items():
        names = [value.get("name", ""), *value.get("aliases", [])]
        if lower in [item.lower() for item in names]:
            return key
    return target


def find_template(templates, name):
    target = slugify(name)
    if target in templates:
        return target
    lower = name.lower()
    for key, value in templates.items():
        names = [value.get("name", ""), *value.get("aliases", [])]
        if lower in [item.lower() for item in names]:
            return key
    return target


def cmd_show(_args):
    print(json.dumps(load_memory(), ensure_ascii=False, indent=2))


def cmd_list_templates(_args):
    data = load_memory()
    templates = data.get("templates", {})
    result = []
    for key, value in templates.items():
        result.append(
            {
                "key": key,
                "name": value.get("name", key),
                "description": value.get("description", ""),
                "role": value.get("role", ""),
                "dimensions": value.get("dimensions", []),
                "updated_at": value.get("updated_at"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_show_template(args):
    data = load_memory()
    templates = data.get("templates", {})
    key = find_template(templates, args.name)
    if key not in templates:
        raise SystemExit(f"template not found: {args.name}")
    print(json.dumps(templates[key], ensure_ascii=False, indent=2))


def cmd_upsert_dimension(args):
    if args.category not in CATEGORIES:
        raise SystemExit(f"--category must be one of: {', '.join(CATEGORIES)}")
    with memory_lock():
        data = load_memory()
        dimensions = data["categories"][args.category]["dimensions"]
        key = find_dimension(dimensions, args.name)
        existing = dimensions.get(key, {})
        aliases = [item.strip() for item in (args.aliases or "").split(",") if item.strip()]
        levels = existing.get("level_anchors", {rating: "" for rating in RATINGS})
        levels.update({rating: value for rating, value in parse_levels(args.levels_json).items() if value})
        dimensions[key] = {
            "name": args.name,
            "aliases": aliases or existing.get("aliases", []),
            "definition": args.definition or existing.get("definition", ""),
            "level_anchors": {rating: levels.get(rating, "") for rating in RATINGS},
            "calibrations": existing.get("calibrations", []),
        }
        save_memory(data)
    print(f"upserted {args.category}.{key}")


def cmd_upsert_template(args):
    dimensions = parse_dimensions(args.dimensions_json)
    with memory_lock():
        data = load_memory()
        templates = data.setdefault("templates", {})
        key = find_template(templates, args.name)
        existing = templates.get(key, {})
        aliases = [item.strip() for item in (args.aliases or "").split(",") if item.strip()]
        timestamp = now()
        templates[key] = {
            "name": args.name,
            "aliases": aliases or existing.get("aliases", []),
            "description": args.description or existing.get("description", ""),
            "role": args.role or existing.get("role", ""),
            "dimensions": dimensions,
            "created_at": existing.get("created_at") or timestamp,
            "updated_at": timestamp,
        }
        save_memory(data)
    print(f"upserted template {key}")


def cmd_add_calibration(args):
    if args.category not in CATEGORIES:
        raise SystemExit(f"--category must be one of: {', '.join(CATEGORIES)}")
    with memory_lock():
        data = load_memory()
        dimensions = data["categories"][args.category]["dimensions"]
        key = find_dimension(dimensions, args.name)
        if key not in dimensions:
            dimensions[key] = {
                "name": args.name,
                "aliases": [],
                "definition": "",
                "level_anchors": {rating: "" for rating in RATINGS},
                "calibrations": [],
            }
        if args.standard:
            anchor_rating = args.from_rating or args.to_rating
            dimensions[key]["level_anchors"][anchor_rating] = args.standard
        dimensions[key].setdefault("calibrations", []).append(
            {
                "timestamp": now(),
                "from_rating": args.from_rating,
                "to_rating": args.to_rating,
                "note": args.note,
                "standard": args.standard,
            }
        )
        save_memory(data)
    print(f"added calibration {args.category}.{key}")


def build_parser():
    parser = argparse.ArgumentParser(description="Manage interview evaluation rubric memory.")
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show", help="Print rubric memory JSON.")
    show.set_defaults(func=cmd_show)

    list_templates = sub.add_parser("list-templates", help="Print saved interview dimension templates.")
    list_templates.set_defaults(func=cmd_list_templates)

    show_template = sub.add_parser("show-template", help="Print one interview dimension template.")
    show_template.add_argument("--name", required=True)
    show_template.set_defaults(func=cmd_show_template)

    upsert = sub.add_parser("upsert-dimension", help="Create or update a rubric dimension.")
    upsert.add_argument("--category", required=True)
    upsert.add_argument("--name", required=True)
    upsert.add_argument("--definition", default="")
    upsert.add_argument("--aliases", default="")
    upsert.add_argument("--levels-json", default="")
    upsert.set_defaults(func=cmd_upsert_dimension)

    template = sub.add_parser("upsert-template", help="Create or update an interview dimension template.")
    template.add_argument("--name", required=True)
    template.add_argument("--description", default="")
    template.add_argument("--role", default="")
    template.add_argument("--aliases", default="")
    template.add_argument("--dimensions-json", required=True)
    template.set_defaults(func=cmd_upsert_template)

    calibration = sub.add_parser("add-calibration", help="Record user feedback on scoring standards.")
    calibration.add_argument("--category", required=True)
    calibration.add_argument("--name", required=True)
    calibration.add_argument("--from-rating", choices=RATINGS, default="")
    calibration.add_argument("--to-rating", choices=RATINGS, required=True)
    calibration.add_argument("--note", required=True)
    calibration.add_argument("--standard", required=True)
    calibration.set_defaults(func=cmd_add_calibration)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
