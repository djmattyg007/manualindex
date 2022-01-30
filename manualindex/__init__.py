from datetime import tzinfo
from pathlib import Path
from typing import Union

from fs.base import FS
from jinja2 import Environment, FileSystemLoader

from .manualindex import (
    Breadcrumb,
    Breadcrumbs,
    Entries,
    Entry,
    EntryType,
    default_date_format,
    default_date_tz,
    default_index_filename,
    default_root_label,
    generate,
    make_breadcrumbs,
    make_entry,
    make_html,
)


__version__ = "1.0.1"


default_template_path = Path(__file__).parent / "templates"
default_template_name = "manualindex.html.j2"
default_jinja_env = Environment(
    loader=FileSystemLoader(default_template_path), autoescape=True, trim_blocks=True
)
default_template = default_jinja_env.get_template(default_template_name)


def generate_default(
    base_dir: Union[FS, Path],
    /,
    *,
    base_urlpath: str = "/",
    date_format: str = default_date_format,
    date_tz: Union[str, tzinfo] = default_date_tz,
    index_filename: str = default_index_filename,
    root_label: str = default_root_label,
) -> None:
    generate(
        base_dir,
        default_template,
        base_urlpath=base_urlpath,
        date_format=date_format,
        date_tz=date_tz,
        index_filename=index_filename,
        root_label=root_label,
    )


__all__ = (
    "EntryType",
    "Entry",
    "Entries",
    "Breadcrumb",
    "Breadcrumbs",
    "make_entry",
    "make_breadcrumbs",
    "make_html",
    "generate",
    "default_date_format",
    "default_date_tz",
    "default_index_filename",
    "default_root_label",
    "default_template_path",
    "default_template_name",
    "default_jinja_env",
    "default_template",
    "generate_default",
)
