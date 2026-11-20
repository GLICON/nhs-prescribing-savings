"""nhs_rx - my NHS prescribing savings project.

This file makes the src/nhs_rx folder a Python "package",
so I can write `import nhs_rx` anywhere in the project.

What goes in this folder (added in later commits):
    sources/     -> downloads data from the NHS APIs
    transforms/  -> the PySpark steps: bronze -> silver -> gold
    bnf.py       -> works out if a medicine is branded or generic
    stats.py     -> the statistics (deprivation test)
"""

__version__ = "0.1.0"  # the version of my project
