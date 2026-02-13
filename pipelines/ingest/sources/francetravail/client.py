import json
import os
import time
from typing import Any, Dict, Optional
from urllib import request, parse


class FranceTravailClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("FT_API_BASE_URL", "").rstrip("/")
        self.token_url = os.getenv("FT_API_TOKEN_URL", "")
        self.client_id = os.getenv("FT_API_CLIENT_ID", "")
        self.client_secret = os.getenv("FT_API_CLIENT_SECRET", "")
        self.search_url = os.getenv("FT_API_SEARCH_URL", "")
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _request_json(self, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, data: Optional[bytes] = None) -> Dict[str, Any]:
        payload = data
        req = request.Request(url, data=payload, method=method)
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        with request.urlopen(req, timeout=60) as response:
            return parse_json(response.read().decode("utf-8"))

    def _get_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expiry:
            return self._token

        if not self.token_url:
            raise ValueError("FT_API_TOKEN_URL is required")

        scope = os.getenv("FT_API_SCOPE", "").strip()
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if scope:
            body["scope"] = scope
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = self._request_json(
            self.token_url,
            method="POST",
            headers=headers,
            data=parse.urlencode(body).encode("utf-8"),
        )
        token = payload.get("access_token")
        expires_in = float(payload.get("expires_in", 3600))
        if not token:
            raise ValueError("France Travail token missing in response")
        self._token = token
        self._token_expiry = now + max(expires_in - 30, 60)
        return token

    def search_offers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.search_url:
            raise ValueError("FT_API_SEARCH_URL is required")
        token = self._get_token()
        query = parse.urlencode(params)
        url = f"{self.search_url}?{query}"
        headers = {"Authorization": f"Bearer {token}"}
        return self._request_json(url, headers=headers)


def parse_json(payload: str) -> Dict[str, Any]:
    return json.loads(payload)
