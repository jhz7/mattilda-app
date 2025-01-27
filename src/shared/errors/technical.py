class TechnicalError(Exception):
    def __init__(self, code: str, message: str, attributes: dict, cause: Exception):
        self.code = code
        self.message = message
        self.attributes = attributes
        self.cause = cause
        super().__init__(
            f"{self.code}: {self.message}, attributes: {self.attributes}, cause: {self.cause}"
        )
