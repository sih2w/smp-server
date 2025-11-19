from typing import List, TypeVar, TypedDict
from numpy.random import Generator

T = TypeVar("T")


class WeightedKeys(TypedDict):
    Keys: List[T]
    Chances: List[float]


class RandomService:
    @staticmethod
    def GetKey(weighted_keys: WeightedKeys, generator: Generator):
        return generator.choice(a=weighted_keys["Keys"], p=weighted_keys["Chances"])

    @staticmethod
    def Normalize(chances: List[float]):
        total_sum = sum(chances)
        return [x / total_sum for x in chances]