import base64
import aiohttp
from typing import TypedDict, List, Any, Dict, Tuple, TypeAlias
from datetime import datetime, timedelta
from scripts.moodservice import MoodService
import os


Track: TypeAlias = Dict[str, Any]


class Song(TypedDict):
    Id: str
    Mood: str
    Title: str
    Artists: List[str]
    ImageUrl: str
    Album: str
    AudioUrl: str


class SpotifyService:
    ClientId = os.getenv("CLIENT_ID")
    ClientSecret = os.getenv("CLIENT_SECRET")
    AccessToken = None
    TokenExpiry = None

    @staticmethod
    async def Authenticate():
        if SpotifyService.TokenValid():
            return True, ""

        try:
            headers = {
                "Authorization": "Basic " + base64.b64encode(
                    f"{SpotifyService.ClientId}:{SpotifyService.ClientSecret}".encode("utf-8")
                ).decode("utf-8"),
                "Content-Type": "application/x-www-form-urlencoded",
            }
            body = {"grant_type": "client_credentials"}
            url = "https://accounts.spotify.com/api/token"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=body) as response:
                    if response.status == 200:
                        data = await response.json()
                        SpotifyService.AccessToken = data["access_token"]
                        SpotifyService.TokenExpiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600))
                        return True, ""
                    else:
                        return False, await response.text()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def TokenValid():
        if SpotifyService.AccessToken is None:
            return False

        if SpotifyService.TokenExpiry is None:
            return False

        return datetime.now() < SpotifyService.TokenExpiry

    @staticmethod
    def ToSong(track: Track, mood: str) -> Song:
        return {
            "Id": SpotifyService.GetTrackId(track),
            "Mood": MoodService.GetMood(mood),
            "Title": SpotifyService.GetTitle(track),
            "Artists": SpotifyService.GetArtists(track),
            "ImageUrl": SpotifyService.GetImageUrl(track),
            "Album": SpotifyService.GetAlbum(track),
            "AudioUrl": SpotifyService.GetAudioUrl(track),
        }

    @staticmethod
    def GetTrackId(track: Track) -> str:
        return track.get("id", "")

    @staticmethod
    def GetAudioUrl(track: Track) -> str:
        return track.get("preview_url", "preview_url")

    @staticmethod
    def GetAlbum(track: Track) -> str:
        return track.get("album", {}).get("name", "")

    @staticmethod
    def GetImageUrl(track: Track) -> str:
        images = track.get("album", {}).get("images", [])
        image_url = images[0].get("url", "") if images else ""
        return image_url

    @staticmethod
    def GetTitle(track: Track) -> str:
        return track.get("name", "")

    @staticmethod
    def GetArtists(track: Dict[str, Any]) -> List[str]:
        return [str(artist.get("name", "")) for artist in track.get("artists", []) if artist.get("name")]

    @staticmethod
    async def Search(query: str, limit: int, mood: str) -> Tuple[List[Song], str]:
        success, message = await SpotifyService.Authenticate()
        if not success:
            return [], message

        try:
            url = "https://api.spotify.com/v1/search"
            headers = {"Authorization": f"Bearer {SpotifyService.AccessToken}"}
            params = {
                "q": query,
                "type": "track",
                "market": "US",
                "limit": str(max(1, min(limit, 100)))
            }

            mood = MoodService.GetMood(mood)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("tracks", {}).get("items", [])
                        songs = [
                            SpotifyService.ToSong(item, mood) for item in items
                        ]
                        print(songs)
                        return songs, ""
        except Exception as e:
            return [], str(e)

        return [], ""

    @staticmethod
    async def GetPlaylist(mood: str, limit: int) -> Tuple[List[Song], str]:
        success, message = await SpotifyService.Authenticate()
        if not success:
            return [], message

        mood = MoodService.GetMood(mood)

        mapping = {
            "HAPPY": "HAPPY UPBEAT POP",
            "SAD": "SAD EMOTIONAL HEARTACHE",
            "CHILL": "LOFI CHILL RELAXING",
            "ENERGETIC": "ENERGETIC WORKOUT POP",
            "ROMANTIC": "ROMANTIC LOVE HEART",
            "ANGRY": "ANGER METAL ROCK SHOUTING",
            "PEACEFUL": "PEACE RELAX CALM",
            "PARTY": "PARTY DANCE EDM",
            "MOTIVATIONAL": "INSPIRE CINEMATIC MOTIVATIONAL",
            "NOSTALGIC": "NOSTALGIC THROWBACK RETRO"
        }

        return await SpotifyService.Search(mapping[mood], limit, mood)

