#!/usr/bin/env python

"""An entry-point that allows the module to be executed.
This also simplifies the distribution as this is the
entry-point for the console script (see setup.py).
"""

import sys
from squad.squad import main as squad_main


def main() -> int:
    """The entry-point of the component."""
    return int(squad_main())


if __name__ == "__main__":
    sys.exit(main())
