from typing import List, TypeVar, TypedDict
from numpy.random import Generator


T = TypeVar("T")


class WeightedKeys(TypedDict):
    keys: List[T]
    chances: List[float]


class RandomService:
    @staticmethod
    def get_key(weighted_keys: WeightedKeys, generator: Generator):
        return generator.choice(a=weighted_keys["keys"], p=weighted_keys["chances"])

    @staticmethod
    def normalize(chances: List[float]):
        total_sum = sum(chances)
        return [x / total_sum for x in chances]