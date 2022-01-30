# manualindex

[![CI](https://github.com/djmattyg007/manualindex/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/djmattyg007/manualindex/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/manualindex.svg)](https://pypi.org/project/manualindex)

Generate autoindex-style HTML for your directory listings.

## Install

```shell
pip install manualindex
```

Or if you're using poetry:

```shell
poetry add manualindex
```

Manualindex supports Python 3.9 and above. 

## Usage

Manualindex can be used both as a library and as a command-line program.

### CLI

```shell
python -m manualindex /path/to/dir
```

A Jinja template is used to generate the `index.html` files. To customise the template, you'll need to pass two flags:

```shell
python -m manualindex /path/to/dir --template-path /path/to/templates --template-name mytemplate.html.j2
```

For this example to work, there must be a file named `mytemplate.html.j2` inside `/path/to/templates`.

Due to how the URL generation works, if your directory listings are not at the root of your domain, you'll need to pass
the base URL path. For example, if your base URL is `https://example.com/mydir/mysubdir/`, you will need the following:

```shell
python -m manualindex /path/to/dir --base-urlpath /mydir/mysubdir/
```

You can customise the date format:

```shell
python -m manualindex /path/to/dir --date-format '%Y-%m-%d'
```

The default date format is `%Y-%m-%d %H:%I`.

To customise the timezone of the formatted timestamps:

```shell
python -m manualindex /path/to/dir --timezone Australia/Melbourne
```

The default timezone is UTC.

### Library

To make use of all the defaults:

```python
from pathlib import Path
from manualindex import generate_default

generate_default(Path("/path/to/dir"))
```

To customise the template generation options, but use the default template:

```python
from pathlib import Path
from manualindex import default_template, generate

generate(
    Path("/path/to/dir"),
    default_template,
    base_urlpath="/mydir/mysubdir/",
    date_format = "%Y-%m-%d",
    date_tz="Australia/Melbourne",
)
```

The second parameter to `generate()` accepts any Jinja `Template` object, so you have full control over the output.
Manualindex makes no assumptions about where the template comes from.

## License

The code is available under the [GPL Version 3](LICENSE.txt).
