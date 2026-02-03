from typing import Optional


class BaseHTTPException(Exception):
    error_code: str = "unknown"
    data: Optional[dict] = None
    code: int = 500

    def __init__(self, description=None, response=None):
        super().__init__(description)

        self.data = {
            "code": self.error_code,
            "message": description,
            "status": self.code,
        }
