from functools import wraps
from os import getenv
from quart import Quart, jsonify, abort
from services.randomservice import RandomService
from services.historyservice import HistoryService, History
from services.spotifyservice import SpotifyService
from services.recommendationservice import RecommendationService
from numpy.random import Generator, PCG64
from quart_cors import cors


app = Quart(__name__)
app = cors(app, allow_origin="*")


def verify_request(func):
    @wraps(func)
    async def decorated_function(key, *args, **kwargs):
        if key != getenv("ACCESS_KEY"):
            abort(403, description="Invalid key.")
        return await func(*args, **kwargs)
    return decorated_function


@app.route("/skip-song/<string:key>/<string:user_id>/<string:song_id>/<string:mood>", methods=["GET"])
@verify_request
async def skip_song(user_id: str, song_id: str, mood: str):
    try:
        return jsonify({
            "success": True,
            "result": HistoryService.skip_song(user_id, song_id, mood)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/search/<string:key>/<string:query>/<int:limit>/<string:mood>", methods=["GET"])
@verify_request
async def search(query: str, limit: int, mood: str):
    try:
        result, message = await SpotifyService.search(query, limit, mood)
        if message == "":
            return jsonify({
                "success": True,
                "result": result,
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/finish-song/<string:key>/<string:user_id>/<string:song_id>/<string:mood>", methods=["GET"])
@verify_request
async def finish_song(user_id: str, song_id: str, mood: str):
    try:
        return jsonify({
            "success": True,
            "result": HistoryService.finish_song(user_id, song_id, mood)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/like-song/<string:key>/<string:user_id>/<string:song_id>/<string:mood>/<int:like>", methods=["GET"])
@verify_request
async def like_song(user_id: str, song_id: str, mood: str, like: int):
    try:
        return jsonify({
            "success": True,
            "result": HistoryService.like_song(user_id, song_id, mood, like == 1)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/dislike-song/<string:key>/<string:user_id>/<string:song_id>/<string:mood>/<int:dislike>", methods=["GET"])
@verify_request
async def dislike_song(user_id: str, song_id: str, mood: str, dislike: int):
    try:
        return jsonify({
            "success": True,
            "result": HistoryService.dislike_song(user_id, song_id, mood, dislike == 1)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/favorite-song/<string:key>/<string:user_id>/<string:song_id>/<string:mood>/<int:favorite>", methods=["GET"])
@verify_request
async def favorite_song(user_id: str, song_id: str, mood: str, favorite: int):
    try:
        return jsonify({
            "success": True,
            "result": HistoryService.favorite_song(user_id, song_id, mood, favorite == 1)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/playlist/<string:key>/<string:mood>/<int:limit>", methods=["GET"])
@verify_request
async def playlist(mood: str, limit: int):
    try:
        result, message = await SpotifyService.get_playlist(mood, limit)
        if message == "":
            return jsonify({
                "success": True,
                "result": result,
            })
        else:
            raise Exception(message)
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/next-song/<string:key>/<string:user_id>/<string:mood>", methods=["GET"])
@verify_request
async def next_song(user_id: str, mood: str):
    try:
        playlist, message = await SpotifyService.get_playlist(mood, 20)
        song_ids = [song["id"] for song in playlist]
        history: History = await HistoryService.get_history(user_id)

        song_chances = RecommendationService.get_song_chances(history, mood, song_ids)
        song_id = RandomService.get_key(song_chances, Generator(PCG64()))

        result = None
        for song in playlist:
            if song["id"] == song_id:
                result = song
                break

        return jsonify({
            "result": result,
            "success": True,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "result": str(e),
        })


@app.route("/<string:key>", methods=["GET"])
@verify_request
async def index_secure():
    return jsonify({
        "success": True,
    })


@app.route("/", methods=["GET"])
async def index():
    return jsonify({
        "success": True,
    })


if __name__ == "__main__":
    app.run()