from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class BaseException(Exception):
    code: str = ""
    message: str = ""
    status_code: int = 0
    headers: dict[str, str] | None = None

    def to_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content={"code": self.code, "message": self.message},
            headers=self.headers,
        )


class NoUserException(BaseException):
    code = "no_user"
    message = "user not found"
    status_code = status.HTTP_400_BAD_REQUEST


class UserAlreadyExistException(BaseException):
    code = "user_already_exist"
    message = "user already exist. you can't use this name."
    status_code = status.HTTP_400_BAD_REQUEST


class CredentialsException(BaseException):
    code = "credentials_exception"
    message = "could not validate credentials"
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


def register_exception(app: FastAPI) -> None:
    app.exception_handlers

    @app.exception_handler(NoUserException)
    async def no_user_exception(request: Request, ext: NoUserException) -> JSONResponse:
        return ext.to_response()

    @app.exception_handler(UserAlreadyExistException)
    async def user_already_exist_exception(
        request: Request, ext: UserAlreadyExistException
    ) -> JSONResponse:
        return ext.to_response()
