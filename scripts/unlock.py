#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dakar Desert Rally - Simplified Chinese unlock patch builder.

The PC release ships with a complete official Simplified Chinese translation
(language ID 10) inside its pak archives, but the in-game language menu only
exposes 7 languages and never offers Chinese.

This script copies the Chinese strings over the English language slot (ID 1)
and repacks them into a UE4 patch pak, so selecting "English" in-game shows a
Chinese interface while keeping English voice-over.

No game assets are stored in this repository - everything is read from the
user's own legally purchased copy at runtime.
"""

import argparse
import collections
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SEP = "<!sp!>"
BOM = b"\xef\xbb\xbf"

# --- pak parameters, must match the original pakchunk0 -----------------------
PAK_VERSION = "V11"
MOUNT_POINT = "../../../"
PATH_HASH_SEED = 1778378931  # 0x69FFE8B3, read from `repak info`

# --- language IDs (see EFFLanguage.txt) --------------------------------------
SRC_LANG = "10"  # Chinese (Simplified)
TARGET_LANG = "1"  # English

# --- text tables inside pakchunk0 -------------------------------------------
TABLE_DIR = "Dakar2Game/Content/Database/FFTranslation"
TABLES = ("FFMessageLanguage.txt", "FFTextLanguage.txt")
PAK_NAME = "pakchunk0-WindowsNoEditor.pak"
PATCH_NAME = "pakchunk0-WindowsNoEditor_P.pak"

# --- hand-translated rally roadbook terms ------------------------------------
# These 43 entries have no official Chinese version; they are the navigator
# roadbook instructions, translated using standard Chinese rally terminology.
ROADBOOK = {
    "7763": "300 米内有提示",
    "7766": "300 米内有路书",
    "7769": "三级危险提示",
    "7772": "沙丘 一级",
    "7773": "沙丘 二级",
    "7774": "沙丘 三级",
    "7943": "水泥路面积水",
    "7946": "水泥路面",
    "7949": "开阔后有新路书",
    "7952": "开阔后路书变更",
    "7955": "起点",
    "7958": "特殊赛段起点",
    "7961": "终点",
    "7964": "特殊赛段终点",
    "7967": "时间控制点",
    "7970": "计时点",
    "7973": "中立化路段起点",
    "7976": "中立化路段终点",
    "7979": "维修区起点",
    "7982": "维修区终点",
    "7991": "限速区",
    "8208": "必须是",
    "8211": "急左转至",
    "8214": "急右转至",
    "8217": "急左转进入",
    "8220": "急右转进入",
    "8223": "发夹弯左至",
    "8226": "发夹弯右至",
    "8229": "发夹弯左入",
    "8232": "发夹弯右入",
    "8235": "靠左行驶于",
    "8238": "靠右行驶于",
    "8241": "左转至",
    "8244": "右转至",
    "8247": "左转进入",
    "8250": "右转进入",
    "8253": "直行于",
    "8256": "直行至",
    "9622": "将在你的左侧",
    "9625": "将在你的右侧",
    "9628": "就在前方",
    "9662": "小沙丘",
    "9777": "你可以在这里查看其他车手的排名",
}


def log(msg):
    print(f"[*] {msg}", flush=True)


def die(msg):
    print(f"[!] {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


# ---------------------------------------------------------------------------
# pak handling
# ---------------------------------------------------------------------------
def find_paks_dir(game_dir: Path) -> Path:
    """Locate Dakar2Game/Content/Paks inside the install directory."""
    candidates = [
        game_dir / "Dakar2Game" / "Content" / "Paks",
        game_dir / "Content" / "Paks",
    ]
    for c in candidates:
        if (c / PAK_NAME).exists():
            return c
    # fall back to a shallow recursive search
    for p in game_dir.rglob(PAK_NAME):
        return p.parent
    die(f"找不到 {PAK_NAME}，请用 --game 指定游戏根目录")


def check_repak(repak: Path):
    if not repak.exists():
        die(f"找不到 repak: {repak}")
    try:
        subprocess.run([str(repak), "--version"], capture_output=True, check=True, timeout=30)
    except Exception as e:
        die(f"repak 无法运行: {e}")


def check_oodle(repak: Path) -> bool:
    """repak needs oo2core_9_win64.dll next to the executable."""
    dll = repak.parent / "oo2core_9_win64.dll"
    if dll.exists():
        return True
    log("警告: repak 同目录下没有 oo2core_9_win64.dll")
    log("      pak 是 Oodle 压缩的，缺少该 DLL 会解压失败。")
    log("      可从 https://github.com/WorkingRobot/OodleUE 获取")
    log("      (Engine/Source/Programs/Shared/EpicGames.Oodle/Sdk/*/win/redist/)")
    return False


def repak_extract(repak: Path, pak: Path, inner: str, dest: Path):
    """Read a single file out of the pak (binary safe)."""
    with open(dest, "wb") as fh:
        r = subprocess.run(
            [str(repak), "get", str(pak), inner],
            stdout=fh, stderr=subprocess.PIPE, timeout=600,
        )
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip()
        die(f"提取 {inner} 失败: {err}")
    if dest.stat().st_size == 0:
        die(f"提取 {inner} 得到空文件")


def game_running() -> bool:
    """Check whether the game process still holds the pak files."""
    if os.name != "nt":
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Dakar2-Win64-Shipping.exe"],
            capture_output=True, text=True, timeout=15,
        ).stdout
        return "Dakar2" in out
    except Exception:
        return False


# ---------------------------------------------------------------------------
# text conversion
# ---------------------------------------------------------------------------
def convert(data: bytes) -> tuple:
    """
    Move every SRC_LANG string into the TARGET_LANG slot.

    Returns (new_bytes, stats) where stats is a dict of counters.
    """
    bom = BOM if data.startswith(BOM) else b""
    body = data[len(bom):].decode("utf-8")
    lines = body.splitlines(keepends=True)

    parsed = []
    for ln in lines:
        core = ln.rstrip("\r\n")
        ending = ln[len(core):]
        parsed.append([core.split(SEP), ending, core])

    # text_id -> {lang_id: text}
    groups = collections.defaultdict(dict)
    for p in parsed:
        parts = p[0]
        if len(parts) >= 4:
            groups[parts[1]][parts[2]] = parts[3]

    n_official = n_roadbook = 0
    for p in parsed:
        parts = p[0]
        if len(parts) < 4 or parts[2] != TARGET_LANG:
            continue
        tid = parts[1]
        zh = groups.get(tid, {}).get(SRC_LANG)
        if zh is not None:
            parts[3] = zh
            n_official += 1
        elif tid in ROADBOOK:
            parts[3] = ROADBOOK[tid]
            n_roadbook += 1
        else:
            continue
        p[2] = SEP.join(parts)

    out = bom + "".join(p[2] + p[1] for p in parsed).encode("utf-8")
    stats = {
        "entries": len(groups),
        "with_chinese": sum(1 for v in groups.values() if SRC_LANG in v),
        "official": n_official,
        "roadbook": n_roadbook,
    }
    return out, stats


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="为 Dakar Desert Rally 生成简体中文解锁补丁 pak",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--game", required=True, help=r"游戏根目录，例如 D:\EpicGames\DakarDesertRally")
    ap.add_argument("--repak", required=True, help="repak 可执行文件路径")
    ap.add_argument("--out", default=None, help="输出 pak 路径（默认与 repak 同目录）")
    ap.add_argument("--no-deploy", action="store_true", help="只生成 pak，不复制进游戏目录")
    ap.add_argument("--keep-temp", action="store_true", help="保留下载/中间目录")
    args = ap.parse_args()

    game_dir = Path(args.game).expanduser().resolve()
    repak = Path(args.repak).expanduser().resolve()
    out_pak = Path(args.out).expanduser().resolve() if args.out else repak.parent / PATCH_NAME

    if not game_dir.is_dir():
        die(f"游戏目录不存在: {game_dir}")
    check_repak(repak)
    if not check_oodle(repak) and "--force" not in sys.argv:
        log("继续尝试（若失败，请补齐 oo2core_9_win64.dll 后重跑）")

    if game_running():
        die("游戏正在运行，请先退出游戏（pak 文件被占用）")

    paks_dir = find_paks_dir(game_dir)
    pak = paks_dir / PAK_NAME
    log(f"游戏 pak: {pak}")
    log(f"pak 大小: {pak.stat().st_size / 1024 / 1024 / 1024:.2f} GB")

    work = Path(tempfile.mkdtemp(prefix="dakar_cn_"))
    try:
        stage = work / TABLE_DIR
        stage.mkdir(parents=True, exist_ok=True)

        # 1. extract
        for name in TABLES:
            dest = stage / name
            inner = f"{TABLE_DIR}/{name}"
            log(f"提取 {name} ...")
            repak_extract(repak, pak, inner, dest)

        # 2. convert
        for name in TABLES:
            path = stage / name
            new_data, st = convert(path.read_bytes())
            path.write_bytes(new_data)
            log(
                f"{name}: {st['entries']:,} 条目, 中文覆盖 {st['with_chinese']:,} "
                f"-> 写入 {st['official']:,} 条官方中文 + {st['roadbook']} 条补译"
            )

        # 3. pack
        log("打包 patch pak ...")
        r = subprocess.run(
            [
                str(repak), "pack",
                "--version", PAK_VERSION,
                "--mount-point", MOUNT_POINT,
                "--path-hash-seed", str(PATH_HASH_SEED),
                str(work), str(out_pak),
            ],
            capture_output=True, text=True, timeout=1800,
        )
        if r.returncode != 0:
            die(f"打包失败: {r.stderr.strip() or r.stdout.strip()}")
        log(f"已生成 {out_pak} ({out_pak.stat().st_size / 1024 / 1024:.2f} MB)")

        # 4. verify
        v = subprocess.run(
            [str(repak), "list", str(out_pak)],
            capture_output=True, text=True, timeout=300,
        )
        listing = v.stdout.strip().splitlines()
        log(f"包内文件 {len(listing)} 个:")
        for line in listing:
            print("    " + line)
        if len(listing) != len(TABLES):
            die("包内文件数量不符，请检查")

        # 5. deploy
        if args.no_deploy:
            log("已跳过部署（--no-deploy）")
        else:
            target = paks_dir / PATCH_NAME
            shutil.copy2(out_pak, target)
            log(f"已部署到 {target}")
            log("启动游戏 -> 语言选 English -> 界面即为中文")
            log(f"卸载：删除 {target}")
    finally:
        if not args.keep_temp:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
