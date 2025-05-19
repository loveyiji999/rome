"""Minimal YAML utilities for this project.

This implementation supports a very small subset of YAML syntax sufficient for
the configuration files contained in the repository. It handles mappings,
sequences and basic scalar values (strings, numbers and booleans). It is **not**
a full YAML parser and should not be used for arbitrary YAML content.
"""

from typing import Any, List, Tuple
import re


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if text == "":
        return None
    if (text.startswith("'") and text.endswith("'")) or (
        text.startswith('"') and text.endswith('"')
    ):
        return text[1:-1]
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        pass

    # Inline list
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]

    # Inline dict
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        result = {}
        if inner:
            for part in inner.split(","):
                if ":" in part:
                    k, v = part.split(":", 1)
                    result[k.strip()] = _parse_scalar(v.strip())
        return result

    return text


def _tokenize(content: str) -> List[Tuple[int, str]]:
    tokens: List[Tuple[int, str]] = []
    for line in content.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        tokens.append((indent, line.lstrip()))
    return tokens


def _parse(tokens: List[Tuple[int, str]], index: int, indent: int) -> Tuple[Any, int]:
    if index >= len(tokens) or tokens[index][0] < indent:
        return None, index

    if tokens[index][1].startswith("- "):
        result: List[Any] = []
        while index < len(tokens) and tokens[index][0] == indent and tokens[index][1].startswith("- "):
            item_text = tokens[index][1][2:].strip()
            index += 1
            if index < len(tokens) and tokens[index][0] > indent:
                if item_text.endswith(":"):
                    key = item_text[:-1].strip()
                    val, index = _parse(tokens, index, indent + 2)
                    result.append({key: val})
                elif ":" in item_text:
                    key, val_str = item_text.split(":", 1)
                    val = _parse_scalar(val_str)
                    extra, index = _parse(tokens, index, indent + 2)
                    if isinstance(extra, dict):
                        obj = {key.strip(): val}
                        obj.update(extra)
                        result.append(obj)
                    elif extra is not None:
                        result.append({key.strip(): val, "extra": extra})
                    else:
                        result.append({key.strip(): val})
                elif item_text:
                    val, index = _parse(tokens, index, indent + 2)
                    result.append({item_text: val} if val is not None else _parse_scalar(item_text))
                else:
                    val, index = _parse(tokens, index, indent + 2)
                    result.append(val)
            else:
                if item_text.endswith(":"):
                    result.append({item_text[:-1].strip(): None})
                elif ":" in item_text:
                    k, v = item_text.split(":", 1)
                    result.append({k.strip(): _parse_scalar(v)})
                else:
                    result.append(_parse_scalar(item_text))
        return result, index

    result: dict = {}
    while index < len(tokens) and tokens[index][0] >= indent and not tokens[index][1].startswith("- "):
        cur_indent, text = tokens[index]
        if cur_indent < indent:
            break
        if ":" in text:
            key, val_part = text.split(":", 1)
            key = key.strip()
            val_part = val_part.strip()
        else:
            key = text.strip()
            val_part = ""
        index += 1
        if index < len(tokens) and tokens[index][0] > cur_indent:
            sub, index = _parse(tokens, index, cur_indent + 2)
            if val_part:
                result[key] = _parse_scalar(val_part)
                if isinstance(sub, dict):
                    result.update({key: result[key], **sub})
                elif sub is not None:
                    result[key] = {"value": result[key], "extra": sub}
            else:
                result[key] = sub
        else:
            result[key] = _parse_scalar(val_part) if val_part else None
    return result, index


def safe_load(stream) -> Any:
    if hasattr(stream, "read"):
        content = stream.read()
    else:
        content = str(stream)
    tokens = _tokenize(content)
    data, _ = _parse(tokens, 0, 0)
    return data


def dump(data: Any, stream=None) -> str:
    def _dump(obj: Any, indent: int = 0) -> List[str]:
        prefix = " " * indent
        lines: List[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{prefix}{k}:")
                    lines.extend(_dump(v, indent + 2))
                else:
                    val = v
                    if isinstance(v, str) and re.search(r"\s", v):
                        val = f'"{v}"'
                    lines.append(f"{prefix}{k}: {val}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}-")
                    lines.extend(_dump(item, indent + 2))
                else:
                    val = item
                    if isinstance(item, str) and re.search(r"\s", item):
                        val = f'"{item}"'
                    lines.append(f"{prefix}- {val}")
        else:
            val = obj
            if isinstance(obj, str) and re.search(r"\s", obj):
                val = f'"{obj}"'
            lines.append(f"{prefix}{val}")
        return lines

    out_lines = _dump(data)
    result = "\n".join(out_lines)
    if stream is not None:
        stream.write(result)
    return result
