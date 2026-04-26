"""Mathbot — K1-K12 procedurally generated math word-problem benchmark plugin."""

from src.plugins.base import (
    BenchmarkPlugin,
    ResponseParser,
    ResultEvaluator,
    TestCaseGenerator,
)

from .evaluator import MathbotEvaluator
from .generator import MathbotGenerator
from .parser import MathbotParser


class MathbotPlugin(BenchmarkPlugin):
    @property
    def task_type(self) -> str:
        return "mathbot"

    @property
    def display_name(self) -> str:
        return "Mathbot — K1-K12 word problems"

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_generator(self) -> TestCaseGenerator:
        return MathbotGenerator()

    def get_parser(self) -> ResponseParser:
        return MathbotParser()

    def get_evaluator(self) -> ResultEvaluator:
        return MathbotEvaluator()


plugin = MathbotPlugin()
