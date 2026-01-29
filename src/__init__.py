"""
Math Problem Generator

A library for generating procedurally-created, multi-step math word problems.
"""

from .generator import generate_problem, generate_problems, get_available_options

__version__ = "0.1.0"
__all__ = ["generate_problem", "generate_problems", "get_available_options"]
