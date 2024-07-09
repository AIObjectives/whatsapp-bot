import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
import logging

class FirebaseService:
    """Service class for handling Firebase operations."""

    def __init__(self, config: Config):
        self.config = config
        self.client = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials from the provided configuration."""
        try:
            cred = credentials.Certificate(self.config.firebase_cert_path)
            firebase_admin.initialize_app(cred)
            self.client = firestore.client()
            logging.info("Firebase initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase: {e}")
            raise ConnectionError(f"Firebase initialization failed: {e}")

    def get_client(self) -> firestore.Client:
        """Returns the Firestore client."""
        if not self.client:
            raise ConnectionError("Firebase client is not initialized.")
        return self.client

    def __del__(self):
        """Destructor to handle cleanup if necessary."""
        if self.client:
            logging.info("Cleaning up Firebase connections...")
            # Perform cleanup actions here, if necessary.

# Example usage:
# app_config = Config()
# firebase_service = FirebaseService(app_config)
# db_client = firebase_service.get_client()