from argparse import ArgumentParser
from pathlib import Path
from typing import Optional, Sequence
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

from . import default_template_name, default_template_path, generate


def make_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="manualindex",
        description="Generate autoindex-style HTML for your directory listings.",
        allow_abbrev=False,
    )

    parser.add_argument("directory", action="store", type=Path)

    parser.add_argument("--template-path", action="store", type=Path, default=default_template_path)
    parser.add_argument("--template-name", action="store", type=str, default=default_template_name)

    parser.add_argument("--base-urlpath", action="store", type=str, default="/")
    parser.add_argument("--date-format", action="store", type=str, default="%Y-%m-%d %H:%I")
    parser.add_argument("--timezone", action="store", type=ZoneInfo, default="UTC")

    return parser


def main(args: Optional[Sequence[str]] = None):
    if args is None:
        import sys

        args = sys.argv[1:]

    parser = make_parser()
    pargs = parser.parse_args(args)

    if not pargs.directory.is_dir():
        raise Exception("Invalid directory specified.")

    jinja_env = Environment(
        loader=FileSystemLoader(pargs.template_path), autoescape=True, trim_blocks=True
    )
    template = jinja_env.get_template(pargs.template_name)

    generate(
        pargs.directory,
        template,
        base_urlpath=pargs.base_urlpath,
        date_format=pargs.date_format,
        date_tz=pargs.timezone,
    )
