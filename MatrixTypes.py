from pydantic import BaseModel


class MatrixRequest(BaseModel):
    prompt: str
    room_id: str
    user_id: str
    event_id: str


class MatrixResponse(BaseModel):
    response: str
    room_id: str
    event_id: str
