"""
Labelord's public interface

Module defines **app** which is instance of class :class:`~labelord.web.LabelordWeb` and function **cli()** which is function :func:`~labelord.cli.cli`.
"""

from .cli import cli
from .web import app 

__all__ = ['cli', 'app']
