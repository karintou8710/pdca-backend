from uuid import UUID


def validate_uuid4(v: str) -> bool:
    try:
        uuid_obj = UUID(v, version=4)
    except ValueError:
        return False

    return v == str(uuid_obj)
