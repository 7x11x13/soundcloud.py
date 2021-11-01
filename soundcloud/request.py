from __future__ import annotations

import string
from dataclasses import dataclass
from typing import (Generator, Generic, Optional, TypeVar, Union, get_args,
                    get_origin)
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from requests import HTTPError

T = TypeVar("T")

@dataclass
class Request(Generic[T]):
    
    base = "https://api-v2.soundcloud.com"
    client: SoundCloud
    format_url: str
    return_type: T
    
    def format_url_and_remove_params(self, kwargs):
        format_args = {tup[1] for tup in string.Formatter().parse(self.format_url) if tup[1] is not None}
        args = {}
        for k in list(kwargs.keys()):
            if k in format_args:
                args[k] = kwargs.pop(k)     
        return self.base + self.format_url.format(**args)
    
    def convert_dict(self, d):
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
    
    def __call__(self, use_auth=True, **kwargs) -> Optional[T]:
        """
        Requests the resource at the given url with
        parameters given by kwargs. Converts the resource
        to type T and returns it. If the
        resource does not exist, returns None
        """
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return None
            r.raise_for_status()
            return self.convert_dict(r.json())

@dataclass
class CollectionRequest(Request, Generic[T]):
    
    def __call__(self, use_auth=True, offset: str = None, limit: int = None, **kwargs) -> Generator[T, None, None]:
        """
        Yields resources from the given url with
        parameters given by kwargs. Converts the resources
        to type T before yielding
        """
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        while resource_url:
            with requests.get(resource_url, params=params, headers=headers) as r:
                if r.status_code in (400, 404, 500):
                    return
                r.raise_for_status()
                data = r.json()
                for resource in data["collection"]:
                    yield self.convert_dict(resource)
                resource_url = data.get("next_href", None)
                parsed = urlparse(resource_url)
                params = parse_qs(parsed.query)
                params["client_id"] = self.client.client_id # next_href doesn't contain client_id
                resource_url = urljoin(resource_url, parsed.path)
                
@dataclass
class ListRequest(Request, Generic[T]):
    """
    Requests the resource list at the given url with
    parameters given by kwargs. Converts the resources
    to type T and returns them.
    """
    def __call__(self, use_auth=True, **kwargs) -> list[T]:
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        resources = []
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return []
            r.raise_for_status()
            for resource in r.json():
                resources.append(self.convert_dict(resource))
        return resources
