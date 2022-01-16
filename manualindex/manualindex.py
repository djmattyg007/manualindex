import dataclasses
import os
from datetime import datetime, tzinfo
from pathlib import Path
from typing import List, Literal, Sequence, Union
from zoneinfo import ZoneInfo

from humanfriendly import format_size
from jinja2 import Template


EntryType = Literal["dir", "file"]


@dataclasses.dataclass(frozen=True)
class Entry:
    label: str
    extensions: Sequence[str]
    link: str
    hidden: bool
    type: EntryType
    mtime: datetime
    size: int
    size_human: str


@dataclasses.dataclass(frozen=True)
class Breadcrumb:
    label: str
    link: str


def make_entry(base_urlpath: str, date_tz: tzinfo, dirpath_p: Path, dirpath_r: Path, name: str, type: EntryType, /) -> Entry:
    fullpath = dirpath_p / name

    extensions: List[str] = []
    for i in range(len(fullpath.suffixes)):
        extensions.append("".join(fullpath.suffixes[i:]))

    link = f"{base_urlpath}{dirpath_r}/{name}"
    if type == "dir":
        link += "/"

    stat = fullpath.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=date_tz)

    return Entry(
        label=name,
        extensions=extensions,
        link=link,
        hidden=name.startswith("."),
        type=type,
        mtime=mtime,
        size=stat.st_size,
        size_human=format_size(stat.st_size, binary=True),
    )


def make_breadcrumbs(
    base_urlpath: str,
    base_dir: Path,
    dirpath: Path,
    /, *,
    root_label: str = "root",
) -> Sequence[Breadcrumb]:
    parts = dirpath.relative_to(base_dir).parts
    breadcrumbs: List[Breadcrumb] = [
        Breadcrumb(
            label=root_label,
            link=base_urlpath,
        ),
    ]

    for i in range(len(parts)):
        path = "/".join(parts[:i + 1])
        breadcrumbs.append(Breadcrumb(
            label=parts[i],
            link=f"{base_urlpath}{path}/",
        ))

    return breadcrumbs


def make_html(
    template: Template,
    dirpath_p: Path,
    dirpath_r: Path,
    breadcrumbs: Sequence[Breadcrumb],
    entries: Sequence[Entry],
    /, *,
    base_urlpath: str = "/",
    date_format: str = "%Y-%m-%d %H:%I",
    date_tz: Union[str, tzinfo] = "UTC",
) -> str:
    if isinstance(date_tz, str):
        date_tz = ZoneInfo(date_tz)

    template_vars = {
        "base_urlpath": base_urlpath,
        "date_format": date_format,
        "date_tz": date_tz,
        "dirpath": dirpath_p,
        "dirpath_r": dirpath_r,
        "has_parent": len(dirpath_r.parts) > 0,
        "breadcrumbs": breadcrumbs,
        "entries": entries,
    }

    return template.render(template_vars)


def generate(
    base_dir: Path,
    template: Template,
    /, *,
    base_urlpath: str = "/",
    date_format: str = "%Y-%m-%d %H:%I",
    date_tz: Union[str, tzinfo] = "UTC",
) -> None:
    if not base_urlpath.startswith("/"):
        raise Exception("Base URL path must start with a forward-slash ('/').")
    if not base_urlpath.endswith("/"):
        raise Exception("Base URL path must end with a forward-slash ('/').")

    if isinstance(date_tz, str):
        date_tz = ZoneInfo(date_tz)

    for dirpath, dirnames, filenames in os.walk(base_dir):
        dirpath_p = Path(dirpath)
        dirpath_r = dirpath_p.relative_to(base_dir)
        index_p = dirpath_p / "index.html"

        entries: List[Entry] = []
        for dirname in sorted(dirnames):
            if dirname == "index.html":
                raise Exception("Found a directory named index.html, which will conflict with manual index generation.")
            entries.append(make_entry(base_urlpath, date_tz, dirpath_p, dirpath_r, dirname, "dir"))

        for filename in filenames:
            if filename == "index.html":
                index_p.unlink(missing_ok=True)
                continue
            entries.append(make_entry(base_urlpath, date_tz, dirpath_p, dirpath_r, filename, "file"))

        breadcrumbs = make_breadcrumbs(base_urlpath, base_dir, dirpath_p)

        html = make_html(template, dirpath_p, dirpath_r, breadcrumbs, entries, base_urlpath=base_urlpath, date_format=date_format, date_tz=date_tz)

        index_p.write_text(html, encoding="utf-8")
