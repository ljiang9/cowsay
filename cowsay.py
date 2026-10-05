#!/usr/bin/env python3
"""cowsay -- 会说话的牛（以及猫和机器人）。

全部 ASCII 艺术均为原创绘制，不是经典 cowsay 的牛。
纯标准库：argparse / sys / unicodedata。
"""
import argparse
import sys
import unicodedata

# ----------------------------------------------------------------------------
# 原创 ASCII 动物（手绘，非经典 cowsay 形象）
# ----------------------------------------------------------------------------

COW = [
    r'   \   .-"-.   ',
    r'    \ ( o o )  ',
    r'      |  ~  |  ',
    r'      | ___ |  ',
    r'       \___/   ',
    r'      _|   |_  ',
    r'     |_|   |_| ',
]

CAT = [
    r'   \   /\_/\   ',
    r'    \ ( o.o )  ',
    r'      >  ~  <  ',
    r'       \___/   ',
    r'      _|   |_  ',
    r'     |_|   |_| ',
]

ROBOT = [
    r'   \   .-"""-. ',
    r'    \ | [o_o] |',
    r'      |  ___  |',
    r'      | |___| |',
    r"       '-----' ",
    r'        | | |  ',
    r'       _| | |_ ',
]

ANIMALS = {"cow": COW, "cat": CAT, "robot": ROBOT}


# ----------------------------------------------------------------------------
# 宽度与换行（CJK 字符按 2 宽计）
# ----------------------------------------------------------------------------

def disp_width(s):
    """显示宽度：东亚宽字符/全角计 2，其余计 1。"""
    w = 0
    for ch in s:
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def wrap_text(text, width):
    """按显示宽度换行：优先按空格断词，超长词按字符硬断。"""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur, curw = [], 0
        for wd in words:
            ww = disp_width(wd)
            if ww > width:
                if cur:
                    lines.append(" ".join(cur))
                    cur, curw = [], 0
                chunk, chunkw = "", 0
                for ch in wd:
                    cw = disp_width(ch)
                    if chunk and chunkw + cw > width:
                        lines.append(chunk)
                        chunk, chunkw = "", 0
                    chunk += ch
                    chunkw += cw
                if chunk:
                    lines.append(chunk)
                continue
            add = ww if not cur else ww + 1
            if cur and curw + add > width:
                lines.append(" ".join(cur))
                cur, curw = [wd], ww
            else:
                cur.append(wd)
                curw += add
        if cur:
            lines.append(" ".join(cur))
    return lines or [""]


def bubble(text, width=40):
    """生成对话框，返回行列表。"""
    lines = wrap_text(text, width)
    inner = max(disp_width(line) for line in lines)
    top = " " + "_" * (inner + 2)
    bottom = " " + "-" * (inner + 2)
    out = [top]
    if len(lines) == 1:
        pad = " " * (inner - disp_width(lines[0]))
        out.append("< " + lines[0] + pad + " >")
    else:
        for i, line in enumerate(lines):
            pad = " " * (inner - disp_width(line))
            if i == 0:
                out.append("/ " + line + pad + " \\")
            elif i == len(lines) - 1:
                out.append("\\ " + line + pad + " /")
            else:
                out.append("| " + line + pad + " |")
    out.append(bottom)
    return out


def say(text, animal="cow", width=40):
    art = ANIMALS.get(animal)
    if art is None:
        raise ValueError("未知的动物：%s（可选：%s）" % (animal, ", ".join(ANIMALS)))
    return "\n".join(bubble(text, width) + art)


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        prog="cowsay",
        description="会说话的牛：把文字装进对话框，让原创 ASCII 动物说出来。",
    )
    p.add_argument("message", nargs="?", help="要说的话（不给则用 --stdin）")
    p.add_argument("--stdin", action="store_true", help="从标准输入读取要说的话")
    p.add_argument("--animal", default="cow", choices=sorted(ANIMALS),
                   help="说话的动物（默认 cow）")
    p.add_argument("--width", type=int, default=40, help="对话框内最大宽度（默认 40）")
    p.add_argument("--list-animals", action="store_true", help="列出可用动物")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.list_animals:
        print("可用动物：" + "、".join(sorted(ANIMALS)))
        return 0
    if args.message is not None:
        text = args.message
    elif args.stdin:
        text = sys.stdin.read()
    else:
        print("error: 请给出要说的话，或用 --stdin 从管道读取。", file=sys.stderr)
        return 2
    if args.width < 10:
        print("error: --width 至少为 10。", file=sys.stderr)
        return 2
    text = text.strip("\n")
    if not text.strip():
        print("error: 说的话不能为空。", file=sys.stderr)
        return 2
    print(say(text, animal=args.animal, width=args.width))
    return 0


if __name__ == "__main__":
    sys.exit(main())
