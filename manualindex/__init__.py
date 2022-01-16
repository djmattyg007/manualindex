from datetime import tzinfo
from pathlib import Path
from typing import Union

from jinja2 import Environment, FileSystemLoader

from .manualindex import *


default_template_path = Path(__file__).parent / "templates"
default_template_name = "manualindex.html.j2"
default_jinja_env = Environment(loader=FileSystemLoader(default_template_path))
default_template = default_jinja_env.get_template(default_template_name)


def generate_default(
    base_dir: Path,
    /,
    *,
    base_urlpath: str = "/",
    date_format: str = "%Y-%m-%d %H:%I",
    date_tz: Union[str, tzinfo] = "UTC",
) -> None:
    generate(
        base_dir,
        default_template,
        base_urlpath=base_urlpath,
        date_format=date_format,
        date_tz=date_tz,
    )


__all__ = (
    "EntryType",
    "Entry",
    "Breadcrumb",
    "make_entry",
    "make_breadcrumbs",
    "make_html",
    "generate",
    "default_template_path",
    "default_template_name",
    "default_jinja_env",
    "default_template",
    "generate_default",
)
