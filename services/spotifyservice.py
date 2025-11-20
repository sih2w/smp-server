import base64
import aiohttp
from typing import TypedDict, List, Any, Dict, Tuple, TypeAlias
from datetime import datetime, timedelta
from services.moodservice import MoodService
from os import getenv


Track: TypeAlias = Dict[str, Any]


class Song(TypedDict):
    id: str
    mood: str
    title: str
    artists: List[str]
    image_url: str
    album: str
    audio_url: str


class SpotifyService:
    client_id = getenv("CLIENT_ID")
    client_secret = getenv("CLIENT_SECRET")
    access_token = None
    token_expiry = None

    @staticmethod
    async def authenticate():
        if SpotifyService.token_valid():
            return True, ""

        try:
            headers = {
                "Authorization": "Basic " + base64.b64encode(
                    f"{SpotifyService.client_id}:{SpotifyService.client_secret}".encode("utf-8")
                ).decode("utf-8"),
                "Content-Type": "application/x-www-form-urlencoded",
            }
            body = {"grant_type": "client_credentials"}
            url = "https://accounts.spotify.com/api/token"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=body) as response:
                    if response.status == 200:
                        data = await response.json()
                        SpotifyService.access_token = data["access_token"]
                        SpotifyService.token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 3600))
                        return True, ""
                    else:
                        return False, await response.text()
        except Exception as e:
            return False, str(e)

    @staticmethod
    def token_valid():
        if SpotifyService.access_token is None:
            return False

        if SpotifyService.token_expiry is None:
            return False

        return datetime.now() < SpotifyService.token_expiry

    @staticmethod
    def to_song(track: Track, mood: str) -> Song:
        return {
            "id": SpotifyService.get_track_id(track),
            "mood": MoodService.get_mood(mood),
            "title": SpotifyService.get_title(track),
            "artists": SpotifyService.get_artists(track),
            "image_url": SpotifyService.get_image_url(track),
            "album": SpotifyService.get_album(track),
            "audio_url": SpotifyService.get_audio_url(track),
        }

    @staticmethod
    def get_track_id(track: Track) -> str:
        return track.get("id", "")

    @staticmethod
    def get_audio_url(track: Track) -> str:
        return track.get("preview_url", "preview_url")

    @staticmethod
    def get_album(track: Track) -> str:
        return track.get("album", {}).get("name", "")

    @staticmethod
    def get_image_url(track: Track) -> str:
        images = track.get("album", {}).get("images", [])
        image_url = images[0].get("url", "") if images else ""
        return image_url

    @staticmethod
    def get_title(track: Track) -> str:
        return track.get("name", "")

    @staticmethod
    def get_artists(track: Dict[str, Any]) -> List[str]:
        return [str(artist.get("name", "")) for artist in track.get("artists", []) if artist.get("name")]

    @staticmethod
    async def search(query: str, limit: int, mood: str) -> Tuple[List[Song], str]:
        success, message = await SpotifyService.authenticate()
        if not success:
            return [], message

        try:
            url = "https://api.spotify.com/v1/search"
            headers = {"Authorization": f"Bearer {SpotifyService.access_token}"}
            params = {
                "q": query,
                "type": "track",
                "market": "US",
                "limit": str(max(1, min(limit, 100)))
            }

            mood = MoodService.get_mood(mood)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("tracks", {}).get("items", [])
                        songs = [
                            SpotifyService.to_song(item, mood) for item in items
                        ]
                        return songs, ""
        except Exception as e:
            return [], str(e)

        return [], ""

    @staticmethod
    async def get_playlist(mood: str, limit: int) -> Tuple[List[Song], str]:
        success, message = await SpotifyService.authenticate()
        if not success:
            return [], message

        mood = MoodService.get_mood(mood)
        keywords = MoodService.get_keywords(mood)

        return await SpotifyService.search(keywords, limit, mood)
