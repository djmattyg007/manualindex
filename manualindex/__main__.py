from argparse import ArgumentParser
from pathlib import Path
from zoneinfo import ZoneInfo  # noqa: I900

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


def main():
    parser = make_parser()
    args = parser.parse_args()

    if not args.directory.is_dir():
        raise Exception("Invalid directory specified.")

    jinja_env = Environment(loader=FileSystemLoader(args.template_path))
    template = jinja_env.get_template(args.template_name)

    generate(
        args.directory,
        template,
        base_urlpath=args.base_urlpath,
        date_format=args.date_format,
        date_tz=args.timezone,
    )


if __name__ == "__main__":
    main()
