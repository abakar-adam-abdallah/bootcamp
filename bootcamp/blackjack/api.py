from ninja import NinjaAPI, Schema
from typing import List, Optional
from datetime import datetime

api = NinjaAPI(title="Demo API")

# stockage très simple en mémoire (débutant)
STUDENTS = []
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
