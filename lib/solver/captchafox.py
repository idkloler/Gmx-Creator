import gzip
import json
import os
import hashlib
import random
import time
from io import BytesIO
from typing import List
import numpy as np
from PIL import Image
from curl_cffi import Session, CurlHttpVersion
from lib.console.console import Console, C, Fore


gap = 23
sex = [10, 25, 60, 95, 105]
logger = Console()


def avg(vals: List[float]) -> float:
    return sum(vals) / len(vals)

def find_gap(data):
    if isinstance(data, bytes):
        img = Image.open(BytesIO(data))
    else:
        img = Image.open(data)
    img = img.convert('RGBA')
    px = np.array(img)
    res = find_x(px)
    if res is None:
        raise Exception("no pixel")
    return res

def find_x(px):
    _, xlen, _ = px.shape
    hits = []
    for y in sex:
        row = px[y]
        mask_rgb = (row[:, 0] != 0) & (row[:, 1] != 0) & (row[:, 2] != 0)
        mask_a = row[:, 3] == 255
        mask = mask_rgb & mask_a
        idx = np.argmax(mask) if mask.any() else None
        if idx is not None and mask.any():
            hits.append({"x": int(idx), "y": y})
    if not hits:
        return None
    return {
        "x": int(avg([m["x"] for m in hits])) + gap,
        "y": int(avg([m["y"] for m in hits]))
    }

def leadzero(s: str, n: int) -> bool:
    if len(s) < n + 1:
        return False
    return s[:n] == "0" * n

def crack(arr):
    if len(arr) != 3:
        raise TypeError("bad input")
    h = arr[1]
    diff = int(arr[2], 2)

    base = hashlib.sha256()
    base.update(h.encode())

    g = 0
    while True:
        hasher = base.copy()
        hasher.update(str(g).encode())
        if leadzero(hasher.hexdigest(), diff):
            return g
        g += 1

def pack(d: dict) -> bytes:
    raw = _prep(d)
    comp = gzip.compress(raw)
    out = bytearray(2 + len(comp))
    out[0] = 1
    out[1] = 4
    for i in range(len(comp)):
        out[2 + i] = (comp[i] ^ (i + 4)) & 0xFF
    return bytes(out)

def _prep(d: dict) -> bytes:
    return json.dumps(d, separators=(",", ":")).encode("utf-8")


ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
icon = 50
slider_width = 300
slider_knob = 32

_CHALLENGE_FP = None
_VERIFY_FP = None


def _load_fp(filename: str) -> dict:
    global _CHALLENGE_FP, _VERIFY_FP
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r") as f:
        data = json.load(f)["cs"]
    return data


class Solver:
    def __init__(self, lang: str = "en", proxy: str | None = None) -> None:
        self.lang = lang
        self.proxy = proxy
        self.session = Session(impersonate="chrome133a")
        self.sitekey = "sk_vKdD8WGlPF5FKpRDs1U4qTuu6Jv0w"
        self.host = "signup.gmx.com"
        self.base_url = "https://mam-api.captchafox.com"
        if proxy:
            self.session.proxies.update(
                {
                    "https": proxy,
                    "http": proxy,
                }
            )
        self.session.headers.update({
            "User-Agent": ua,
            "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        })

    def _get_config(self) -> dict:
        logger.info(
            f"{C["pink"]}Solving Captcha{Fore.RESET} "+
            f"| {C["gray"]}{self.sitekey[:28]}{Fore.RESET} "
        )
        cfg = self.session.get(
            f"{self.base_url}/captcha/{self.sitekey}/config?site=https://signup.gmx.com/",
            headers={
                "User-Agent": ua,
                "Accept": "*/*",
                "Accept-Language": "ja,en-US;q=0.7,en;q=0.3",
                "Referer": "https://signup.gmx.com/",
                "Origin": "https://signup.gmx.com",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Priority": "u=4",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "X-Pulse": "a327e996eeba9274"
            },
        )
        c = cfg.json()
        if not cfg.ok:
            raise Exception(f"cfg fail ({cfg.status_code}): {c.get('error')}")
        return c

    def _create_challenge(self, config: dict) -> dict:
        global _CHALLENGE_FP
        if _CHALLENGE_FP is None:
            _CHALLENGE_FP = _load_fp("challenge.json")
        fp = dict(_CHALLENGE_FP)
        fp["CF0106"] = int(time.time()*1000)
        ch_payload = {
            "lng": self.lang,
            "h": config.get("h"),
            "cs": fp,
            "host": "signup.gmx.com",
            "k": 0,
            "type": "slide",
        }
        ch = self.session.post(
            f"{self.base_url}/captcha/{self.sitekey}/challenge",
            data=pack(ch_payload),
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "text/plain",
                "dnt": "1",
                "origin": "https://signup.gmx.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://signup.gmx.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": ua,
                "X-Pulse": "a327e996eeba9274"
            },
        )
        chj = ch.json()
        if not ch.ok:
            raise Exception(f"challenge fail ({ch.status_code}): {chj.get('error')}")
        #logger.info("Got Challenge", h=str(chj["h"]))
        return chj

    def _calculate_position(self, challenge: dict) -> int:
        import base64

        bg = challenge["challenge"]["bg"]
        img_b64 = bg[bg.index(",") + 1 :]
        img = base64.b64decode(img_b64)
        gap_data = find_gap(img)
        px = int(gap_data["x"] / 2) - (icon // 2) + random.randint(-5, 5)
        px = max(0, min(px, slider_width - slider_knob))
        return px

    def _generate_trail(self, target: int) -> tuple[list[int], float]:
        goal = max(0, min(int(target), slider_width - slider_knob))
        steps = random.randint(18, 30)
        xs: list[int] = []
        current_x = 0
        for i in range(steps):
            remaining = goal - current_x
            if remaining <= 0:
                break
            base_step = max(1, remaining // max(1, (steps - i)))
            step = min(remaining, base_step + random.randint(0, 3))
            current_x += step
            xs.append(current_x)
            if current_x >= goal:
                break
        if not xs or xs[-1] != goal:
            xs.append(goal)
        xs = xs[:40]

        y = 0
        trail: list[int] = []
        y_bias = random.choice([-2, -1, 0, 1])
        for x in xs:
            y += random.randint(-1, 1)
            if random.random() < 0.5:
                y += y_bias
            y = max(-15, min(15, y))
            trail.extend([y, x])
        duration = round(max(0.5, random.uniform(0.6, 1.4) + len(xs) * 0.01), 2)
        if not trail:
            trail = [0, goal]
        return trail[:80], duration

    def _verify(self, challenge: dict, px: int, t: float, moves: List[int]) -> dict:
        #print(moves)
        global _VERIFY_FP
        if _VERIFY_FP is None:
            _VERIFY_FP = _load_fp("verify.json")
        fp = dict(_VERIFY_FP)
        fp["CF0106"] = int(time.time()*1000)
        v_payload = {
            "sk": self.sitekey,
            "mv": moves,
            "t": t,
            "p": px,
            "h": challenge["h"],
            "cs": fp,
            "k": crack(challenge["j"]),
            "type": challenge["type"],
            "host": self.host,
        }
        v = self.session.post(
            f"{self.base_url}/captcha/verify",
            data=pack(v_payload),
            headers={
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "text/plain",
                "dnt": "1",
                "origin": "https://signup.gmx.com",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "referer": "https://signup.gmx.com/",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": ua,
                "X-Pulse": "a327e996eeba9274"
            },
        )
        vj = v.json()
        #print(vj)
        if not v.ok:
            raise Exception(f"verify fail ({v.status_code}): {vj.get('error')}")
        return vj

    def solve(self) -> dict:
        st = time.time()
        config = self._get_config()
        challenge = self._create_challenge(config)
        px = self._calculate_position(challenge)
        moves, t = self._generate_trail(px)
        vj = self._verify(challenge, px, t, moves)
        if vj.get("solved"):
            logger.info(
            f"{C["pink"]}Solved  Captcha{Fore.RESET} "+
            f"| {C["gray"]}{vj.get("token")[:28]}{Fore.RESET} "+
            f"| {C["gray"]}{time.time() - st:.2f}s.{Fore.RESET}"
        )
            return {"token": vj.get("token")}
        raise Exception(
            f"not solved (solved: {vj.get('solved')} - failed: {vj.get('failed', False)})"
        )
