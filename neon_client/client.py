from .http_client import Neon_API_V2
from .resources import ResourceCollection

from . import models


class ItemView:
    """A view into a single item."""

    def __init__(self, item, key_id=None):
        self._item = item
        self._key_id = key_id

    @property
    def item(self):
        if self._key_id:
            return getattr(self._item, self._key_id)

        return self._item

    def __getattr__(self, name):
        return getattr(self.item, name)

    def __setattr__(self, name, value):
        if name == "_item":
            return super().__setattr__(name, value)

        return setattr(self.item, name, value)

    def __str__(self):
        return str(self.item)

    def __repr__(self):
        return repr(self.item)

    def __eq__(self, other):
        return self.item == other

    def __ne__(self, other):
        return self.item != other


class CollectionView:
    """A view into a collection of items."""

    def __init__(self, collection, key_ids=None, collection_id=None):
        self.pagination = None

        if not key_ids:
            key_ids = []

        self._key_ids = key_ids
        if collection_id:
            self._collection = getattr(collection, collection_id)
            try:
                self.pagination = collection.pagination
            except AttributeError:
                pass

        else:
            self._collection = collection

    def __iter__(self):
        return iter(self._collection)

    def __getitem__(self, key):
        for k in self._key_ids:
            for item in self._collection:
                if str(getattr(item, k)) == str(key):
                    return item

        return self._collection[key]

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        return repr(self._collection)

    def __str__(self):
        return str(self._collection)

    def __contains__(self, item):
        return item in self._collection

    def __eq__(self, other):
        return self._collection == other

    def __ne__(self, other):
        return self._collection != other


class NeonClient:
    def __init__(self, api_key: str, **kwargs):
        self.api = Neon_API_V2(api_key, **kwargs)
        self.resources = ResourceCollection(self.api)

    def me(self):
        return self.resources.users.get_current_user_info()

    def api_keys(self):
        """Get a list of API keys."""

        return CollectionView(self.resources.api_keys.get_list(), key_ids=["id"])

    def projects(self, shared=False, **kwargs):
        """Get a list of projects."""

        a = self.resources.projects.get_list(shared=shared, **kwargs)
        print(a)
        exit()

        return CollectionView(
            self.resources.projects.get_list(shared=shared, **kwargs),
            key_ids=["id", "name"],
            collection_id="projects",
        )

    def project(self, project_id: str, **kwargs):
        """Get a single project."""

        return ItemView(
            self.resources.projects.get(project_id, **kwargs), key_id="project"
        )

    def project_create(self, **kwargs):
        return ItemView(self.resources.projects.create(**kwargs), key_id="project")

    def project_delete(self, project_id: str, **kwargs):
        return ItemView(
            self.resources.projects.delete(project_id, **kwargs), key_id="project"
        )

    def databases(self, project_id: str, branch_id: str, **kwargs):
        return CollectionView(
            self.resources.databases.get_list(project_id, branch_id, **kwargs),
            key_ids=["id"],
            collection_id="databases",
        )

    def database(self, project_id: str, database_id: str, **kwargs):
        return ItemView(
            self.resources.databases.get(project_id, database_id, **kwargs),
            key_id="database",
        )

    def branches(self, project_id: str, **kwargs):
        return CollectionView(
            self.resources.branches.get_list(project_id, **kwargs),
            key_ids=["id", "name"],
            collection_id="branches",
        )

    def branch(self, project_id: str, branch_id: str):
        return ItemView(
            self.resources.branches.get(project_id, branch_id),
            key_id="branch",
        )

    def branch_create(self, project_id: str, **kwargs):
        return ItemView(
            self.resources.branches.create(project_id, **kwargs),
            key_id="branch",
        )

    def branch_delete(self, project_id: str, branch_id: str, **kwargs):
        return ItemView(
            self.resources.branches.delete(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def branch_update(self, project_id: str, branch_id: str, **kwargs):
        # TODO: untested.
        return ItemView(
            self.resources.branches.update(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def branch_rename(self, project_id: str, branch_id: str, **kwargs):
        # TODO: untested.
        return ItemView(
            self.resources.branches.rename(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def branch_add_compute(self, project_id: str, branch_id: str, **kwargs):
        # TODO: untested.
        return ItemView(
            self.resources.branches.add_compute(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def branch_remove_compute(self, project_id: str, branch_id: str, **kwargs):
        # TODO: untested.
        return ItemView(
            self.resources.branches.remove_compute(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def branch_set_primary(self, project_id: str, branch_id: str, **kwargs):
        # TODO: untested.
        return ItemView(
            self.resources.branches.set_primary(project_id, branch_id, **kwargs),
            key_id="branch",
        )

    def get_connection_string(self, project_id: str, branch_id: str, database_id: str):
        # TODO: implement this.
        return self.resources.databases.get_connection_string(
            project_id,
            branch_id,
            database_id,
        )

    # def branch_create(self, project_id: str, **kwargs):
    #     return ItemView(
    #         self.resources.branches.create(project_id, **kwargs),
    #         key_id="branch",
    #     )
