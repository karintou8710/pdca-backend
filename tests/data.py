from tests.types.response import ErrorResponse

# error response
NOT_AUTHENTICATED_ERROR_RESPONSE: ErrorResponse = {
    "code": "not_authenticated",
    "message": "not authenticated.",
}

EXPIRED_SIGNATURE_ERROR_RESPONSE: ErrorResponse = {
    "code": "expired_signature",
    "message": "jwt expired.",
}

ALREADY_EXIST_ERROR_RESPONSE: ErrorResponse = {
    "code": "user_already_exist",
    "message": "user already exist. you can't use this name.",
}

NO_USER_ERROR_RESPONSE: ErrorResponse = {
    "code": "no_user",
    "message": "user not found.",
}

NO_TASK_ERROR_RESPONSE: ErrorResponse = {
    "code": "no_task",
    "message": "task not found.",
}

CREDENTIAL_ERROR_RESPONSE: ErrorResponse = {
    "code": "credentials_exception",
    "message": "could not validate credentials.",
}

VALIDATION_ERROR_RESPONSE: ErrorResponse = {
    "code": "validation_error",
    "message": "failed to validation.",
}

LOGIN_VALIDATION_ERROR_RESPONSE: ErrorResponse = {
    "code": "login_validation",
    "message": "incorrect username or password.",
}

FORBIDDEN_ERROR_RESPONSE: ErrorResponse = {
    "code": "forbidden",
    "message": "access forbidden.",
}
