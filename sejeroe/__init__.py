"""Sejerø Tidende: a manchet, slot, and quote desk for the 2023 silver-label hops.

This package is a personal, download-free workbook. It does not load the 2023
course weights. The original root scripts are left untouched.
"""

from sejeroe.fixtures import ARTICLES, article_by_id
from sejeroe.paths import REPO_ROOT

__all__ = ["ARTICLES", "REPO_ROOT", "article_by_id"]
__version__ = "0.1.0"
