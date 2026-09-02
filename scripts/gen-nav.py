#!/usr/bin/env python3
"""從 README.md 的「文件索引」段落產生 _data/nav.yml。

導覽側欄、上下篇、麵包屑都讀這份 yml。README 的索引改了就重跑一次:

    python3 scripts/gen-nav.py

之所以用產生的而不是手維護:索引已經在 README 裡以閱讀順序排好了,
再抄一份到 yml 只會兩邊不同步。
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
OUT = os.path.join(ROOT, "_data", "nav.yml")

SECTION_RE = re.compile(r'^###\s+(\S+)\s*(.*)$')
GROUP_RE   = re.compile(r'^####\s+(\S+)\s*(.*)$')
BOLD_RE    = re.compile(r'^\*\*(.+?)\*\*\s*$')
ITEM_RE    = re.compile(r'^(\s*)-\s+\[([^\]]+)\]\(([^)]+)\)')

# 章節在頂部導覽列上的短標籤(README 的標題太長,放不下)
SHORT = {
    "00-overview": "總覽", "10-core": "核心", "20-forms": "形態",
    "40-fleet": "調度", "50-physical-ai": "模擬", "55-vlm-llm": "VLM",
    "60-compliance": "法規", "70-security": "資安", "90-foundations": "基礎",
}

def url_of(path):
    """markdown 路徑 → 站上的 URL(相對站根,不含 baseurl)。"""
    path = path.split("#")[0]
    if path.endswith("/"):
        return "/" + path
    if path.endswith(".md"):
        # README.md 由 jekyll-readme-index 產成該目錄的 index
        d = os.path.dirname(path)
        if os.path.basename(path) == "README.md":
            return "/" + (d + "/" if d else "")
        return "/" + path[:-3] + ".html"
    return "/" + path

def esc(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def main():
    lines = open(README, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("## 文件索引"))
    except StopIteration:
        sys.exit("README.md 找不到「## 文件索引」段落")

    sections, cur, group, group_url = [], None, None, None
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        m = SECTION_RE.match(line)
        if m:
            sid, title = m.group(1), m.group(2).strip()
            if not re.match(r'^[0-9]{2}-', sid):      # 「### 參考論文」這種沒編號的
                sid, title = "", (sid + " " + title).strip()
            cur = {"id": sid, "title": title, "short": SHORT.get(sid, title), "pages": []}
            sections.append(cur)
            group = group_url = None
            # 章節自己的 index(docs/<id>/README.md)README 不一定會列,補在最前面
            if sid and os.path.exists(os.path.join(ROOT, "docs", sid, "README.md")):
                short = SHORT.get(sid, title)
                sep = " " if short[-1:].isascii() else ""
                cur["pages"].append({"url": "/docs/%s/" % sid, "title": short + sep + "總覽",
                                     "depth": 0, "group": None, "group_url": None})
            continue
        if cur is None:
            continue
        m = GROUP_RE.match(line)
        if m:
            group = m.group(2).strip() or m.group(1)
            d = os.path.join(ROOT, "docs", m.group(1))
            group_url = ("/docs/" + m.group(1) + "/") if os.path.exists(os.path.join(d, "README.md")) else None
            continue
        m = BOLD_RE.match(line)
        if m:
            group, group_url = m.group(1).strip(), None
            continue
        m = ITEM_RE.match(line)
        if m:
            indent, title, path = len(m.group(1)), m.group(2), m.group(3)
            if path.startswith(("http://", "https://", "#")):
                continue
            url = url_of(path)
            dup = next((q for q in cur["pages"] if q["url"] == url), None)
            if dup:
                dup["title"] = title          # 章節 index 已經補過,改用 README 的標題
                continue
            cur["pages"].append({
                "url": url, "title": title,
                "depth": 1 if indent >= 2 else 0,
                "group": group if indent < 2 else None,
                "group_url": group_url if indent < 2 else None,
            })
            continue

    sections.append({
        "id": "", "title": "這個 repo 怎麼寫的", "short": "關於", "pages": [
            {"url": "/PLAN.html", "title": "整理計畫與進度", "depth": 0, "group": None},
            {"url": "/CONTEXT.html", "title": "術語表", "depth": 0, "group": None},
            {"url": "/docs/_meta/lessons-learned.html", "title": "寫作慣例與 lessons learned", "depth": 0, "group": None},
            {"url": "/docs/_meta/github-actions-gz-sim-playbook.html", "title": "GitHub Actions × gz sim playbook", "depth": 0, "group": None},
            {"url": "/docs/section-map.html", "title": "舊版 28 章對照表", "depth": 0, "group": None},
            {"url": "/docs/_legacy/", "title": "舊版單檔整理", "depth": 0, "group": None},
        ],
    })

    out = ["# 由 scripts/gen-nav.py 從 README.md 的文件索引產生,不要手改。", "sections:"]
    for s in sections:
        out += [f"  - id: {esc(s['id'])}",
                f"    title: {esc(s['title'])}",
                f"    short: {esc(s['short'])}",
                 "    pages:"]
        for p in s["pages"]:
            out += [f"      - url: {esc(p['url'])}",
                    f"        title: {esc(p['title'])}",
                    f"        depth: {p['depth']}"]
            if p.get("group"):
                out.append(f"        group: {esc(p['group'])}")
            if p.get("group_url"):
                out.append(f"        group_url: {esc(p['group_url'])}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    n = sum(len(s["pages"]) for s in sections)
    print(f"寫出 {OUT}:{len(sections)} 個章節、{n} 個頁面")

if __name__ == "__main__":
    main()
