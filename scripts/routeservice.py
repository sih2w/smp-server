from quart import Quart, jsonify, request
from scripts.moodservice import MoodService
from scripts.randomservice import RandomService
from scripts.historyservice import HistoryService, History
from scripts.spotifyservice import SpotifyService
from scripts.recommendationservice import RecommendationService
from numpy.random import Generator, PCG64


app = Quart(__name__)


class RouteService:
    @staticmethod
    @app.route("/skip", methods=["GET"])
    def Skip():
        try:
            user_id = request.args.get("UserId")
            song_id = request.args.get("SongId")
            mood = MoodService.GetMood(request.args.get("Mood"))

            history: History = HistoryService.GetHistory(user_id)
            if not song_id in history[mood]["Skipped"]:
                history[mood]["Skipped"][song_id] = 0
            history[mood]["Skipped"][song_id] += 1

            RouteService.AddToPreviouslyPlayed(history, mood, song_id)
            return jsonify({
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.route("/finish", methods=["GET"])
    def Finish():
        try:
            user_id = request.args.get("UserId")
            song_id = request.args.get("SongId")
            mood = MoodService.GetMood(request.args.get("Mood"))

            history: History = HistoryService.GetHistory(user_id)
            if not song_id in history[mood]["Finished"]:
                history[mood]["Finished"][song_id] = 0
            history[mood]["Finished"][song_id] += 1

            RouteService.AddToPreviouslyPlayed(history, mood, song_id)
            return jsonify({
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.route("/like", methods=["GET"])
    def Like():
        try:
            user_id = request.args.get("UserId")
            song_id = request.args.get("SongId")
            mood = MoodService.GetMood(request.args.get("Mood"))
            like = request.args.get("Like", default=True)

            history: History = HistoryService.GetHistory(user_id)
            history[mood]["Liked"][song_id] = like
            return jsonify({
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.route("/dislike", methods=["GET"])
    def Dislike():
        try:
            user_id = request.args.get("UserId")
            song_id = request.args.get("SongId")
            mood = MoodService.GetMood(request.args.get("Mood"))
            disliked = request.args.get("Dislike", default=True)

            history: History = HistoryService.GetHistory(user_id)
            history[mood]["Disliked"][song_id] = disliked
            return jsonify({
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.route("/favorite", methods=["GET"])
    async def Favorite():
        try:
            user_id = request.args.get("UserId")
            song_id = request.args.get("SongId")
            mood = MoodService.GetMood(request.args.get("Mood"))
            favorite = request.args.get("Favorite", default=True)

            history: History = HistoryService.GetHistory(user_id)
            history[mood]["Favorite"][song_id] = favorite
            return jsonify({
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })


    @staticmethod
    def AddToPreviouslyPlayed(history: History, mood: str, song_id: str):
        history[mood]["Previous"].insert(0, song_id)
        if len(history[mood]["Previous"]) > 3:
            history[mood]["Previous"].pop()

    @staticmethod
    @app.route("/playlist", methods=["GET"])
    async def Playlist():
        try:
            mood = MoodService.GetMood(request.args.get("Mood"))
            limit = int(request.args.get("Limit", default=0))

            playlist, message = await SpotifyService.GetPlaylist(mood, limit)

            if message == "":
                return jsonify({
                    "Success": True,
                    "Playlist": playlist,
                })
            else:
                raise Exception(message)
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.route("/next", methods=["GET"])
    def Next():
        try:
            user_id = request.args.get("UserId")
            mood = MoodService.GetMood(request.args.get("Mood"))
            song_ids = request.args.get("SongsIds", [])
            history: History = HistoryService.GetHistory(user_id)

            song_chances = RecommendationService.GetSongChances(history, mood, song_ids)
            song_id = RandomService.GetKey(song_chances, Generator(PCG64()))

            return jsonify({
                "SongId": song_id,
                "Success": True,
            })
        except Exception as e:
            return jsonify({
                "Success": False,
                "Error": str(e),
            })

    @staticmethod
    @app.teardown_appcontext
    def Cleanup(exception=None):
        for user_id, history in HistoryService.Cache.items():
            HistoryService.Save(user_id, history)
            print(f"Saved {user_id}'s history.")

if __name__ == "__main__":
    app.run(debug=True)