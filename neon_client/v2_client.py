from .http_client import Neon_API_V2
from .resources import ResourceCollection

from . import openapi_models


class BaseNeonItem:
    def __repr__(self):
        return str(self)


class NeonUser(BaseNeonItem, openapi_models.CurrentUserAuthAccount):
    @classmethod
    def from_get_response(cls, r):
        """Create a NeonUser from an API response."""

        # TODO: is this the right way to do this?
        me = r.auth_accounts[0]

        return cls.model_validate(me.model_dump())

    def __str__(self):
        return f"<NeonUser email={self.email}>"


class CollectionView:
    def __init__(self, collection, key_ids=None):
        if not key_ids:
            key_ids = []

        self._key_ids = key_ids
        self._collection = collection

    def __iter__(self):
        return iter(self._collection)

    def __getitem__(self, key):
        for k in key_ids:
            for item in self._collection:
                if getattr(item, k) == key:
                    return item

        return self._collection[key]

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        return repr(self._collection)


class NeonAPIKey(BaseNeonItem, openapi_models.ApiKeysListResponseItem):
    @classmethod
    def from_list_response(cls, r, *, neon):
        """Create a list of APIKeys from an API response."""

        def gen():
            for key in r:
                k = cls.model_validate(key.model_dump())
                k.neon = neon

                yield k

        return [g for g in gen()]

    def __str__(self):
        return f"<NeonAPIKey id={self.id}>"

    def revoke(self, *, neon):
        """Revoke this API key."""

        return bool(neon.resources.api_keys.revoke(self.id))


class NeonClient:
    def __init__(self, api_key: str, **kwargs):
        self.api = Neon_API_V2(api_key, **kwargs)
        self.resources = ResourceCollection(self.api)

    @property
    def me(self):
        user = self.resources.users.get_current_user_info()
        return NeonUser.from_get_response(user)

    @property
    def api_keys(self):
        keys = self.resources.api_keys.get_list()
        return CollectionView(
            NeonAPIKey.from_list_response(keys, neon=self), key_ids=["id"]
        )
