import dataclasses
from datetime import datetime, tzinfo
from pathlib import Path
from typing import List, Literal, Optional, Sequence, Union
from zoneinfo import ZoneInfo

from fs.base import FS
from fs.errors import ResourceNotFound
from fs.filesize import binary as format_size
from fs.info import Info as FSInfo
from fs.path import combine as path_combine
from fs.path import parts as path_parts
from jinja2 import Template


EntryType = Literal["dir", "file"]


default_date_format = "%Y-%m-%d %H:%I"
default_date_tz = "UTC"
default_index_filename = "index.html"
default_root_label = "root"


# TODO: Add slots=true when supporting python3.10 only
@dataclasses.dataclass(frozen=True)
class Entry:
    info: FSInfo
    extensions: Sequence[str]
    link: str
    hidden: bool
    entry_type: EntryType
    ctime_local: Optional[datetime]
    mtime_local: Optional[datetime]
    size_human: str


Entries = Sequence[Entry]


# TODO: Add slots=true when supporting python3.10 only
@dataclasses.dataclass(frozen=True)
class Breadcrumb:
    label: str
    link: str


Breadcrumbs = Sequence[Breadcrumb]


def make_entry(
    base_urlpath: str,
    date_tz: tzinfo,
    dirpath: str,
    info: FSInfo,
    entry_type: EntryType,
) -> Entry:
    extensions: List[str] = []
    for i in range(len(info.suffixes)):
        extensions.append("".join(info.suffixes[i:]))

    link = f"{base_urlpath}{dirpath}{info.name}"
    if entry_type == "dir":
        link += "/"

    return Entry(
        info=info,
        extensions=tuple(extensions),
        link=link,
        hidden=info.name.startswith("."),
        entry_type=entry_type,
        ctime_local=info.created.astimezone(date_tz) if info.created else None,
        mtime_local=info.modified.astimezone(date_tz) if info.modified else None,
        size_human=format_size(info.size),
    )


def make_breadcrumbs(
    base_urlpath: str,
    dirpath: str,
    /,
    *,
    root_label: str = default_root_label,
) -> Breadcrumbs:
    parts = path_parts(dirpath)[1:]
    breadcrumbs: List[Breadcrumb] = [
        Breadcrumb(
            label=root_label,
            link=base_urlpath,
        )
    ]

    for i in range(len(parts)):
        path = "/".join(parts[: i + 1])
        breadcrumbs.append(
            Breadcrumb(
                label=parts[i],
                link=f"{base_urlpath}{path}/",
            )
        )

    return tuple(breadcrumbs)


def make_html(
    template: Template,
    dirpath: str,
    breadcrumbs: Breadcrumbs,
    entries: Entries,
    /,
    *,
    base_urlpath: str = "/",
    date_format: str = default_date_format,
    date_tz: Union[str, tzinfo] = default_date_tz,
) -> str:
    if isinstance(date_tz, str):
        date_tz = ZoneInfo(date_tz)

    template_vars = {
        "base_urlpath": base_urlpath,
        "date_format": date_format,
        "date_tz": date_tz,
        "dirpath": dirpath,
        "has_parent": dirpath.count("/") > 0,
        "breadcrumbs": breadcrumbs,
        "entries": entries,
    }

    return template.render(template_vars)


def generate(
    base_dir: Union[FS, Path],
    template: Template,
    /,
    *,
    base_urlpath: str = "/",
    date_format: str = default_date_format,
    date_tz: Union[str, tzinfo] = default_date_tz,
    index_filename: str = default_index_filename,
    root_label: str = default_root_label,
) -> None:
    if not base_urlpath.startswith("/"):
        raise ValueError("Base URL path must start with a forward-slash ('/').")
    if not base_urlpath.endswith("/"):
        raise ValueError("Base URL path must end with a forward-slash ('/').")

    for sep in ("/", "\\", ":", ";"):
        if sep in index_filename:
            raise ValueError("Index filename must not contain path separators.")

    if isinstance(base_dir, Path):
        from fs.osfs import OSFS

        with OSFS(str(base_dir)) as p_base_dir:
            return generate(
                p_base_dir,
                template,
                base_urlpath=base_urlpath,
                date_format=date_format,
                date_tz=date_tz,
            )

    if isinstance(date_tz, str):
        date_tz = ZoneInfo(date_tz)

    for dirpath, subdirs, subfiles in base_dir.walk(namespaces=["details"]):
        if dirpath == "/":
            dirpath = ""
        else:
            dirpath = dirpath[1:] + "/"

        entries: List[Entry] = []
        for subdir in sorted(subdirs, key=lambda info: info.name):
            if subdir.name == index_filename:
                raise Exception(
                    "Found a directory named index.html, which will conflict with manual index generation."
                )
            entries.append(make_entry(base_urlpath, date_tz, dirpath, subdir, "dir"))

        for subfile in sorted(subfiles, key=lambda info: info.name):
            if subfile.name == index_filename:
                try:
                    base_dir.remove(path_combine(dirpath, subfile.name))
                except ResourceNotFound:
                    pass
                continue

            entries.append(make_entry(base_urlpath, date_tz, dirpath, subfile, "file"))

        breadcrumbs = make_breadcrumbs(base_urlpath, dirpath, root_label=root_label)

        html = make_html(
            template,
            dirpath,
            breadcrumbs,
            tuple(entries),
            base_urlpath=base_urlpath,
            date_format=date_format,
            date_tz=date_tz,
        )

        base_dir.writetext(path_combine(dirpath, index_filename), html, encoding="utf-8")


__all__ = (
    "EntryType",
    "Entry",
    "Entries",
    "Breadcrumb",
    "Breadcrumbs",
    "default_date_format",
    "default_date_tz",
    "default_index_filename",
    "default_root_label",
    "make_entry",
    "make_breadcrumbs",
    "make_html",
    "generate",
)
