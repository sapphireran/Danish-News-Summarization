"""Fjordpressen: an offline study kit for the 2023 ITU silver-label pipeline.

Nothing in this package downloads weights or talks to Hugging Face. It
reconstructs the *shape* of the 2023 course scripts — sentence packing,
four-hop silver labels, and lexical overlap — on a closed-world municipal
gazette so the method can be inspected on a laptop.
"""

from .entities import EntityHit, extract_entities, retention_table
from .hops import HopRecord, run_hops
from .ledger import LedgerRow, build_ledger
from .metrics import rouge_scores, compression_ratio
from .packing import TokenCounter, WordTokenCounter, pack_article
from .sentences import split_sentences

__all__ = [
    "EntityHit",
    "HopRecord",
    "LedgerRow",
    "TokenCounter",
    "WordTokenCounter",
    "build_ledger",
    "compression_ratio",
    "extract_entities",
    "pack_article",
    "retention_table",
    "rouge_scores",
    "run_hops",
    "split_sentences",
]

__version__ = "0.1.0"
