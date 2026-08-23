import os
import time
import requests
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class InstagramAPI:
    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

        if not self.access_token or not self.ig_account_id:
            raise ValueError(
                "Configure META_ACCESS_TOKEN e INSTAGRAM_BUSINESS_ACCOUNT_ID no .env"
            )

    def _url(self, path: str) -> str:
        return f"{GRAPH_API_BASE}/{path}"

    def _params(self, extra: dict = None) -> dict:
        base = {"access_token": self.access_token}
        if extra:
            base.update(extra)
        return base

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def _get(self, path: str, params: dict = None) -> dict:
        r = requests.get(self._url(path), params=self._params(params))
        r.raise_for_status()
        return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def _post(self, path: str, data: dict = None) -> dict:
        r = requests.post(self._url(path), params=self._params(), json=data or {})
        r.raise_for_status()
        return r.json()

    def get_account_info(self) -> dict:
        return self._get(
            self.ig_account_id,
            {"fields": "id,username,followers_count,media_count,biography"},
        )

    def create_image_container(self, image_url: str, caption: str) -> str:
        data = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.access_token,
        }
        result = requests.post(
            self._url(f"{self.ig_account_id}/media"), data=data
        )
        result.raise_for_status()
        return result.json()["id"]

    def create_carousel_item(self, image_url: str) -> str:
        data = {
            "image_url": image_url,
            "is_carousel_item": True,
            "access_token": self.access_token,
        }
        result = requests.post(
            self._url(f"{self.ig_account_id}/media"), data=data
        )
        result.raise_for_status()
        return result.json()["id"]

    def create_carousel_container(self, children_ids: list[str], caption: str) -> str:
        data = {
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": self.access_token,
        }
        result = requests.post(
            self._url(f"{self.ig_account_id}/media"), data=data
        )
        result.raise_for_status()
        return result.json()["id"]

    def publish_container(self, container_id: str) -> str:
        data = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }
        result = requests.post(
            self._url(f"{self.ig_account_id}/media_publish"), data=data
        )
        result.raise_for_status()
        return result.json()["id"]

    def post_image(self, image_url: str, caption: str) -> str:
        container_id = self.create_image_container(image_url, caption)
        time.sleep(3)
        return self.publish_container(container_id)

    def post_carousel(self, image_urls: list[str], caption: str) -> str:
        item_ids = [self.create_carousel_item(url) for url in image_urls]
        time.sleep(5)
        container_id = self.create_carousel_container(item_ids, caption)
        time.sleep(5)
        return self.publish_container(container_id)

    def get_recent_media(self, limit: int = 10) -> list[dict]:
        result = self._get(
            f"{self.ig_account_id}/media",
            {"fields": "id,caption,media_type,timestamp,like_count,comments_count", "limit": limit},
        )
        return result.get("data", [])

    def get_insights(self, media_id: str) -> dict:
        return self._get(
            f"{media_id}/insights",
            {"metric": "reach,impressions,engagement,saved"},
        )
