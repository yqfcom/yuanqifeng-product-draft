#!/usr/bin/env python3
"""Check a draft JSON; report lengths and fail only on hard limits.
Input: {title, selling_point, overview: [paragraphs] or string,
        steps: [{name, description}]}.
"""
import argparse
import json
from pathlib import Path


def check(draft):
    checks = []
    def add(field, text, maximum):
        size = len(text.replace('\r', '').replace('\n', ''))
        checks.append({'field': field, 'characters': size, 'maximum': maximum,
                       'passed': size <= maximum})
    add('title', draft['title'], 22)
    add('selling_point', draft['selling_point'], 60)
    overview = draft['overview']
    paragraphs = overview if isinstance(overview, list) else overview.splitlines()
    paragraphs = [p for p in paragraphs if p.strip()]
    add('overview.total', ''.join(paragraphs), 500)
    for index, paragraph in enumerate(paragraphs, 1):
        add(f'overview.paragraph.{index}', paragraph, 120)
    for index, step in enumerate(draft['steps'], 1):
        add(f'steps.{index}.name', step['name'], 15)
        add(f'steps.{index}.description', step['description'], 35)
    return {'passed': all(c['passed'] for c in checks), 'checks': checks,
            'note': '长度通过不代表内容完整、事实正确或风格合格；另行进行语义检查。'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft', type=Path)
    args = parser.parse_args()
    result = check(json.loads(args.draft.read_text(encoding='utf-8')))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
