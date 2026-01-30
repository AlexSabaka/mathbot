"""Custom Faker provider for math problem generation.

This provider supplies context-appropriate items, prices, and values
for procedural math problem generation.
"""

import random
from faker.providers import BaseProvider


class MathProblemProvider(BaseProvider):
    """Faker provider for math problem-specific data."""

    # Grocery items: (name_plural, name_singular, min_price, max_price)
    GROCERY_ITEMS = [
        ("apples", "apple", 0.50, 2.00),
        ("oranges", "orange", 0.60, 2.50),
        ("bananas", "banana", 0.30, 1.50),
        ("milk cartons", "milk carton", 2.50, 5.00),
        ("loaves of bread", "loaf of bread", 2.00, 4.00),
        ("dozen eggs", "dozen eggs", 2.50, 6.00),
        ("blocks of cheese", "block of cheese", 3.00, 8.00),
        ("pounds of chicken", "pound of chicken", 5.00, 12.00),
        ("tomatoes", "tomato", 0.75, 2.50),
        ("heads of lettuce", "head of lettuce", 1.50, 3.50),
    ]

    # Online store items
    ONLINE_ITEMS = [
        ("books", "book", 8.00, 25.00),
        ("notebooks", "notebook", 3.00, 8.00),
        ("pens", "pen", 1.00, 5.00),
        ("headphones", "pair of headphones", 15.00, 50.00),
        ("phone cases", "phone case", 10.00, 30.00),
        ("water bottles", "water bottle", 8.00, 20.00),
        ("backpacks", "backpack", 20.00, 60.00),
    ]

    # Electronics items
    ELECTRONICS_ITEMS = [
        ("laptops", "laptop", 400.00, 1200.00),
        ("tablets", "tablet", 200.00, 600.00),
        ("mice", "mouse", 15.00, 50.00),
        ("keyboards", "keyboard", 30.00, 100.00),
        ("monitors", "monitor", 150.00, 400.00),
        ("webcams", "webcam", 40.00, 120.00),
    ]

    # Clothing items
    CLOTHING_ITEMS = [
        ("shirts", "shirt", 15.00, 40.00),
        ("pants", "pair of pants", 25.00, 60.00),
        ("shoes", "pair of shoes", 40.00, 100.00),
        ("socks", "pair of socks", 5.00, 15.00),
        ("jackets", "jacket", 50.00, 150.00),
        ("sweaters", "sweater", 30.00, 70.00),
    ]

    # Book types
    BOOK_ITEMS = [
        ("novels", "novel", 12.00, 25.00),
        ("textbooks", "textbook", 40.00, 100.00),
        ("comic books", "comic book", 5.00, 15.00),
        ("magazines", "magazine", 4.00, 10.00),
        ("cookbooks", "cookbook", 20.00, 40.00),
    ]

    # Days of the week
    WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Seasons
    SEASONS = ["spring", "summer", "fall", "winter"]
    
    # Time of day
    TIMES_OF_DAY = ["morning", "afternoon", "evening"]

    # Store types
    STORE_SUFFIXES = [" Boutique", " Outlet", " Store", " Shop", " Emporium"]
    
    # Restaurant suffixes
    RESTAURANT_SUFFIXES = [" Restaurant", " Cafe", " Bistro", " Grill", " Kitchen"]

    # Locations for geometry problems
    GARDEN_LOCATIONS = ["backyard", "community park", "rooftop", "neighborhood"]
    
    # Field types
    FIELD_TYPES = ["athletic", "farming", "community", "recreational"]
    
    # Room types
    ROOM_TYPES = ["living room", "kitchen", "bathroom", "bedroom", "office"]

    # Transit types
    TRANSIT_TYPES = ["bus", "train", "subway", "metro"]
    
    # Travel reasons
    TRAVEL_REASONS = ["a business trip", "vacation", "visiting family", "a conference"]

    # Project types for sharing problems
    PROJECT_TYPES = ["a community project", "a hackathon", "a research project", "a startup"]
    
    # Relationship types for inheritance
    INHERITANCE_TYPES = ["family estate", "trust fund", "will", "inheritance"]

    # Investment item types: (name, min_price, max_price, depreciation_rates)
    DEPRECIATING_ITEMS = [
        ("car", 25000, 35000, [10, 12, 15]),
        ("laptop", 1200, 2000, [20, 25, 30]),
        ("machinery", 50000, 80000, [10, 12, 15]),
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
