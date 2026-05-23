from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import httpx


class Response:
    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self._response.headers

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def text(self) -> str:
        return self._response.text

    @property
    def cookies(self) -> httpx.Cookies:
        return self._response.cookies

    def json(self) -> Any:
        return self._response.json()

    def iter_lines(self) -> Iterator[str]:
        yield from self._response.iter_lines()

    def raise_for_status(self) -> None:
        self._response.raise_for_status()

    def close(self) -> None:
        self._response.close()


class Session:
    def __init__(
        self,
        *,
        impersonate: str | None = None,
        verify: bool = True,
        proxy: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **_: Any,
    ) -> None:
        self.impersonate = impersonate
        self.headers: dict[str, str] = dict(headers or {})
        kwargs: dict[str, Any] = {"verify": verify, "follow_redirects": True}
        if proxy:
            kwargs["proxy"] = proxy
        if timeout is not None:
            kwargs["timeout"] = timeout
        self._client = httpx.Client(**kwargs)

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        kwargs.pop("impersonate", None)
        stream = bool(kwargs.pop("stream", False))
        follow_redirects = kwargs.pop("allow_redirects", None)
        headers = dict(self.headers) | dict(kwargs.pop("headers", {}) or {})
        request = self._client.build_request(method, url, headers=headers, **kwargs)
        send_kwargs: dict[str, Any] = {"stream": stream}
        if follow_redirects is not None:
            send_kwargs["follow_redirects"] = bool(follow_redirects)
        return Response(self._client.send(request, **send_kwargs))

    def get(self, url: str, **kwargs: Any) -> Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Session:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def request(method: str, url: str, **kwargs: Any) -> Response:
    with Session(
        verify=bool(kwargs.pop("verify", True)),
        proxy=kwargs.pop("proxy", None),
        impersonate=kwargs.pop("impersonate", None),
    ) as session:
        response = session.request(method, url, **kwargs)
        _ = response.content
        return response


def get(url: str, **kwargs: Any) -> Response:
    return request("GET", url, **kwargs)


def post(url: str, **kwargs: Any) -> Response:
    return request("POST", url, **kwargs)


def put(url: str, **kwargs: Any) -> Response:
    return request("PUT", url, **kwargs)


def delete(url: str, **kwargs: Any) -> Response:
    return request("DELETE", url, **kwargs)


def patch(url: str, **kwargs: Any) -> Response:
    return request("PATCH", url, **kwargs)


exceptions = SimpleNamespace(RequestException=httpx.RequestError)
