from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str


class CreateTask(BaseModel):
    title: str = Field(min_length=1)
