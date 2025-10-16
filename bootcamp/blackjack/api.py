

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field
from ninja import NinjaAPI, Schema

api = NinjaAPI(title="Demo API")

# =========================
#  STUDENTS (mémoire)
# =========================
STUDENTS: List[dict] = []
SEQ = 0


class StudentIn(Schema):
    name: str
    email: str


class StudentOut(Schema):
    id: int
    name: str
    email: str
    created_at: datetime


class Msg(Schema):
    detail: str


@api.get("/students", response=List[StudentOut])
def list_students(request):
    return STUDENTS


@api.post("/students", response={201: StudentOut})
def create_student(request, data: StudentIn):
    global SEQ
    SEQ += 1
    item = {
        "id": SEQ,
        "name": data.name,
        "email": data.email,
        "created_at": datetime.utcnow(),
    }
    STUDENTS.append(item)
    return 201, item


@api.delete("/students/{pk}", response={204: None, 404: Msg})
def delete_student(request, pk: int):
    for i, s in enumerate(STUDENTS):
        if s["id"] == pk:
            STUDENTS.pop(i)
            return 204, None
    return 404, {"detail": "Student not found"}


# =========================
#  GAMES & PLAYERS (mémoire)
# =========================
GAMES: Dict[int, Dict[str, Any]] = {}     # id -> game dict
PLAYERS: Dict[int, Dict[str, Any]] = {}   # id -> player dict
GAME_SEQ = 0
PLAYER_SEQ = 0


# ---- Schémas ----
class GameIn(Schema):
    name: str


class PlayerIn(Schema):
    name: str


class PlayerOut(Schema):
    id: int
    name: str
    score: int
    stand: bool
    game_id: int


class GameOut(Schema):
    id: int
    name: str
    turn: int
    ended: bool
    # Surtout pas "=[]" (mutable) → utiliser default_factory
    players: List[PlayerOut] = Field(default_factory=list)


class GameListItem(Schema):
    id: int
    name: str
    turn: int
    ended: bool


class PlayInput(Schema):
    # très simple : on ajoute du score OU on “stand”
    add_score: Optional[int] = 0
    stand: Optional[bool] = False


# ---- Helpers ----
def _game_or_404(gid: int):
    game = GAMES.get(gid)
    if not game:
        return None, (404, {"detail": "Game not found"})
    return game, None


def _player_or_404(pid: int):
    p = PLAYERS.get(pid)
    if not p:
        return None, (404, {"detail": "Player not found"})
    return p, None


def _serialize_player(p: dict) -> PlayerOut:
    return PlayerOut(
        id=p["id"],
        name=p["name"],
        score=p["score"],
        stand=p["stand"],
        game_id=p["game_id"],
    )


def _serialize_game_detail(g: dict) -> GameOut:
    players = [
        _serialize_player(p)
        for p in PLAYERS.values()
        if p["game_id"] == g["id"]
    ]
    return GameOut(
        id=g["id"],
        name=g["name"],
        turn=g["turn"],
        ended=g["ended"],
        players=players,
    )


# ---- Endpoints Games ----
@api.post("/games", response={201: GameOut})
def create_game(request, data: GameIn):
    global GAME_SEQ
    GAME_SEQ += 1
    g = {
        "id": GAME_SEQ,
        "name": data.name.strip(),
        "turn": 0,
        "ended": False,
    }
    GAMES[g["id"]] = g
    return 201, _serialize_game_detail(g)


@api.get("/games", response=List[GameListItem])
def list_games(request):
    return [GameListItem(**g) for g in GAMES.values()]  # id, name, turn, ended


@api.get("/games/{gid}", response={200: GameOut, 404: Msg})
def get_game(request, gid: int):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload
    return _serialize_game_detail(game)


@api.post("/games/{gid}/start", response={200: GameOut, 404: Msg})
def start_game(request, gid: int):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload
    game["turn"] = 0
    game["ended"] = False
    return _serialize_game_detail(game)


@api.post("/games/{gid}/end", response={200: GameOut, 404: Msg})
def end_game(request, gid: int):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload
    game["ended"] = True
    return _serialize_game_detail(game)


# ---- Endpoints Players ----
@api.post("/games/{gid}/players", response={201: PlayerOut, 404: Msg})
def add_player(request, gid: int, data: PlayerIn):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload

    global PLAYER_SEQ
    PLAYER_SEQ += 1
    p = {
        "id": PLAYER_SEQ,
        "name": data.name.strip(),
        "score": 0,
        "stand": False,
        "game_id": gid,
    }
    PLAYERS[p["id"]] = p
    return 201, _serialize_player(p)


@api.post("/games/{gid}/players/{pid}/play", response={200: PlayerOut, 404: Msg})
def play_turn(request, gid: int, pid: int, data: PlayInput):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload

    player, err = _player_or_404(pid)
    if err:
        status, payload = err
        return status, payload

    if player["game_id"] != game["id"]:
        return 404, {"detail": "Player does not belong to this game"}

    # logique minimaliste : on modifie le score, on peut mettre stand=True,
    # et on avance le tour si on a joué
    if data.add_score:
        player["score"] = max(0, player["score"] + int(data.add_score))
        game["turn"] += 1

    if data.stand:
        player["stand"] = True

    return _serialize_player(player)


@api.delete("/games/{gid}/players/{pid}", response={204: None, 404: Msg})
def remove_player(request, gid: int, pid: int):
    game, err = _game_or_404(gid)
    if err:
        status, payload = err
        return status, payload

    player, err = _player_or_404(pid)
    if err:
        status, payload = err
        return status, payload

    if player["game_id"] != game["id"]:
        return 404, {"detail": "Player does not belong to this game"}

    PLAYERS.pop(pid, None)
    return 204, None
-----------

from typing import List
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from .models import Student, Game, Player
from .schemas import (
    StudentIn, StudentOut, Msg,
    GameIn, GameOut, GameListItem,
    PlayerIn, PlayerOut, PlayInput
)

api = NinjaAPI(title="Demo API (ORM)")


# =========================
# Students (ORM)
# =========================
@api.get("/students", response=List[StudentOut])
def list_students(request):
    return Student.objects.all()


@api.post("/students", response={201: StudentOut})
def create_student(request, data: StudentIn):
    obj = Student.objects.create(**data.dict())
    return 201, obj


@api.delete("/students/{pk}", response={204: None, 404: Msg})
def delete_student(request, pk: int):
    deleted, _ = Student.objects.filter(pk=pk).delete()
    if deleted:
        return 204, None
    return 404, {"detail": "Student not found"}


# =========================
# Games & Players (ORM)
# =========================
@api.post("/games", response={201: GameOut})
def create_game(request, data: GameIn):
    g = Game.objects.create(name=data.name.strip())
    g = Game.objects.prefetch_related("players").get(pk=g.pk)
    return 201, {
        "id": g.id,
        "name": g.name,
        "turn": g.turn,
        "ended": g.ended,
        "players": [PlayerOut.from_orm(p) for p in g.players.all()],
    }


@api.get("/games", response=List[GameListItem])
def list_games(request):
    return [
        GameListItem(id=g.id, name=g.name, turn=g.turn, ended=g.ended)
        for g in Game.objects.all()
    ]


@api.get("/games/{gid}", response={200: GameOut, 404: Msg})
def get_game(request, gid: int):
    g = Game.objects.prefetch_related("players").filter(pk=gid).first()
    if not g:
        return 404, {"detail": "Game not found"}
    return {
        "id": g.id,
        "name": g.name,
        "turn": g.turn,
        "ended": g.ended,
        "players": [PlayerOut.from_orm(p) for p in g.players.all()],
    }


@api.post("/games/{gid}/start", response={200: GameOut, 404: Msg})
def start_game(request, gid: int):
    g = Game.objects.filter(pk=gid).first()
    if not g:
        return 404, {"detail": "Game not found"}
    g.turn = 0
    g.ended = False
    g.save(update_fields=["turn", "ended"])
    g.refresh_from_db()
    return get_game(request, gid)[1] if isinstance(get_game(request, gid), tuple) else get_game(request, gid)


@api.post("/games/{gid}/end", response={200: GameOut, 404: Msg})
def end_game(request, gid: int):
    g = Game.objects.filter(pk=gid).first()
    if not g:
        return 404, {"detail": "Game not found"}
    g.ended = True
    g.save(update_fields=["ended"])
    g.refresh_from_db()
    return get_game(request, gid)[1] if isinstance(get_game(request, gid), tuple) else get_game(request, gid)


@api.post("/games/{gid}/players", response={201: PlayerOut, 404: Msg})
def add_player(request, gid: int, data: PlayerIn):
    g = Game.objects.filter(pk=gid).first()
    if not g:
        return 404, {"detail": "Game not found"}
    p = Player.objects.create(game=g, name=data.name.strip())
    return 201, p


@api.post("/games/{gid}/players/{pid}/play", response={200: PlayerOut, 404: Msg})
def play_turn(request, gid: int, pid: int, data: PlayInput):
    g = Game.objects.filter(pk=gid).first()
    if not g:
        return 404, {"detail": "Game not found"}
    p = Player.objects.filter(pk=pid, game=g).first()
    if not p:
        return 404, {"detail": "Player not found or not in this game"}

    updated_fields = []
    if data.add_score:
        p.score = max(0, p.score + int(data.add_score))
        updated_fields.append("score")
        g.turn += 1
        g.save(update_fields=["turn"])

    if data.stand:
        p.stand = True
        updated_fields.append("stand")

    if updated_fields:
        p.save(update_fields=updated_fields)

    return p


@api.delete("/games/{gid}/players/{pid}", response={204: None, 404: Msg})
def remove_player(request, gid: int, pid: int):
    # S'assure que le joueur appartient bien au game
    deleted, _ = Player.objects.filter(pk=pid, game_id=gid).delete()
    if deleted:
        return 204, None
    return 404, {"detail": "Player not found"}




# --------------------------------------------------------------
# from typing import List
# from ninja import NinjaAPI
# from django.db.models import Prefetch

# from .models import Student, Game, Player
# from .schemas import (
#     Msg,
#     StudentIn, StudentOut,
#     GameIn, GameOut, GameListItem,
#     PlayerIn, PlayerOut, PlayInput,
# )

# api = NinjaAPI(title="Demo API (ORM)")


# # -------------------------
# # Students (ORM)
# # -------------------------
# @api.get("/students", response=List[StudentOut])
# def list_students(request):
#     return Student.objects.all()


# @api.post("/students", response={201: StudentOut})
# def create_student(request, data: StudentIn):
#     obj = Student.objects.create(**data.dict())
#     return 201, obj


# @api.delete("/students/{pk}", response={204: None, 404: Msg})
# def delete_student(request, pk: int):
#     deleted, _ = Student.objects.filter(pk=pk).delete()
#     if deleted:
#         return 204, None
#     return 404, {"detail": "Student not found"}


# # -------------------------
# # Helpers Games
# # -------------------------
# def _serialize_game_with_players(g: Game) -> GameOut:
#     # g.players est déjà préfetch si on l’a fait dans la vue
#     return GameOut(
#         id=g.id,
#         name=g.name,
#         turn=g.turn,
#         ended=g.ended,
#         players=list(g.players.all()),  # PlayerOut sait lire des objets ORM (from_attributes)
#     )


# # -------------------------
# # Games & Players (ORM)
# # -------------------------
# @api.post("/games", response={201: GameOut})
# def create_game(request, data: GameIn):
#     g = Game.objects.create(name=data.name.strip())
#     g = Game.objects.prefetch_related("players").get(pk=g.pk)
#     return 201, _serialize_game_with_players(g)


# @api.get("/games", response=List[GameListItem])
# def list_games(request):
#     # Pas besoin des joueurs ici
#     return [
#         GameListItem(id=g.id, name=g.name, turn=g.turn, ended=g.ended)
#         for g in Game.objects.all().order_by("id")
#     ]


# @api.get("/games/{gid}", response={200: GameOut, 404: Msg})
# def get_game(request, gid: int):
#     g = Game.objects.prefetch_related("players").filter(pk=gid).first()
#     if not g:
#         return 404, {"detail": "Game not found"}
#     return _serialize_game_with_players(g)


# @api.post("/games/{gid}/start", response={200: GameOut, 404: Msg})
# def start_game(request, gid: int):
#     g = Game.objects.filter(pk=gid).first()
#     if not g:
#         return 404, {"detail": "Game not found"}
#     g.turn = 0
#     g.ended = False
#     g.save(update_fields=["turn", "ended"])
#     g = Game.objects.prefetch_related("players").get(pk=gid)
#     return _serialize_game_with_players(g)


# @api.post("/games/{gid}/end", response={200: GameOut, 404: Msg})
# def end_game(request, gid: int):
#     g = Game.objects.filter(pk=gid).first()
#     if not g:
#         return 404, {"detail": "Game not found"}
#     g.ended = True
#     g.save(update_fields=["ended"])
#     g = Game.objects.prefetch_related("players").get(pk=gid)
#     return _serialize_game_with_players(g)


# @api.post("/games/{gid}/players", response={201: PlayerOut, 404: Msg})
# def add_player(request, gid: int, data: PlayerIn):
#     g = Game.objects.filter(pk=gid).first()
#     if not g:
#         return 404, {"detail": "Game not found"}
#     p = Player.objects.create(game=g, name=data.name.strip())
#     return 201, p


# @api.post("/games/{gid}/players/{pid}/play", response={200: PlayerOut, 404: Msg})
# def play_turn(request, gid: int, pid: int, data: PlayInput):
#     g = Game.objects.filter(pk=gid).first()
#     if not g:
#         return 404, {"detail": "Game not found"}

#     p = Player.objects.filter(pk=pid, game=g).first()
#     if not p:
#         return 404, {"detail": "Player not found or not in this game"}

#     fields = []
#     if data.add_score:
#         p.score = max(0, p.score + int(data.add_score))
#         fields.append("score")
#         g.turn += 1
#         g.save(update_fields=["turn"])

#     if data.stand:
#         p.stand = True
#         fields.append("stand")

#     if fields:
#         p.save(update_fields=fields)

#     return p


# @api.delete("/games/{gid}/players/{pid}", response={204: None, 404: Msg})
# def remove_player(request, gid: int, pid: int):
#     deleted, _ = Player.objects.filter(pk=pid, game_id=gid).delete()
#     if deleted:
#         return 204, None
#     return 404, {"detail": "Player not found"}
