#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
DOCS_DIR = ROOT / "docs"
OUTPUT = DOCS_DIR / "index.html"

REPO_URL = "https://github.com/yaojingang/yao-open-prompts"

CATEGORY_ORDER = [
    "AI方法",
    "AI工作",
    "AI学习",
    "AI生活",
    "AI教育",
    "AI内容",
    "AI编程",
    "AI营销",
    "AI思考",
]

CATEGORY_DESCRIPTIONS = {
    "AI方法": "元提示词、反编译、网页逆向、提示词工程框架",
    "AI工作": "企业调研、合同、客服、销售、产品原型、PPT、网页",
    "AI学习": "学习方法、记忆术、费曼提问、习惯养成",
    "AI生活": "健康、亲子、生活创作",
    "AI教育": "儿童教育、互动学习页面、小游戏生成、教学活动",
    "AI内容": "写作、润色、标题、公众号HTML、短视频、内容运营、图像",
    "AI编程": "架构设计、系统方案、开发协作",
    "AI营销": "GEO文章生成、Schema.org结构化数据、AI搜索优化",
    "AI思考": "批判思维、记忆宫殿、标题灵感、思维工具",
}

CATEGORY_COLORS = {
    "AI方法": "#2563eb",
    "AI工作": "#0f766e",
    "AI学习": "#7c3aed",
    "AI生活": "#ca8a04",
    "AI教育": "#db2777",
    "AI内容": "#dc2626",
    "AI编程": "#475569",
    "AI营销": "#16a34a",
    "AI思考": "#9333ea",
}

REPRESENTATIVE_SLUGS = {
    "AI方法": [
        "rtf-meta-prompt-system-v06",
        "meta-prompt-rtf-generator",
        "interactive-rtf-meta-prompt-system",
        "lisp-rtf-meta-prompt-v08",
        "webpage-reverse-engineering",
        "image-reverse-engineering",
        "article-reverse-engineering",
        "video-reverse-engineering",
    ],
    "AI工作": [
        "company-research-methodology",
        "contract-generator",
        "customer-service-system-prompt",
        "private-domain-sales-prompt",
        "douyin-style-product-prototype-generator",
        "high-quality-ai-ppt-generator",
        "html-ppt-generator-v3",
        "world-class-webpage-generator",
    ],
    "AI学习": [
        "personalized-habit-formation-planner",
        "keyword-learning-assistant",
        "memory-technique-coach",
        "feynman-learning-method",
        "feynman-questioning-coach",
        "pomodoro-learning-coach",
    ],
    "AI生活": [
        "personalized-health-report",
        "personalized-parent-child-song",
    ],
    "AI教育": [
        "children-learning-page-lisp",
        "child-game-maze-digging",
        "child-game-pixel-racing",
        "child-game-shark-fish",
    ],
    "AI内容": [
        "hook-opening-copy",
        "spoken-viral-script",
        "topic-planner",
        "douyin-viral-planner",
        "xiaohongshu-graphic-expert",
        "content-data-review-diagnostician",
        "humanized-writing-v2",
        "humanized-writing-polish-v3",
        "knowledge-base-writing-rebuilder",
        "title-alchemist-content",
        "xiaohongshu-title-generator",
        "wechat-article-html-generator",
        "sora2-character-video-ideas",
        "cut-everything-video-generator",
        "nano-banana",
        "nano-banana-ppt",
        "sanmao-style-memoir-generator",
    ],
    "AI编程": [
        "ai-system-architect",
    ],
    "AI营销": [
        "geo-article-generator",
        "geo-article-rewriter",
        "schema-org-geo-optimization",
    ],
    "AI思考": [
        "self-critique-master",
        "memory-palace-architect",
        "title-alchemist-thinking",
    ],
}

FEATURED_SLUGS = [
    "rtf-meta-prompt-system-v06",
]

COLLECTIONS = [
    {
        "kicker": "专题入口",
        "title": "36 个内容与运营提示词",
        "description": "新增的 36 个提示词已直接并入 AI内容目录，采用与仓库其他文件一致的命名方式，覆盖短视频文案、人设风格、平台运营、行业内容、直播转化、私域成交、AI绘画、数据复盘和爆款重构。",
        "href": f"{REPO_URL}/blob/main/prompts/06-ai-content/README.md",
        "meta": "36 个",
    },
]


@dataclass
class Prompt:
    title: str
    category: str
    subcategory: str
    version: str
    tags: list[str]
    description: str
    rel_path: str
    github_url: str
    slug: str


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def extract_description(body: str) -> str:
    match = re.search(r"## 简介\s+(.+?)(?:\n## |\Z)", body, re.S)
    if not match:
        return ""
    text = " ".join(line.strip() for line in match.group(1).splitlines() if line.strip())
    return re.sub(r"\s+", " ", text).strip()


def load_prompts() -> list[Prompt]:
    prompts = []
    for path in sorted(PROMPTS_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        fm, body = parse_frontmatter(path)
        if not fm:
            continue
        rel = path.relative_to(ROOT).as_posix()
        tags = [tag.strip() for tag in fm.get("tags", "").split(",") if tag.strip()]
        prompts.append(
            Prompt(
                title=fm.get("title", path.stem),
                category=fm.get("category", ""),
                subcategory=fm.get("subcategory", ""),
                version=fm.get("version", ""),
                tags=tags,
                description=extract_description(body),
                rel_path=rel,
                github_url=f"{REPO_URL}/blob/main/{rel}",
                slug=path.stem,
            )
        )
    return prompts


def html_attrs(attrs: dict[str, str]) -> str:
    return " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in attrs.items())


def tag_list(tags: list[str]) -> str:
    return "".join(f"<span>{escape(tag)}</span>" for tag in tags[:3])


def build_category_cards(counts: dict[str, int], total: int) -> str:
    max_count = max(counts.values())
    cards = []
    for category in CATEGORY_ORDER:
        count = counts.get(category, 0)
        pct = round(count / total * 100) if total else 0
        width = round(count / max_count * 100) if max_count else 0
        color = CATEGORY_COLORS[category]
        cards.append(
            f"""
            <a class="type-card" href="#{escape(category)}" style="--accent:{color}; --bar:{width}%">
              <div class="type-card__top">
                <span class="type-name">{escape(category)}</span>
                <strong>{count}</strong>
              </div>
              <p>{escape(CATEGORY_DESCRIPTIONS[category])}</p>
              <div class="type-bar" aria-hidden="true"><i></i></div>
              <span class="type-share">{pct}% of library</span>
            </a>
            """
        )
    return "\n".join(cards)


def build_prompt_card(prompt: Prompt, color: str) -> str:
    desc = prompt.description
    if len(desc) > 120:
        desc = desc[:118].rstrip() + "..."
    return f"""
      <article class="prompt-card" style="--accent:{color}">
        <div class="prompt-card__meta">
          <span>{escape(prompt.subcategory)}</span>
          <span>{escape(prompt.version)}</span>
        </div>
        <h3>{escape(prompt.title)}</h3>
        <p>{escape(desc)}</p>
        <div class="prompt-card__tags">{tag_list(prompt.tags)}</div>
        <a class="prompt-link" href="{escape(prompt.github_url)}" target="_blank" rel="noreferrer">查看 Prompt</a>
      </article>
    """


def build_featured(prompts: list[Prompt]) -> str:
    by_slug = {prompt.slug: prompt for prompt in prompts}
    cards = []
    for slug in FEATURED_SLUGS:
        prompt = by_slug.get(slug)
        if not prompt:
            continue
        cards.append(
            f"""
            <article class="featured-card">
              <div class="featured-copy">
                <span class="featured-kicker">重点推荐</span>
                <h2>{escape(prompt.title)}</h2>
                <p>{escape(prompt.description)}</p>
                <div class="prompt-card__tags">{tag_list(prompt.tags)}</div>
              </div>
              <div class="featured-side">
                <span>{escape(prompt.category)}</span>
                <strong>{escape(prompt.version)}</strong>
                <a class="button" href="{escape(prompt.github_url)}" target="_blank" rel="noreferrer">查看推荐 Prompt</a>
              </div>
            </article>
            """
        )
    if not cards:
        return ""
    return f"""
    <section class="featured" aria-label="重点推荐提示词">
      {''.join(cards)}
    </section>
    """


def build_collections() -> str:
    cards = []
    for item in COLLECTIONS:
        cards.append(
            f"""
            <article class="collection-card">
              <div>
                <span class="collection-kicker">{escape(item["kicker"])}</span>
                <h2>{escape(item["title"])}</h2>
                <p>{escape(item["description"])}</p>
              </div>
              <div class="collection-action">
                <strong>{escape(item["meta"])}</strong>
                <a class="button secondary" href="{escape(item["href"])}" target="_blank" rel="noreferrer">进入合集</a>
              </div>
            </article>
            """
        )
    return f"""
    <section class="collections" aria-label="专题合集入口">
      {''.join(cards)}
    </section>
    """


def build_sections(prompts: list[Prompt]) -> str:
    by_slug = {prompt.slug: prompt for prompt in prompts}
    sections = []
    for category in CATEGORY_ORDER:
        color = CATEGORY_COLORS[category]
        cards = []
        for slug in REPRESENTATIVE_SLUGS[category]:
            prompt = by_slug.get(slug)
            if prompt:
                cards.append(build_prompt_card(prompt, color))
        sections.append(
            f"""
            <section class="category-section" id="{escape(category)}">
              <div class="section-heading">
                <div>
                  <span class="section-kicker" style="--accent:{color}">{escape(category)}</span>
                  <h2>{escape(CATEGORY_DESCRIPTIONS[category])}</h2>
                </div>
                <a href="{REPO_URL}/tree/main/prompts" target="_blank" rel="noreferrer">完整目录</a>
              </div>
              <div class="prompt-grid">
                {''.join(cards)}
              </div>
            </section>
            """
        )
    return "\n".join(sections)


def build_html(prompts: list[Prompt]) -> str:
    counts = defaultdict(int)
    for prompt in prompts:
        counts[prompt.category] += 1
    total = len(prompts)
    representative_count = sum(len(slugs) for slugs in REPRESENTATIVE_SLUGS.values())
    featured_section = build_featured(prompts)
    collections_section = build_collections()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Yao Open Prompts - 类型与代表提示词</title>
  <meta name="description" content="Yao Open Prompts 的提示词类型与代表提示词导航页。">
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #171717;
      --muted: #666b74;
      --line: #deded7;
      --soft: #ecece6;
      --shadow: 0 18px 45px rgba(20, 20, 20, .08);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
      background: var(--bg);
      color: var(--ink);
      letter-spacing: 0;
    }}
    a {{ color: inherit; text-decoration: none; }}
    .shell {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid rgba(20,20,20,.08);
      background: rgba(247,247,244,.92);
      backdrop-filter: blur(16px);
    }}
    .topbar .shell {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 64px;
      gap: 20px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
      font-weight: 720;
    }}
    .brand-mark {{
      width: 30px;
      height: 30px;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 3px;
    }}
    .brand-mark i {{
      border-radius: 2px;
      background: var(--ink);
      opacity: .9;
    }}
    .brand-mark i:nth-child(2) {{ background: #2563eb; }}
    .brand-mark i:nth-child(4) {{ background: #16a34a; }}
    .brand-mark i:nth-child(8) {{ background: #dc2626; }}
    .nav {{
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding: 10px 0;
      scrollbar-width: none;
    }}
    .nav::-webkit-scrollbar {{ display: none; }}
    .nav a {{
      flex: 0 0 auto;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      color: #343840;
      font-size: 13px;
      background: rgba(255,255,255,.62);
    }}
    .hero {{
      padding: 48px 0 28px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr);
      gap: 28px;
      align-items: stretch;
    }}
    .hero h1 {{
      margin: 0;
      max-width: 820px;
      font-size: clamp(34px, 5vw, 68px);
      line-height: .98;
      letter-spacing: 0;
    }}
    .hero p {{
      max-width: 700px;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.8;
      margin: 22px 0 0;
    }}
    .hero-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 26px;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      padding: 0 14px;
      border-radius: 7px;
      border: 1px solid var(--ink);
      background: var(--ink);
      color: #fff;
      font-weight: 650;
      font-size: 14px;
    }}
    .button.secondary {{
      color: var(--ink);
      background: transparent;
      border-color: var(--line);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }}
    .metric {{
      min-height: 112px;
      padding: 18px;
      border-radius: 8px;
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
    }}
    .metric strong {{
      display: block;
      font-size: 36px;
      line-height: 1;
    }}
    .metric span {{
      display: block;
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }}
    .featured {{
      padding: 6px 0 20px;
    }}
    .featured-card {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 22px;
      align-items: stretch;
      padding: 24px;
      border: 1px solid #b8c7ee;
      border-top: 4px solid #2563eb;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: var(--shadow);
    }}
    .featured-kicker {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 0 9px;
      border-radius: 999px;
      background: #eff6ff;
      color: #1d4ed8;
      font-size: 13px;
      font-weight: 760;
    }}
    .featured-card h2 {{
      margin: 14px 0 10px;
      font-size: clamp(24px, 3vw, 38px);
      line-height: 1.14;
      letter-spacing: 0;
    }}
    .featured-card p {{
      max-width: 760px;
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.75;
    }}
    .featured-side {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      padding: 18px;
      border-radius: 8px;
      background: #f8fafc;
      border: 1px solid var(--line);
    }}
    .featured-side span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .featured-side strong {{
      font-size: 42px;
      line-height: 1;
    }}
    .collections {{
      padding: 0 0 22px;
    }}
    .collection-card {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 220px;
      gap: 22px;
      align-items: stretch;
      padding: 22px;
      border: 1px solid #fecaca;
      border-left: 4px solid #dc2626;
      border-radius: 8px;
      background: #fff;
      box-shadow: var(--shadow);
    }}
    .collection-kicker {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 0 9px;
      border-radius: 999px;
      background: #fef2f2;
      color: #b91c1c;
      font-size: 13px;
      font-weight: 760;
    }}
    .collection-card h2 {{
      margin: 14px 0 10px;
      font-size: clamp(23px, 3vw, 34px);
      line-height: 1.15;
      letter-spacing: 0;
    }}
    .collection-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.72;
    }}
    .collection-action {{
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      padding: 16px;
      border-radius: 8px;
      background: #fff7ed;
      border: 1px solid #fed7aa;
    }}
    .collection-action strong {{
      font-size: 30px;
      line-height: 1;
      color: #9a3412;
    }}
    .type-map {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 14px;
    }}
    .type-card {{
      display: block;
      min-height: 152px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      transition: transform .18s ease, border-color .18s ease;
    }}
    .type-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent);
    }}
    .type-card__top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }}
    .type-name {{
      color: var(--accent);
      font-weight: 750;
    }}
    .type-card strong {{
      font-size: 26px;
    }}
    .type-card p {{
      min-height: 42px;
      margin: 10px 0 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}
    .type-bar {{
      height: 8px;
      background: var(--soft);
      border-radius: 999px;
      overflow: hidden;
    }}
    .type-bar i {{
      display: block;
      height: 100%;
      width: var(--bar);
      background: var(--accent);
    }}
    .type-share {{
      display: block;
      margin-top: 10px;
      color: #777b82;
      font-size: 12px;
    }}
    .overview {{
      padding: 10px 0 12px;
    }}
    .visual-panel {{
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }}
    .visual-title {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .visual-title h2 {{
      margin: 0;
      font-size: 18px;
    }}
    .visual-title span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .signal {{
      display: grid;
      grid-template-columns: repeat(10, 1fr);
      gap: 4px;
      min-height: 132px;
      align-items: end;
      margin: 20px 0 8px;
    }}
    .signal i {{
      display: block;
      min-height: 18px;
      border-radius: 3px 3px 0 0;
      background: var(--c);
      opacity: .88;
    }}
    .signal i:nth-child(1) {{ height: 38%; --c: #2563eb; }}
    .signal i:nth-child(2) {{ height: 54%; --c: #0f766e; }}
    .signal i:nth-child(3) {{ height: 70%; --c: #7c3aed; }}
    .signal i:nth-child(4) {{ height: 28%; --c: #ca8a04; }}
    .signal i:nth-child(5) {{ height: 36%; --c: #db2777; }}
    .signal i:nth-child(6) {{ height: 100%; --c: #dc2626; }}
    .signal i:nth-child(7) {{ height: 22%; --c: #475569; }}
    .signal i:nth-child(8) {{ height: 28%; --c: #16a34a; }}
    .signal i:nth-child(9) {{ height: 28%; --c: #9333ea; }}
    .signal i:nth-child(10) {{ height: 64%; --c: #111827; }}
    .signal-caption {{
      display: flex;
      justify-content: space-between;
      color: var(--muted);
      font-size: 12px;
    }}
    .category-section {{
      padding: 34px 0 14px;
      scroll-margin-top: 86px;
    }}
    .section-heading {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 14px;
    }}
    .section-heading h2 {{
      margin: 8px 0 0;
      font-size: clamp(22px, 3vw, 34px);
      line-height: 1.15;
      letter-spacing: 0;
    }}
    .section-heading a {{
      color: var(--muted);
      font-size: 14px;
      border-bottom: 1px solid currentColor;
    }}
    .section-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--accent);
      font-weight: 760;
      font-size: 14px;
    }}
    .section-kicker::before {{
      content: "";
      width: 28px;
      height: 3px;
      background: var(--accent);
      border-radius: 99px;
    }}
    .prompt-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }}
    .prompt-card {{
      display: flex;
      flex-direction: column;
      min-height: 226px;
      padding: 18px;
      border: 1px solid var(--line);
      border-top: 4px solid var(--accent);
      border-radius: 8px;
      background: var(--panel);
    }}
    .prompt-card__meta {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .prompt-card h3 {{
      margin: 14px 0 8px;
      font-size: 19px;
      line-height: 1.35;
      letter-spacing: 0;
    }}
    .prompt-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.7;
    }}
    .prompt-card__tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 14px;
    }}
    .prompt-card__tags span {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 0 8px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--accent) 10%, white);
      color: #343840;
      font-size: 12px;
    }}
    .prompt-link {{
      align-self: flex-start;
      margin-top: auto;
      padding-top: 18px;
      color: var(--accent);
      font-weight: 700;
      font-size: 14px;
    }}
    .footer {{
      margin-top: 48px;
      padding: 28px 0 42px;
      color: var(--muted);
      border-top: 1px solid var(--line);
      font-size: 14px;
      line-height: 1.7;
    }}
    @media (max-width: 980px) {{
      .hero-grid {{
        grid-template-columns: 1fr;
      }}
      .prompt-grid,
      .type-map {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .featured-card {{
        grid-template-columns: 1fr;
      }}
      .collection-card {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 680px) {{
      .topbar .shell {{
        align-items: flex-start;
        flex-direction: column;
        gap: 0;
        padding-top: 12px;
      }}
      .hero {{
        padding-top: 34px;
      }}
      .metrics {{
        grid-template-columns: 1fr;
      }}
      .prompt-grid,
      .type-map {{
        grid-template-columns: 1fr;
      }}
      .section-heading {{
        align-items: flex-start;
        flex-direction: column;
      }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="shell">
      <a class="brand" href="#">
        <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>
        <span>Yao Open Prompts</span>
      </a>
      <nav class="nav" aria-label="提示词类型导航">
        {''.join(f'<a href="#{escape(category)}">{escape(category)}</a>' for category in CATEGORY_ORDER)}
      </nav>
    </div>
  </header>

  <main class="shell">
    <section class="hero">
      <div class="hero-grid">
        <div>
          <h1>提示词类型与代表提示词导航</h1>
          <p>从当前开源库中抽取 9 类提示词结构，展示每类的用途、规模和代表样例。当前重点推荐「智能元提示词生成系统 V0.6」；新增的 36 个内容与运营提示词已直接并入 AI内容目录，方便浏览、复制和持续维护。</p>
          <div class="hero-actions">
            <a class="button" href="#AI方法">查看类型</a>
            <a class="button secondary" href="{REPO_URL}/blob/main/CATALOG.md" target="_blank" rel="noreferrer">完整目录</a>
          </div>
        </div>
        <aside class="visual-panel" aria-label="提示词库统计">
          <div class="visual-title">
            <h2>Library Snapshot</h2>
            <span>Generated from repository files</span>
          </div>
          <div class="metrics">
            <div class="metric"><strong>{total}</strong><span>独立提示词文件</span></div>
            <div class="metric"><strong>{len(CATEGORY_ORDER)}</strong><span>一级类型</span></div>
            <div class="metric"><strong>{representative_count}</strong><span>代表提示词入口</span></div>
          </div>
          <div class="signal" aria-hidden="true">{''.join('<i></i>' for _ in range(10))}</div>
          <div class="signal-caption"><span>方法</span><span>内容密集区</span><span>思考</span></div>
        </aside>
      </div>
    </section>

    {featured_section}

    {collections_section}

    <section class="overview" aria-label="提示词类型总览">
      <div class="type-map">
        {build_category_cards(counts, total)}
      </div>
    </section>

    {build_sections(prompts)}
  </main>

  <footer class="footer">
    <div class="shell">
      本页面由 <code>scripts/generate_webpage.py</code> 生成，数据来源于 <code>prompts/</code> 与 <code>CATALOG.md</code>。更新提示词后可重新运行脚本刷新页面。
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    prompts = load_prompts()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    html = "\n".join(line.rstrip() for line in build_html(prompts).splitlines()) + "\n"
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)} with {len(prompts)} prompts.")


if __name__ == "__main__":
    main()
