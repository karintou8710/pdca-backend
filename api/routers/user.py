from fastapi import APIRouter

router = APIRouter()


@router.get("/users/me")
async def read_me() -> None:
    pass


@router.put("/users/{user_id}")
async def update_user() -> None:
    pass


@router.delete("/users/{user_id}")
async def delete_user() -> None:
    pass


@router.post("/signup")
async def sign_up() -> None:
    pass


@router.post("/login")
async def login() -> None:
    pass
