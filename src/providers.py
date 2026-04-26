"""Custom Faker provider for math problem generation.

Locale-specific data (item lists, weekdays, context phrases) lives in
`src/data/pools.<locale>.yaml`. This module loads the active locale's
pool at import and exposes the lists as class attributes on
`MathProblemProvider` so existing call sites (`MathProblemProvider.GROCERY_ITEMS`,
`self.fake.grocery_item()`, etc.) keep working.

Numeric helpers (price/quantity/percentage/ratio generators) stay here
because they are locale-agnostic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from faker.providers import BaseProvider


_DATA_DIR = Path(__file__).parent / "data"
ItemTuple = Tuple[str, str, float, float]


def load_pools(locale: str = "en") -> Dict[str, Any]:
    """Load entity pools from `src/data/pools.<locale>.yaml`.

    Falls back to `en` if the locale file is missing.
    """
    path = _DATA_DIR / f"pools.{locale}.yaml"
    if not path.exists():
        path = _DATA_DIR / "pools.en.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _items_to_tuples(entries: List[Dict[str, Any]]) -> List[ItemTuple]:
    """Convert YAML item dicts to (plural, singular, min_price, max_price) tuples."""
    return [
        (e["plural"], e["singular"], e["min_price"], e["max_price"])
        for e in entries
    ]


_pools = load_pools("en")


class MathProblemProvider(BaseProvider):
    """Faker provider for math problem-specific data."""

    # Item categories: (name_plural, name_singular, min_price, max_price)
    GROCERY_ITEMS = _items_to_tuples(_pools["items"]["grocery"])
    ONLINE_ITEMS = _items_to_tuples(_pools["items"]["online"])
    ELECTRONICS_ITEMS = _items_to_tuples(_pools["items"]["electronics"])
    CLOTHING_ITEMS = _items_to_tuples(_pools["items"]["clothing"])
    BOOK_ITEMS = _items_to_tuples(_pools["items"]["book"])
    SCHOOL_ITEMS = _items_to_tuples(_pools["items"]["school"])
    FURNITURE_ITEMS = _items_to_tuples(_pools["items"]["furniture"])
    OTHER_ITEMS = _items_to_tuples(_pools["items"]["other"])

    # Calendar / time-of-day pools
    WEEKDAYS = list(_pools["calendar"]["weekdays"])
    MONTHS = list(_pools["calendar"]["months"])
    SEASONS = list(_pools["calendar"]["seasons"])
    TIMES_OF_DAY = list(_pools["calendar"]["times_of_day"])

    # Naming suffixes
    STORE_SUFFIXES = list(_pools["naming"]["store_suffixes"])
    RESTAURANT_SUFFIXES = list(_pools["naming"]["restaurant_suffixes"])

    # Context pools
    GARDEN_LOCATIONS = list(_pools["contexts"]["garden_locations"])
    FIELD_TYPES = list(_pools["contexts"]["field_types"])
    ROOM_TYPES = list(_pools["contexts"]["room_types"])
    TRANSIT_TYPES = list(_pools["contexts"]["transit_types"])
    TRAVEL_REASONS = list(_pools["contexts"]["travel_reasons"])
    PROJECT_TYPES = list(_pools["contexts"]["project_types"])
    INHERITANCE_TYPES = list(_pools["contexts"]["inheritance_types"])

    # Investment items: (name, min_price, max_price, depreciation_rates)
    DEPRECIATING_ITEMS = [
        (e["name"], e["min_price"], e["max_price"], list(e["rates"]))
        for e in _pools["depreciating_items"]
    ]

    def grocery_item(self):
        """Return a random grocery item tuple."""
        return self.random_element(self.GROCERY_ITEMS)

    def grocery_items(self, count: int = 1):
        """Return multiple unique grocery items."""
        return self.random_elements(self.GROCERY_ITEMS, length=count, unique=True)

    def online_item(self):
        """Return a random online store item tuple."""
        return self.random_element(self.ONLINE_ITEMS)

    def online_items(self, count: int = 1):
        """Return multiple unique online store items."""
        return self.random_elements(self.ONLINE_ITEMS, length=count, unique=True)

    def electronics_item(self):
        """Return a random electronics item tuple."""
        return self.random_element(self.ELECTRONICS_ITEMS)

    def electronics_items(self, count: int = 1):
        """Return multiple unique electronics items."""
        return self.random_elements(self.ELECTRONICS_ITEMS, length=count, unique=True)

    def clothing_item(self):
        """Return a random clothing item tuple."""
        return self.random_element(self.CLOTHING_ITEMS)

    def clothing_items(self, count: int = 1):
        """Return multiple unique clothing items."""
        return self.random_elements(self.CLOTHING_ITEMS, length=count, unique=True)

    def book_item(self):
        """Return a random book type tuple."""
        return self.random_element(self.BOOK_ITEMS)

    def book_items(self, count: int = 1):
        """Return multiple unique book types."""
        return self.random_elements(self.BOOK_ITEMS, length=count, unique=True)

    def weekday(self):
        """Return a random weekday."""
        return self.random_element(self.WEEKDAYS)

    def season(self):
        """Return a random season."""
        return self.random_element(self.SEASONS)

    def time_of_day(self):
        """Return a random time of day."""
        return self.random_element(self.TIMES_OF_DAY)

    def store_name(self, base_name: str = None):
        """Generate a store name with suffix."""
        base = base_name or self.generator.company()
        suffix = self.random_element(self.STORE_SUFFIXES)
        return base + suffix

    def restaurant_name(self, base_name: str = None):
        """Generate a restaurant name."""
        base = base_name or self.generator.company()
        # Clean up common company suffixes
        for remove in ["Inc", "LLC", "Ltd", "Corp", "Co"]:
            base = base.replace(remove, "").strip()
        suffix = self.random_element(self.RESTAURANT_SUFFIXES)
        return base + suffix

    def garden_location(self):
        """Return a random garden location."""
        return self.random_element(self.GARDEN_LOCATIONS)

    def field_type(self):
        """Return a random field type."""
        return self.random_element(self.FIELD_TYPES)

    def room_type(self):
        """Return a random room type."""
        return self.random_element(self.ROOM_TYPES)

    def transit_type(self):
        """Return a random transit type."""
        return self.random_element(self.TRANSIT_TYPES)

    def travel_reason(self):
        """Return a random travel reason."""
        return self.random_element(self.TRAVEL_REASONS)

    def project_type(self):
        """Return a random project type."""
        return self.random_element(self.PROJECT_TYPES)

    def inheritance_type(self):
        """Return a random inheritance type."""
        return self.random_element(self.INHERITANCE_TYPES)

    def depreciating_item(self):
        """Return a random depreciating item tuple."""
        return self.random_element(self.DEPRECIATING_ITEMS)

    def price(self, min_price: float = 0.5, max_price: float = 50.0, step: float = 0.25):
        """Generate a realistic price with step increments."""
        num_steps = int((max_price - min_price) / step)
        random_step = self.generator.random.randint(0, num_steps)
        return round(min_price + (random_step * step), 2)

    def quantity(self, min_qty: int = 1, max_qty: int = 10):
        """Generate a random quantity."""
        return self.generator.random.randint(min_qty, max_qty)

    def percentage(self, min_pct: int = 5, max_pct: int = 50, step: int = 5):
        """Generate a percentage value with step increments."""
        num_steps = (max_pct - min_pct) // step
        return min_pct + (self.generator.random.randint(0, num_steps) * step)

    def interest_rate(self):
        """Generate a realistic interest rate."""
        return self.random_element([3, 4, 5, 6, 7, 8])

    def principal_amount(self):
        """Generate a principal investment amount."""
        return self.random_element([500, 1000, 1500, 2000, 2500, 3000, 5000])

    def bill_amount(self):
        """Generate a bill amount for splitting."""
        return self.random_element([60, 90, 120, 150, 180, 200, 240])

    def prize_amount(self):
        """Generate a prize amount."""
        return self.random_element([1000, 1500, 2000, 2500, 3000, 5000])

    def ratio_pair(self):
        """Generate a 2-person ratio."""
        return self.random_element([[1, 2], [2, 3], [1, 3], [3, 4]])

    def ratio_triple(self):
        """Generate a 3-person ratio."""
        return self.random_element([[1, 2, 3], [2, 3, 4], [1, 1, 2], [1, 2, 2]])

    def ratio_quad(self):
        """Generate a 4-person ratio."""
        return self.random_element([[1, 2, 3, 4], [1, 1, 2, 2], [2, 3, 3, 4]])

    def dimension(self, min_val: int = 5, max_val: int = 20):
        """Generate a dimension value."""
        return self.generator.random.randint(min_val, max_val)

    def speed_mph(self, context: str = "car"):
        """Generate a speed in mph based on context."""
        speeds = {
            "car": [30, 40, 50, 60, 70],
            "bike": [8, 10, 12, 15, 18],
            "walking": [2, 3, 4],
            "bus": [20, 25, 30, 35],
            "train": [40, 50, 60, 70, 80],
            "airplane": [450, 500, 550],
        }
        return self.random_element(speeds.get(context, speeds["car"]))

    def distance_miles(self, context: str = "local"):
        """Generate a distance in miles based on context."""
        distances = {
            "local": range(2, 15),
            "city": range(10, 50),
            "regional": range(50, 200),
            "flight": range(400, 1500),
        }
        return self.generator.random.choice(list(distances.get(context, distances["local"])))

    def fraction(self):
        """Generate a simple fraction as (numerator, denominator)."""
        fractions = [(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (1, 5), (2, 5), (3, 5)]
        return self.random_element(fractions)
