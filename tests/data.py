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
