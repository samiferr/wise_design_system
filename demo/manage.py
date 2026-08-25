#!/usr/bin/env python
import os
import sys
from pathlib import Path

# The wise_core/wise_autocomplete/wise_richtext packages live one level up,
# at the repo root, since this demo is just one consumer of them.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
