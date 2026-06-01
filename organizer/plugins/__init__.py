"""Plugins package for organizer.

Plugins can expose additional rule sources or hooks in the future.
This package is a placeholder and provides a simple registry API.
"""

_registry = {}


def register(name: str, obj):
    _registry[name] = obj


def get(name: str):
    return _registry.get(name)


def list_plugins():
    return list(_registry.keys())
