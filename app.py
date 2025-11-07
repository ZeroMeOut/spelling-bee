import uuid
import redis
import pickle
import fastapi
from pydantic import BaseModel
from utils.game import SpellingBeeGame
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

## For the first time in my life I am gonna be using Redis for session management
## Gemini told me about it when I should it my first iteration to solve the "singleton" problem in FastAPI apps
## I got an idea of using Redis and I am pretty excited to try it out

app = fastapi.FastAPI()
try:
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)
except Exception as e:
    raise RuntimeError(f"Failed to connect to Redis: {e}")

SESSION_TTL = 3600  ## 1 hour

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, set your domain instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GuessRequest(BaseModel):
    user_id: str
    guess: str

def get_game(user_id: str) -> SpellingBeeGame | None:
    try:
        data = r.get(user_id)
        if not data:
            return None
        return pickle.loads(data)
    except Exception:
        return None

def save_game(user_id: str, game: SpellingBeeGame) -> None:
    try:
        r.setex(user_id, SESSION_TTL, pickle.dumps(game))
    except Exception:
        pass

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/start")
def start_game():
    try:
        user_id = str(uuid.uuid4())
        game = SpellingBeeGame()
        save_game(user_id, game)
        return {"user_id": user_id, "message": "Game started"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to start game: {str(e)}"})


@app.get("/definition")
def get_definition(user_id: str):
    game = get_game(user_id)
    if not game:
        return JSONResponse(status_code=404, content={"error": "Game not found or expired"})
    return {"definition": game.get_current_word_definition()}

@app.get("/audio")
def get_audio(user_id: str):
    game = get_game(user_id)
    if not game:
        return JSONResponse(status_code=404, content={"error": "Game not found or expired"})
    try:
        audio_bytes = game.get_audio_bytes_of_current_word()
        return fastapi.Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to load audio: {str(e)}"})

@app.post("/guess")
def make_guess(request: GuessRequest):
    game = get_game(request.user_id)
    if not game:
        return JSONResponse(status_code=404, content={"error": "Game not found or expired"})
    try:
        result = game.one_game_session(request.guess)
        save_game(request.user_id, game)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to process guess: {str(e)}"})

@app.post("/reset")
def reset_game(user_id: str):
    game = get_game(user_id)
    if not game:
        return JSONResponse(status_code=404, content={"error": "Game not found or expired"})
    try:
        game.reset_game()
        save_game(user_id, game)
        return {"message": "Game reset successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to reset game: {str(e)}"})

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
