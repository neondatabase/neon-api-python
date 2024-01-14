from .http_client import Neon_API_V2
from .resources import ResourceCollection


class NeonClient:
    def __init__(self, api_key: str, **kwargs):
        self.api = Neon_API_V2(api_key, **kwargs)
        self.resources = ResourceCollection(self.api)

        # self.api_keys = APIKeyResource(self.api)
        # self.users = UserResource(self.api)
        # self.projects = ProjectResource(self.api)
        # self.databases = DatabaseResource(self.api)
