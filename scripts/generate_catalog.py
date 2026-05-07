#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / 'prompts'
CATALOG = ROOT / 'CATALOG.md'

CATEGORY_DESCRIPTIONS = {
    'AI方法': '元提示词、反编译、网页逆向和提示词工程方法。',
    'AI工作': '面向企业、合同、销售、客服、产品原型、PPT、网页等生产力场景。',
    'AI学习': '学习方法、记忆术、费曼提问、习惯养成和学习助理。',
    'AI生活': '健康、亲子歌曲等生活场景。',
    'AI教育': '儿童教育、互动学习页面和小游戏创作。',
    'AI内容': '写作、润色、标题、公众号 HTML、短视频、内容运营、图像和 PPT 创意。',
    'AI编程': '架构设计和编程协作。',
    'AI营销': 'GEO 内容生成、改写、Schema.org 结构化数据和营销增长。',
    'AI思考': '批判思维、记忆、标题和思维类灵感提示词。',
}
CATEGORY_ORDER = list(CATEGORY_DESCRIPTIONS)


def parse_frontmatter(path: Path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return None
    end = text.find('\n---\n', 4)
    if end == -1:
        return None
    data = {}
    for line in text[4:end].splitlines():
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        value = value.strip().strip('"')
        data[key.strip()] = value
    return data


def main():
    entries = []
    for path in sorted(PROMPTS.rglob('*.md')):
        if path.name == 'README.md':
            continue
        fm = parse_frontmatter(path)
        if not fm:
            continue
        rel = path.relative_to(ROOT).as_posix()
        entries.append((rel, fm))

    counts = defaultdict(int)
    for _, fm in entries:
        counts[fm.get('category', '')] += 1

    cat_rows = []
    for cat in CATEGORY_ORDER:
        if counts[cat]:
            cat_rows.append(f'| {cat} | {counts[cat]} | {CATEGORY_DESCRIPTIONS[cat]} |')

    item_rows = []
    for rel, fm in entries:
        item_rows.append(
            f'| {fm.get("category", "")} | {fm.get("subcategory", "")} | '
            f'[{fm.get("title", Path(rel).stem)}]({rel}) | {fm.get("status", "")} | '
            f'{fm.get("tags", "").split(",")[0].strip()} |'
        )

    CATALOG.write_text(
        '# 提示词目录\n\n'
        f'当前共拆分出 **{len(entries)}** 个提示词文件。\n\n'
        '## 分类统计\n\n'
        '| 分类 | 数量 | 说明 |\n'
        '| --- | ---: | --- |\n'
        + '\n'.join(cat_rows)
        + '\n\n## 全量索引\n\n'
        '| 分类 | 子类 | 标题 | 状态 | 主标签 |\n'
        '| --- | --- | --- | --- | --- |\n'
        + '\n'.join(item_rows)
        + '\n',
        encoding='utf-8',
    )
    print(f'Generated {CATALOG.relative_to(ROOT)} with {len(entries)} entries.')


if __name__ == '__main__':
    main()
