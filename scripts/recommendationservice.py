from typing import List
from scripts.historyservice import History
from scripts.randomservice import WeightedKeys, RandomService


class RecommendationService:
    @staticmethod
    def GetSongChance(history: History, mood: str, song_id: str):
        chance = 0.50

        if song_id in history[mood]["Disliked"]:
            chance = 0.10
        else:
            if song_id in history[mood]["Previous"]:
                chance -= 0.20

            if song_id in history[mood]["Liked"]:
                chance += 0.10

            if song_id in history[mood]["Favorite"]:
                chance += 0.20

            if song_id in history[mood]["Skipped"] and song_id in history[mood]["Finished"]:
                finished_count = history[mood]["Finished"][song_id]
                skipped_count = history[mood]["Skipped"][song_id]
                percent_finished = finished_count / (finished_count + skipped_count)
                chance += (0.10 * percent_finished)

        chance = max(0.00, min(chance, 1.00))

        return chance

    @staticmethod
    def GetSongChances(history: History, mood: str, song_ids: List[str]):
        song_chances: WeightedKeys = {
            "Keys": [],
            "Chances": [],
        }

        for song_id in song_ids:
            chance = RecommendationService.GetSongChance(history, mood, song_id)
            song_chances["Keys"].append(song_id)
            song_chances["Chances"].append(chance)
        song_chances["Chances"] = RandomService.Normalize(song_chances["Chances"])

        return song_chances