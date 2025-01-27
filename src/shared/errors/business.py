class BusinessError(Exception):
    def __init__(self, code: str, message: str, attributes: dict):
        self.code = code
        self.message = message
        self.attributes = attributes
        super().__init__(f"{self.code}: {self.message}, attributes: {self.attributes}")
