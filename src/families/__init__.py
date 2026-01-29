"""Problem family implementations."""

from .sequential_purchase import SequentialPurchaseFamily
from .rate_time import RateTimeFamily
from .compound_growth import CompoundGrowthFamily
from .multi_person_sharing import MultiPersonSharingFamily
from .area_perimeter_chain import AreaPerimeterChainFamily

# Registry of all problem families
FAMILY_REGISTRY = {
    "sequential_purchase": SequentialPurchaseFamily,
    "rate_time": RateTimeFamily,
    "compound_growth": CompoundGrowthFamily,
    "multi_person_sharing": MultiPersonSharingFamily,
    "area_perimeter_chain": AreaPerimeterChainFamily,
}
