"""
Compatibility shim for legacy modules expecting the stdlib ``cgi`` package.
Python 3.14 removed :mod:`cgi`, but httpx/googletrans still import
``parse_header``.  This lightweight replacement implements the subset needed.
"""

from email.parser import HeaderParser


def parse_header(line: str):
    """
    Parse a header like ``'text/plain; charset=\"utf-8\"'`` and return a tuple
    ``(main_value, params_dict)`` matching the historical :func:`cgi.parse_header`
    contract.
    """
    if line is None:
        return "", {}
    parser = HeaderParser()
    header = parser.parsestr(f"Content-Type: {line}\n")
    main = header.get_content_type()
    params_list = header.get_params()[1:]
    params = {key.lower(): value for key, value in params_list}
    return main, params


__all__ = ["parse_header"]
