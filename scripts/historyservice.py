import json
from typing import TypedDict, Dict, List, TypeAlias
from scripts.moodservice import MoodService


class MoodHistory(TypedDict):
    Liked: Dict[str, bool]
    Disliked: Dict[str, bool]
    Favorite: Dict[str, bool]
    Skipped: Dict[str, int]
    Finished: Dict[str, int]
    Previous: List[str]


History: TypeAlias = Dict[str, MoodHistory]


class HistoryService:
    Cache: Dict[str, History] = {}

    @staticmethod
    def GetHistory(user_id: str) -> History:
        if user_id not in HistoryService.Cache:
            HistoryService.Cache[user_id] = HistoryService.Load(user_id)
        history = HistoryService.Cache[user_id]
        return history

    @staticmethod
    def GetUserFilePath(user_id):
        return f"../data/users/{user_id}.json"

    @staticmethod
    def Reset(user_id):
        history = HistoryService.Create()
        HistoryService.Save(user_id, history)
        return history

    @staticmethod
    def Load(user_id: str) -> History:
        try:
            with open(HistoryService.GetUserFilePath(user_id), "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return HistoryService.Create()

    @staticmethod
    def Save(user_id: str, history: History) -> None:
        with open(HistoryService.GetUserFilePath(user_id), "w") as f:
            f.write(json.dumps(history))

    @staticmethod
    def Create():
        return {
            mood: {
                "Liked": {},
                "Disliked": {},
                "Favorite": {},
                "Skipped": {},
                "Finished": {},
                "Previous": [],
            } for mood in MoodService.Moods
        }