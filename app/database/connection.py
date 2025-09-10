from supabase import create_client, Client
from ..core.config import settings


class SupabaseConnection:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseConnection, cls).__new__(cls)
        return cls._instance

    def get_client(self) -> Client:
        if self._client is None:
            self._client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_KEY
            )
        return self._client

    def get_service_client(self) -> Client:
        return create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

supabase_connection = SupabaseConnection()


def get_supabase() -> Client:
    return supabase_connection.get_client()


def get_supabase_admin() -> Client:
    return supabase_connection.get_service_client()
