import string
from dataclasses import asdict, dataclass
from typing import (
    TYPE_CHECKING,
    Generator,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import requests

from soundcloud.resource.base import BaseData
from soundcloud.resource.graphql import UserInteraction

if TYPE_CHECKING:
    from soundcloud.soundcloud import SoundCloud

try:
    from typing import get_args, get_origin
except ImportError:
    # get_args and get_origin shim for version < 3.8
    def get_args(tp):
        return getattr(tp, "__args__", ())

    def get_origin(tp):
        return getattr(tp, "__origin__", None)


from urllib.parse import parse_qs, urljoin, urlparse

T = TypeVar("T", bound=BaseData)


@dataclass
class Request(Generic[T]):

    base = "https://api-v2.soundcloud.com"
    format_url: str
    return_type: T

    def _format_url_and_remove_params(self, kwargs):
        format_args = {
            tup[1]
            for tup in string.Formatter().parse(self.format_url)
            if tup[1] is not None
        }
        args = {}
        for k in list(kwargs.keys()):
            if k in format_args:
                args[k] = kwargs.pop(k)
        return self.base + self.format_url.format(**args)

    def _convert_dict(self, d):
        union = get_origin(self.return_type) is Union
        if union:
            for t in get_args(self.return_type):
                try:
                    return t.from_dict(d)
                except:
                    pass
        else:
            return self.return_type.from_dict(d)
        raise ValueError(f"Could not convert {d} to type {self.return_type}")

    def __call__(self, client: "SoundCloud", use_auth=True, **kwargs) -> Optional[T]:
        """
        Requests the resource at the given url with
        parameters given by kwargs. Converts the resource
        to type T and returns it. If the
        resource does not exist, returns None
        """
        resource_url = self._format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = client.client_id
        headers = client._get_default_headers()
        if use_auth and client._authorization is not None:
            headers["Authorization"] = client._authorization
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return None
            r.raise_for_status()
            return self._convert_dict(r.json())


@dataclass
class CollectionRequest(Request, Generic[T]):

    def __call__(
        self,
        client: "SoundCloud",
        use_auth=True,
        offset: str = None,
        limit: int = None,
        **kwargs,
    ) -> Generator[T, None, None]:
        """
        Yields resources from the given url with
        parameters given by kwargs. Converts the resources
        to type T before yielding
        """
        resource_url = self._format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = client.client_id
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        headers = client._get_default_headers()
        if use_auth and client._authorization is not None:
            headers["Authorization"] = client._authorization
        while resource_url:
            with requests.get(resource_url, params=params, headers=headers) as r:
                if r.status_code in (400, 404, 500):
                    return
                r.raise_for_status()
                data = r.json()
                for resource in data["collection"]:
                    yield self._convert_dict(resource)
                resource_url = data.get("next_href", None)
                parsed = urlparse(resource_url)
                params = parse_qs(parsed.query)
                params["client_id"] = (
                    client.client_id
                )  # next_href doesn't contain client_id
                resource_url = urljoin(resource_url, parsed.path)


@dataclass
class ListRequest(Request, Generic[T]):
    """
    Requests the resource list at the given url with
    parameters given by kwargs. Converts the resources
    to type T and returns them.
    """

    def __call__(self, client: "SoundCloud", use_auth=True, **kwargs) -> List[T]:
        resource_url = self._format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = client.client_id
        headers = client._get_default_headers()
        if use_auth and client._authorization is not None:
            headers["Authorization"] = client._authorization
        resources = []
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return []
            r.raise_for_status()
            for resource in r.json():
                resources.append(self._convert_dict(resource))
        return resources


# GraphQL requests

Q = TypeVar("Q")


@dataclass
class GraphQLRequest(Request, Generic[Q, T]):
    base = "https://graph.soundcloud.com/graphql"
    operation_name: str
    query_arg_type: Q
    query_template_str: str

    def __call__(
        self, client: "SoundCloud", query_params: Q, use_auth=True
    ) -> Optional[T]:
        params = {}
        params["client_id"] = client.client_id
        headers = client._get_default_headers()
        headers["Apollographql-Client-Name"] = "v2"
        if use_auth and client._authorization is not None:
            headers["Authorization"] = client._authorization

        data = {
            "operationName": self.operation_name,
            "query": self.query_template_str,
            "variables": asdict(query_params),
        }

        with requests.post(self.base, json=data, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return None
            r.raise_for_status()
            return self._convert_dict(r.json()["data"])


@dataclass
class UserInteractionsQueryResult(BaseData):
    user: List[UserInteraction]
    creator: List[UserInteraction]


@dataclass
class UserInteractionsQueryParams:
    createdByProfileUrn: str
    interactionTypeUrn: str
    parentUrn: str
    targetUrns: List[str]


UserInteractionsRequest = GraphQLRequest[
    UserInteractionsQueryParams, UserInteractionsQueryResult
](
    "",
    UserInteractionsQueryResult,
    "UserInteractions",
    UserInteractionsQueryParams,
    (
        "query UserInteractions(\n"
        "   $parentUrn: String!\n"
        "   $interactionTypeUrn: String!\n"
        "   $targetUrns: [String!]!\n"
        "   $createdByProfileUrn: String\n"
        ") {\n"
        "   user: userInteractions(\n"
        "       parentUrn: $parentUrn\n"
        "       interactionTypeUrn: $interactionTypeUrn\n"
        "       targetUrns: $targetUrns\n"
        "   ) {\n"
        "       interactionCounts {\n"
        "           count\n"
        "           interactionTypeValueUrn\n"
        "       }\n"
        "       interactionTypeUrn\n"
        "       targetUrn\n"
        "       userInteraction\n"
        "   }\n"
        "\n"
        "   creator: userInteractions(\n"
        "       parentUrn: $parentUrn\n"
        "       interactionTypeUrn: $interactionTypeUrn\n"
        "       targetUrns: $targetUrns\n"
        "       createdByProfileUrn: $createdByProfileUrn\n"
        "   ) {\n"
        "       interactionCounts {\n"
        "           count\n"
        "           interactionTypeValueUrn\n"
        "       }\n"
        "       interactionTypeUrn\n"
        "       targetUrn\n"
        "       userInteraction\n"
        "   }\n"
        "}"
    ),
)
