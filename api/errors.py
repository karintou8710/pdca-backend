from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
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


# 400
class NoUserException(BaseException):
    code = "no_user"
    message = "user not found."
    status_code = status.HTTP_404_NOT_FOUND


class RequestValidationException(BaseException):
    code = "validation_error"
    message = "failed to validation."
    status_code = status.HTTP_400_BAD_REQUEST


class UserAlreadyExistException(BaseException):
    code = "user_already_exist"
    message = "user already exist. you can't use this name."
    status_code = status.HTTP_400_BAD_REQUEST


class LoginValidationException(BaseException):
    code = "login_validation"
    message = "incorrect username or password."
    status_code = status.HTTP_400_BAD_REQUEST
    headers = {"WWW-Authenticate": "Bearer"}


# 401
class NoBearerHeaderException(BaseException):
    code = "not_authenticated"
    message = "not authenticated."
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class CredentialsException(BaseException):
    code = "credentials_exception"
    message = "could not validate credentials."
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class ExpiredSignatureException(BaseException):
    code = "expired_signature"
    message = "jwt expired."
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

    @app.exception_handler(NoBearerHeaderException)
    async def nobearer_header_exception(
        request: Request, ext: NoBearerHeaderException
    ) -> JSONResponse:
        return ext.to_response()

    @app.exception_handler(CredentialsException)
    async def credentials_exception(
        request: Request, ext: CredentialsException
    ) -> JSONResponse:
        return ext.to_response()

    @app.exception_handler(ExpiredSignatureException)
    async def expired_signature_exception(
        request: Request, ext: ExpiredSignatureException
    ) -> JSONResponse:
        return ext.to_response()

    @app.exception_handler(LoginValidationException)
    async def login_validation_exception(
        request: Request, ext: LoginValidationException
    ) -> JSONResponse:
        return ext.to_response()

    @app.exception_handler(RequestValidationError)
    async def validation_exception(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # TODO: 詳細メッセージのスキーマを考える
        err = RequestValidationException()
        return err.to_response()
