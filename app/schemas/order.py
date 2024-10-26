from pydantic import BaseModel

class AddSchema(BaseModel):
  user_id: int
  train_id: int
  wagon_id: int
  seat_ids: int