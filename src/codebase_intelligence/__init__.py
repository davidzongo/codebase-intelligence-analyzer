"""
Codebase Intelligence Analyzer

A tool for context-aware code intelligence with natural language queries.
Provides traceable references and private deployment options.
"""

__version__ = "0.1.0"
__author__ = "David Zongo"

from .indexer.code_indexer import CodebaseIndexer
from .query.query_engine import QueryEngine

__all__ = ["CodebaseIndexer", "QueryEngine"]
