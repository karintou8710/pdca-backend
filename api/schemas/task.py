from pydantic import BaseModel, ConfigDict


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
