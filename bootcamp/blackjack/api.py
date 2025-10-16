from ninja import NinjaAPI, Schema
from typing import Optional, Literal, Dict
import random

api = NinjaAPI(title="Mini Game API")


GAMES: Dict[int, dict] = {}
GAME_ID = 0

#  Schémas de validation 
class StartIn(Schema):
    player: str

class PlayIn(Schema):
    game_id: int
    guess: Literal["heads", "tails"]  # validation très simple

class GameOut(Schema):
    id: int
    player: str
    status: Literal["new", "finished"]
    last_flip: Optional[str] = None
    last_guess: Optional[str] = None
    result: Optional[str] = None        
    wins: int
    losses: int

class Message(Schema):
    detail: str


#  Endpoints
@api.post("/start", response={201: GameOut})
def start(request, data: StartIn):
    """Créer une partie (pile ou face, 1 coup)."""
    global GAME_ID
    GAME_ID += 1
    game = {
        "id": GAME_ID,
        "player": data.player.strip() or "Player",
        "status": "new",
        "last_flip": None,
        "last_guess": None,
        "result": None,
        "wins": 0,
        "losses": 0,
    }
    GAMES[GAME_ID] = game
    return 201, game


@api.post("/play", response={200: GameOut, 404: Message, 409: Message})
def play(request, data: PlayIn):
    """Jouer un coup : deviner heads/tails. Partie ultra courte (un seul coup)."""
    game = GAMES.get(data.game_id)
    if not game:
        return 404, {"detail": "Game not found."}

    if game["status"] == "finished":
        return 409, {"detail": "Game already finished. Start a new one."}

    flip = random.choice(["heads", "tails"])
    game["last_flip"] = flip
    game["last_guess"] = data.guess
    if data.guess == flip:
        game["result"] = "win"
        game["wins"] += 1
    else:
        game["result"] = "lose"
        game["losses"] += 1

    # partie à un seul coup → finie
    game["status"] = "finished"
    return game


@api.get("/{pk}", response={200: GameOut, 404: Message})
def get_game(request, pk: int):
    """Obtenir l'état d'une partie."""
    game = GAMES.get(pk)
    if not game:
        return 404, {"detail": "Game not found."}
    return game
