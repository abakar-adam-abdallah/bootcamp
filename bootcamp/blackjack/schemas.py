# from typing import List, Optional
# from ninja import Schema, ModelSchema
# from .models import Student, Game, Player


# # ---------- Students ----------
# class StudentIn(Schema):
#     name: str
#     email: str


# class StudentOut(ModelSchema):
#     class Meta:
#         model = Student
#         fields = ["id", "name", "email", "created_at"]


# # ---------- Games / Players ----------
# class GameIn(Schema):
#     name: str


# class PlayerIn(Schema):
#     name: str


# class PlayerOut(ModelSchema):
#     game_id: int  # on expose l'id du game
#     class Meta:
#         model = Player
#         fields = ["id", "name", "score", "stand", "game_id"]


# class GameListItem(Schema):
#     id: int
#     name: str
#     turn: int
#     ended: bool


# class GameOut(Schema):
#     id: int
#     name: str
#     turn: int
#     ended: bool
#     players: List[PlayerOut]


# class PlayInput(Schema):
#     add_score: Optional[int] = 0
#     stand: Optional[bool] = False


# class Msg(Schema):
#     detail: str
# ------------------------

from datetime import datetime
from typing import List, Optional
from ninja import Schema
from pydantic import Field, ConfigDict


class Msg(Schema):
    detail: str


# ---------- Students ----------
class StudentIn(Schema):
    name: str
    email: str


class StudentOut(Schema):
    # permet d’hydrater le schéma depuis un objet Django
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


# ---------- Games / Players ----------
class GameIn(Schema):
    name: str


class PlayerIn(Schema):
    name: str


class PlayerOut(Schema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    score: int
    stand: bool
    game_id: int


class GameOut(Schema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    turn: int
    ended: bool
    # IMPORTANT: pas de liste mutable par défaut
    players: List[PlayerOut] = Field(default_factory=list)


class GameListItem(Schema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    turn: int
    ended: bool


class PlayInput(Schema):
    add_score: Optional[int] = 0
    stand: Optional[bool] = False
