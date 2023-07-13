from datetime import datetime
import secrets

KEY_LENGTH: int = 16


class ApiKey:
    def __init__(
        self,
        name: str,
        description: str,
        created_at: datetime = None,
        valid_until: datetime = None,
    ):
        self.name = name
        self.description = description
        self.created_at = created_at if created_at else datetime.now()
        self.valid_until = (
            valid_until
            if valid_until
            else datetime.now().replace(month=datetime.now().month + 1)
        )

        self.key = self._generate_api_key()

    @staticmethod
    def _generate_api_key():
        return secrets.token_hex(KEY_LENGTH)
