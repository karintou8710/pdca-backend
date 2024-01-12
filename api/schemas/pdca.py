from pydantic import BaseModel, ConfigDict


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


class UpdatePdca(BaseModel):
    plan_content: str
    do_content: str
    check_content: str
    action_content: str
