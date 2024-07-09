from decouple import config, Csv
from typing import Any, Optional

class Config:
    """Central configuration class for the application."""
    
    def __init__(self):
        self._load_config()

    def _load_config(self):
        """Private method to load configuration from environment variables."""
        self.openai_api_key = self._get_config("OPENAI_API_KEY")
        self.twilio_account_sid = self._get_config("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = self._get_config("TWILIO_AUTH_TOKEN")
        self.twilio_number = self._get_config("TWILIO_NUMBER")
        self.firebase_cert_path = self._get_config("FIREBASE_CERT_PATH")
        self.allowed_origins = self._get_config("ALLOWED_ORIGINS", cast=Csv())

    def _get_config(self, key: str, default: Any = None, cast: Any = None) -> Any:
        """
        Retrieve environment variables safely, with optional type casting.
        
        Parameters:
            key (str): The environment variable key.
            default (Any): The default value if the key is not found.
            cast (Any): Optional type cast function.
        
        Returns:
            Any: The value of the environment variable, with casting applied if specified.
        """
        return config(key, default=default, cast=cast)

    def __str__(self):
        """String representation of the current configuration."""
        return (f"OpenAI API Key: {self.openai_api_key}, Twilio Account SID: {self.twilio_account_sid}, "
                f"Twilio Auth Token: {self.twilio_auth_token}, Twilio Number: {self.twilio_number}, "
                f"Firebase Cert Path: {self.firebase_cert_path}, Allowed Origins: {self.allowed_origins}")

# Example usage:
# app_config = Config()
# print(app_config)
