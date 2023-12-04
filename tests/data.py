from api.models.user import User as UserModel
from api.types.response import UserResponse

# model
TEST_USER1 = UserModel(
    id="dd99e701-f778-47b1-a860-f41fb83bb413", name="test", password="password"
)

# response
USER1_RESPONSE: UserResponse = {"id": TEST_USER1.id, "name": TEST_USER1.name}
