from typing import List
from services.historyservice import History
from services.randomservice import WeightedKeys, RandomService


class RecommendationService:
    @staticmethod
    def get_song_chance(history: History, mood: str, song_id: str):
        chance = 1.00

        if song_id in history[mood]["disliked"]:
            chance = 0.10
        else:
            if song_id in history[mood]["previous"]:
                chance -= 0.20

            if song_id in history[mood]["liked"]:
                chance += 0.10

            if song_id in history[mood]["favorite"]:
                chance += 0.20

            if song_id in history[mood]["skipped"] and song_id in history[mood]["finished"]:
                finished_count = history[mood]["finished"][song_id]
                skipped_count = history[mood]["skipped"][song_id]
                percent_finished = finished_count / (finished_count + skipped_count)
                chance += (0.10 * percent_finished)

        chance = max(0.00, min(chance, 1.00))

        return chance

    @staticmethod
    def get_song_chances(history: History, mood: str, song_ids: List[str]):
        song_chances: WeightedKeys = {
            "keys": [],
            "chances": [],
        }

        for song_id in song_ids:
            chance = RecommendationService.get_song_chance(history, mood, song_id)
            song_chances["keys"].append(song_id)
            song_chances["chances"].append(chance)
        song_chances["chances"] = RandomService.normalize(song_chances["chances"])

        return song_chances