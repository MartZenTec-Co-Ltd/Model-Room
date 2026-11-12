"""Persistent, validated UI preferences and local-only wallpaper import."""
import json
import re
from pathlib import Path

from room_locale import LANGUAGES, system_language

DEFAULTS = {"language": "", "mode": "light", "accent": "#5262d5", "wallpaper": "",
            "wallpaper_opacity": 18, "wallpaper_fit": "cover", "auto_detect_agents": True,
            "nickname": "", "avatar": "", "message_font_size": 11, "send_with_enter": True,
            "show_timestamps": True, "auto_scroll": True, "default_rounds": 6}


def load_preferences(store):
    try:
        values = json.loads(store.setting("preferences", "{}"))
    except (TypeError, ValueError):
        values = {}
    return validate_preferences(values)


def validate_preferences(values):
    options = {**DEFAULTS, **{k: v for k, v in values.items() if k in DEFAULTS}} if isinstance(values, dict) else dict(DEFAULTS)
    if options["language"] not in LANGUAGES:
        options["language"] = system_language()
    if options["mode"] not in {"light", "dark"}:
        options["mode"] = "light"
    if not isinstance(options["accent"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", options["accent"]):
        options["accent"] = DEFAULTS["accent"]
    options["wallpaper"] = str(options["wallpaper"] or "")
    try:
        options["wallpaper_opacity"] = max(0, min(100, int(options["wallpaper_opacity"])))
    except (ValueError, TypeError):
        options["wallpaper_opacity"] = 18
    options["auto_detect_agents"] = bool(options["auto_detect_agents"])
    if options["wallpaper_fit"] not in {"cover", "contain", "tile"}:
        options["wallpaper_fit"] = "cover"
    options["nickname"] = str(options["nickname"] or "")[:32].strip()
    options["avatar"] = str(options["avatar"] or "")
    for key, low, high in (("message_font_size", 10, 18), ("default_rounds", 2, 1000000)):
        try:
            options[key] = max(low, min(high, int(options[key])))
        except (TypeError, ValueError):
            options[key] = DEFAULTS[key]
    for key in ("send_with_enter", "show_timestamps", "auto_scroll"):
        options[key] = bool(options[key])
    return options


def save_preferences(store, options, *, room_id=None, room_nickname=None):
    options = validate_preferences(options)
    values = {"preferences": json.dumps(options, ensure_ascii=False)}
    if room_id is not None and room_nickname is not None:
        values["room_identity:"+room_id] = json.dumps({"nickname": room_nickname}, ensure_ascii=False)
    store.set_settings(**values)
    return options


def import_wallpaper(source, directory):
    from PIL import Image, ImageOps
    # Decode once, remove metadata, and copy to application data so moving the original is safe.
    with Image.open(source) as image:
        if image.width * image.height > 40_000_000:
            raise ValueError("请选择不超过四千万像素的图片。")
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((2560, 1600), Image.Resampling.LANCZOS)
        target = Path(directory) / "appearance"
        target.mkdir(parents=True, exist_ok=True)
        # Content-addressed files keep Cancel from overwriting the active wallpaper.
        import hashlib
        digest = hashlib.sha256(image.tobytes()).hexdigest()[:20]
        path = target / ("wallpaper-" + digest + ".png")
        image.info.clear()
        image.save(path, format="PNG")
        return str(path)


def wallpaper_image(options, width, height, color):
    """Render a full viewport image; bubbles are drawn above it, never as an opaque row."""
    from PIL import Image, ImageOps
    size = (max(1, width), max(1, height))
    with Image.open(options["wallpaper"]) as original:
        original = original.convert("RGB")
        mode = options.get("wallpaper_fit", "cover")
        if mode == "tile":
            tile = original.copy()
            tile.thumbnail((512, 512), Image.Resampling.LANCZOS)
            image = Image.new("RGB", size, color)
            for y in range(0, size[1], tile.height):
                for x in range(0, size[0], tile.width):
                    image.paste(tile, (x, y))
        elif mode == "contain":
            fitted = ImageOps.contain(original, size, Image.Resampling.LANCZOS)
            image = Image.new("RGB", size, color)
            image.paste(fitted, ((size[0]-fitted.width)//2, (size[1]-fitted.height)//2))
        else:
            image = ImageOps.fit(original, size, method=Image.Resampling.LANCZOS)
    return Image.blend(Image.new("RGB", size, color), image, options["wallpaper_opacity"] / 100)


def wallpaper_photo(root, options, width, height, color):
    from PIL import Image, ImageOps, ImageTk
    source = options.get("wallpaper")
    if not source or not Path(source).is_file():
        return None
    try:
        image = wallpaper_image(options, width, height, color)
        return ImageTk.PhotoImage(image, master=root)
    except (OSError, ValueError):
        return None
