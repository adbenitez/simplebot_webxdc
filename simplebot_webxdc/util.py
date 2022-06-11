import functools
import zipfile
from io import BytesIO
from typing import List

import requests
import toml
from bs4 import BeautifulSoup
from cachelib import BaseCache, FileSystemCache, NullCache
from simplebot.bot import DeltaBot

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
    }
)
session.request = functools.partial(session.request, timeout=15)  # type: ignore
_cache: BaseCache = NullCache()


def init_cache(path: str) -> None:
    global _cache  # noqa
    _cache = FileSystemCache(path, threshold=2000, default_timeout=60 * 60 * 24 * 90)


def get_urls(bot: DeltaBot) -> List[str]:
    scope = __name__.split(".", maxsplit=1)[0]
    urls = bot.get("urls", scope=scope)
    return urls.split("\n") if urls else []


def set_urls(bot: DeltaBot, urls: List[str]) -> None:
    bot.set("urls", "\n".join(urls), scope=__name__.split(".", maxsplit=1)[0])


def get_webxdc(bot: DeltaBot, url: str) -> tuple:
    if url not in get_urls(bot):
        return None, None
    cached_url, xdcfile = _get_webxdc(url)
    if not cached_url:
        get_metadata(url)
        cached_url, xdcfile = _get_webxdc(url)
    return cached_url, xdcfile


def _get_webxdc(url: str) -> tuple:
    return _cache.get(f"xdc+{url}") or (None, None)


def _set_webxdc(url: str, data: tuple) -> None:
    _cache.set(f"xdc+{url}", data)


def reset_metadata(url: str) -> None:
    _cache.set(url, None)


def get_metadata(project_url: str) -> dict:
    meta = _cache.get(project_url)  # noqa
    if not meta:
        meta = {
            "name": "Unknow",
            "publisher": "Unknow",
            "version": "",
            "description": "",
            "id": project_url,
        }
        if project_url.startswith("https://github.com/"):
            url = f"{project_url}/releases"
            meta["publisher"] = project_url.split("https://github.com/")[-1].split("/")[
                0
            ]
        else:
            url = project_url
        with session.get(url) as resp:
            soup = BeautifulSoup(resp.text, "html.parser")
            file_url = (
                (soup.find(class_="Box-footer") or soup).find(
                    "a", attrs={"href": lambda href: href and href.endswith(".xdc")}
                )
                or {}
            ).get("href")
            if not file_url:
                return {}
            if file_url.startswith("/"):
                scheme, root = project_url.split("://", maxsplit=1)
                root = root.split("/", maxsplit=1)[0]
                file_url = f"{scheme}://{root}{file_url}"
            meta["file_url"] = file_url
            if project_url.startswith("https://github.com/"):
                desc = soup.find("meta", attrs={"name": "description"})
                if desc:
                    meta["description"] = desc["content"].split(" - GitHub - ")[0]
                    _parts = meta["description"].split(" Contribute to ", maxsplit=1)
                    if len(_parts) != 1 and "GitHub" in _parts[1]:
                        meta["description"] = _parts[0]
                meta["version"] = file_url.rsplit("/", maxsplit=2)[-2]

        cached_url, xdcfile = _get_webxdc(project_url)
        if file_url != cached_url:
            with session.get(file_url) as resp:
                xdcfile = resp.content
                _set_webxdc(project_url, (file_url, xdcfile))

        meta.update(_get_metadata_from_file(BytesIO(xdcfile)))
        _cache.set(project_url, meta, timeout=60 * 60 * 24)
    return meta


def _get_metadata_from_file(file) -> dict:
    with zipfile.ZipFile(file) as xdc:
        with xdc.open("manifest.toml") as manifest:
            meta = toml.loads(manifest.read().decode())
        for ext in ("png", "jpg"):
            try:
                with xdc.open("icon." + ext) as icon:
                    meta["icon"] = (ext, icon.read())
                    break
            except KeyError:
                pass
    return meta
