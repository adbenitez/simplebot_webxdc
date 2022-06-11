import json
import os
import zipfile
import zlib
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import List

import simplebot
from deltachat import Message
from simplebot.bot import DeltaBot, Replies

from .data import CSS_FILE, HTML_FILE, JS_FILE
from .util import (
    get_metadata,
    get_urls,
    get_webxdc,
    init_cache,
    reset_metadata,
    set_urls,
)

zlib.Z_DEFAULT_COMPRESSION = 9  # type: ignore


@simplebot.hookimpl
def deltabot_init(bot: DeltaBot) -> None:
    path = os.path.join(os.path.dirname(bot.account.db_path), __name__)
    if not os.path.exists(path):
        os.makedirs(path)
    init_cache(path)


@simplebot.filter(admin=True)
def filter_messages(bot: DeltaBot, message: Message, replies: Replies) -> None:
    """Send me webxdc source URLs to add them to the list"""
    if message.chat.is_group() or not message.text.startswith("http"):
        return

    url = message.text.rstrip("/")
    urls = get_urls(bot)
    if url in urls:
        replies.add(text="❌ URL already added", quote=message)
    else:
        urls.append(url)
        set_urls(bot, urls)
        replies.add(text="✔️Addded to the list", quote=message)


@simplebot.command(name="/list")
def list_cmd(bot: DeltaBot, replies: Replies) -> None:
    """Get list of available webxdc"""
    with NamedTemporaryFile(
        dir=bot.account.get_blobdir(), prefix="store-", suffix=".xdc", delete=False
    ) as file:
        path = file.name

    apps: List[dict] = []
    with open(path, "wb") as xdc:
        with zipfile.ZipFile(xdc, "w", compression=zipfile.ZIP_DEFLATED) as fzip:

            for index, url in enumerate(get_urls(bot)):
                meta = get_metadata(url)
                if not meta:
                    continue
                if meta.get("icon"):
                    icon = f"img/{index}.{meta['icon'][0]}"
                    fzip.writestr(icon, meta["icon"][1])
                    meta["icon"] = icon
                else:
                    meta["icon"] = ""
                apps.append(meta)

            if apps:
                apps.sort(key=lambda it: it.get("name"))  # type: ignore
                fzip.writestr("manifest.toml", 'name = "Webxdc List"')
                fzip.writestr("index.html", HTML_FILE)
                fzip.writestr("main.js", JS_FILE)
                fzip.writestr("styles.css", CSS_FILE)
                fzip.writestr("data.json", json.dumps(apps))

    if not apps:
        os.remove(path)
        replies.add(text="❌ Empty List")
        return

    replies.add(filename=path)


@simplebot.command
def download(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Download the webxdc with the given ID"""
    url, content = get_webxdc(bot, payload)
    if url:
        replies.add(filename="app.xdc", bytefile=BytesIO(content))
    else:
        replies.add(text="❌ Unknow webxdc ID", quote=message)


@simplebot.command(admin=True)
def delete(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Delete the webxdc with the given ID"""
    urls = get_urls(bot)
    try:
        urls.remove(payload)
        set_urls(bot, urls)
        replies.add(text="✔️Deleted", quote=message)
    except ValueError:
        replies.add(text="❌ Unknow webxdc ID", quote=message)


@simplebot.command(admin=True)
def refresh(bot: DeltaBot, payload: str, message: Message, replies: Replies) -> None:
    """Force to refresh the metadata of the webxdc with the given ID"""
    if payload not in get_urls(bot):
        replies.add(text="❌ Unknow webxdc ID", quote=message)
    else:
        reset_metadata(payload)
        replies.add(text="✔️Updated", quote=message)
