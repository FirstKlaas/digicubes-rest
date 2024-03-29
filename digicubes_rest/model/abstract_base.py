from pydantic import BaseModel
from responder import Response


class ResponseModel(BaseModel):
    def send_json(self, resp: Response, status_code=200, include=None, exclude=None) -> None:
        resp.status_code = status_code
        resp.mimetype = "application/json"
        resp.text = self.json(
            exclude_none=True,
            exclude_unset=True,
            include=include,
            exclude=exclude,
        )
