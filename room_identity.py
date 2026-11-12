"""Local profile assets and stable human identity, independent of model routing IDs."""
import base64
import hashlib
import io
import json
import re
from functools import lru_cache
from pathlib import Path


def clean_nickname(value):
    value = value.strip()
    if len(value) > 32 or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError("昵称最多 32 个字符，不能包含换行或控制字符。")
    return value


def room_nickname(store, room_id):
    try:
        value = json.loads(store.setting("room_identity:"+room_id, "{}"))
        return clean_nickname(str(value.get("nickname", "")))
    except (TypeError, ValueError, AttributeError):
        return ""


def import_avatar(source, directory):
    from PIL import Image, ImageOps, ImageDraw, ImageChops
    with Image.open(source) as original:
        if original.width * original.height > 40_000_000:
            raise ValueError("请选择不超过四千万像素的图片。")
        image = ImageOps.fit(ImageOps.exif_transpose(original).convert("RGBA"), (256, 256), Image.Resampling.LANCZOS)
    mask = Image.new("L", (256, 256))
    ImageDraw.Draw(mask).ellipse((0, 0, 255, 255), fill=255)
    image.putalpha(ImageChops.multiply(image.getchannel("A"),mask))
    filename = "avatar-"+hashlib.sha256(image.tobytes()).hexdigest()[:20]+".png"
    path = Path(directory)/"avatars"/filename
    path.parent.mkdir(parents=True, exist_ok=True)
    image.info.clear()
    image.save(path, format="PNG")
    return str(path)


def avatar_path(directory, asset):
    if isinstance(asset, str) and re.fullmatch(r"avatar-[a-f0-9]{20}\.png", asset):
        return Path(directory)/"avatars"/asset
    return None


def avatar_photo(root, path, size=34):
    from PIL import Image, ImageTk
    if not path:
        return None
    try:
        with Image.open(path) as original:
            image = original.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image, master=root)
    except (OSError, ValueError):
        return None


def avatar_data_url(directory, asset):
    path = avatar_path(directory, asset)
    if not path:
        return ""
    return _avatar_data_url(str(path))


@lru_cache(maxsize=128)
def _avatar_data_url(path):
    from PIL import Image
    try:
        with Image.open(path) as original:
            image = original.convert("RGBA").resize((48, 48), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return "data:image/png;base64,"+base64.b64encode(buffer.getvalue()).decode("ascii")
    except (OSError, ValueError):
        return ""


def display_author(message, fallback="你"):
    return (message.details.get("display_name") or fallback) if message.author == "你" else message.author
