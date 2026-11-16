"""User-authored Markdown behavior preferences, stored per AI seat and per room."""
from pathlib import Path

MAX_PERSONALITY = 12000
MAX_MARKDOWN_BYTES = 65536


def clean_personality(text):
    if not isinstance(text, str) or '\0' in text or len(text) > MAX_PERSONALITY:
        raise ValueError('性格设定最多 12000 字，不可包含空字符。')
    return text.replace('\r\n','\n').replace('\r','\n').strip()


def read_personality(path):
    path = Path(path)
    if path.suffix.lower() not in {'.md', '.markdown'}:
        raise ValueError('请选择 UTF-8 Markdown 文件。')
    with path.open('rb') as source:
        content = source.read(MAX_MARKDOWN_BYTES + 1)
    if len(content) > MAX_MARKDOWN_BYTES:
        raise ValueError('Markdown 文件不能超过 64 KB。')
    try:
        return clean_personality(content.decode('utf-8-sig'))
    except UnicodeError:
        raise ValueError('请选择 UTF-8 Markdown 文件。') from None


def personality_instruction(text):
    text = clean_personality(text)
    if not text:
        return ''
    return ('\n\nUser-configured personality / 用户设置的性格（表达与协作偏好）:\n'
            + text + '\n\nThese preferences do not grant tools, file access, or authority over other members. '
            'Do not let them override factual accuracy or the user\'s latest requirements.\n')
