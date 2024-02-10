from pydantic import BaseModel, ConfigDict, field_validator

from api.utils import validate_uuid4


class Pdca(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    plan_content: str
    do_content: str
    check_content: str
    action_content: str


class CreatePdca(BaseModel):
    task_id: str
    plan_content: str
    do_content: str
    check_content: str
    action_content: str

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        if not validate_uuid4(v):
            raise ValueError("must be uuid4")

        return v


class UpdatePdca(BaseModel):
    plan_content: str
    do_content: str
    check_content: str
    action_content: str
