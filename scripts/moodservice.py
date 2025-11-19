class MoodService:
    Moods = [
        "HAPPY",
        "SAD",
        "CHILL",
        "ENERGETIC",
        "ROMANTIC",
        "ANGRY",
        "PEACEFUL",
        "PARTY",
        "MOTIVATIONAL",
        "NOSTALGIC"
    ]

    @staticmethod
    def GetMood(mood: str) -> str:
        if mood in MoodService.Moods:
            return mood
        return MoodService.Moods[-1]