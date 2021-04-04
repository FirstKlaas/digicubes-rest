from pydantic import BaseModel, PositiveInt


class BearerTokenData(BaseModel):
    bearer_token: str
    user_id: PositiveInt
    lifetime: int  # Lifetime (max age) of this token
    expires_at: str  # expiration date as iso formatted string
