#!/usr/bin/env python3
"""
AI对话记录统一导入器
====================
将多平台AI对话记录统一转换为MemPalace格式，
并自动分类到对应的 Wing（翅膀/项目）中。

支持的平台：
  - Claude Code / Codeium / OpenCode  (JSONL)
  - Kiro / QCode / Antigravity         (AnySpecs CLI + 自有格式)
  - DeepSeek / Qwen(千问) / Gemini     (JSON/Markdown 导出)
  - ChatGPT / Claude.ai                (原生支持 MemPalace)

使用方法：
  python ai-convo-unified-importer.py --scan ~/ai-exports --dry-run
  python ai-convo-unified-importer.py --scan ~/ai-exports --import
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

# ─────────────────────────────────────────────────────────────
#  格式检测与转换
# ─────────────────────────────────────────────────────────────

def detect_and_convert(filepath: Path, wing_name: str) -> Optional[str]:
    """
    检测文件格式，自动转换为 MemPalace 的 > 用户消息 格式。
    返回转换后的文本内容，失败返回 None。
    """
    ext = filepath.suffix.lower()
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠️  读取失败 {filepath.name}: {e}")
        return None

    # 1. 已有 > 标记的纯文本 → 直接返回
    if ext in (".txt", ".md") and content.count(">") >= 2:
        return content

    # 2. Claude Code / Codex JSONL
    if ext == ".jsonl":
        return convert_jsonl_to_transcript(content, wing_name)

    # 3. JSON 格式检测
    if ext in (".json",) or content.strip().startswith(("{")):
        converted = try_convert_json(content, wing_name)
        if converted:
            return converted

    # 4. Markdown 格式（AI对话助手导出）
    if ext in (".md",):
        converted = convert_markdown_convo(content, wing_name)
        if converted:
            return converted

    return None


def convert_jsonl_to_transcript(content: str, wing: str) -> Optional[str]:
    """转换 JSONL 格式（Claude Code / Codex）"""
    lines = []
    for line in content.strip().split("\n"):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        role = obj.get("role", "")
        text = ""

        if isinstance(obj.get("content"), list):
            for block in obj["content"]:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    break
        elif isinstance(obj.get("content"), str):
            text = obj["content"]

        if not text:
            continue

        if role in ("user", "human"):
            lines.append(f"> {text}\n")
        elif role in ("assistant", "ai", "model"):
            lines.append(f"{text}\n")

    return "\n".join(lines) if lines else None


def try_convert_json(content: str, wing: str) -> Optional[str]:
    """尝试多种 JSON 格式转换"""
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None

    # 格式 1: ChatGPT conversations.json (mapping tree)
    if isinstance(data, dict) and "mapping" in data:
        return convert_chatgpt_json(data)

    # 格式 2: Claude.ai flat messages list
    if isinstance(data, dict) and "messages" in data:
        return convert_claudeai_json(data)

    # 格式 3: DeepSeek / Qwen 等的 messages 数组格式
    if isinstance(data, list):
        return convert_messages_array(data, wing)

    return None


def convert_chatgpt_json(data: dict) -> Optional[str]:
    """ChatGPT conversations.json"""
    mapping = data.get("mapping", {})
    messages = []

    # 找根节点
    root_id = None
    for node_id, node in mapping.items():
        if node.get("parent") is None and node.get("message") is None:
            root_id = node_id
            break

    if not root_id:
        return None

    current_id = root_id
    visited = set()
    while current_id and current_id not in visited:
        visited.add(current_id)
        node = mapping.get(current_id, {})
        msg = node.get("message")
        if msg:
            role = msg.get("author", {}).get("role", "")
            content = msg.get("content", {})
            parts = content.get("parts", []) if isinstance(content, dict) else []
            text = " ".join(str(p) for p in parts if isinstance(p, str) and p).strip()
            if role == "user" and text:
                messages.append(("user", text))
            elif role == "assistant" and text:
                messages.append(("assistant", text))
        children = node.get("children", [])
        current_id = children[0] if children else None

    return build_transcript(messages)


def convert_claudeai_json(data: dict) -> Optional[str]:
    """Claude.ai JSON export"""
    messages_list = data.get("messages", data.get("chat_messages", []))
    messages = []

    for item in messages_list:
        if not isinstance(item, dict):
            continue
        role = item.get("role", "")
        text = ""
        content = item.get("content", "")

        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    break
        elif isinstance(content, str):
            text = content

        if not text:
            continue

        if role in ("user", "human"):
            messages.append(("user", text))
        elif role in ("assistant", "ai"):
            messages.append(("assistant", text))

    return build_transcript(messages)


def convert_messages_array(data: list, wing: str) -> Optional[str]:
    """通用 messages 数组格式（DeepSeek / Qwen / Gemini 等）"""
    messages = []
    for item in data:
        if not isinstance(item, dict):
            continue
        role = item.get("role", "")
        text = ""
        content = item.get("content", "")

        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    break
        elif isinstance(content, str):
            text = content

        if not text:
            continue

        if role in ("user", "human", "text"):
            messages.append(("user", text))
        elif role in ("assistant", "ai", "model", "assistant_reasoning"):
            messages.append(("assistant", text))

    return build_transcript(messages)


def convert_markdown_convo(content: str, wing: str) -> Optional[str]:
    """
    Markdown 格式转换（支持以下变体）：
    1. DeepSeek/通义导出的 Markdown 对话
    2. AnySpecs CLI 导出的 Markdown
    """
    lines = content.split("\n")
    messages = []
    current_role = None
    current_text = []

    for line in lines:
        stripped = line.strip()

        # 新消息标记
        if stripped.startswith("**") and stripped.endswith("**"):
            # 保存前一条
            if current_role and current_text:
                messages.append((current_role, "\n".join(current_text)))
                current_text = []

            # 解析角色
            role_block = stripped.strip("*")
            if "用户" in role_block or "Human" in role_block or "User" in role_block:
                current_role = "user"
            elif "助手" in role_block or "Assistant" in role_block or "AI" in role_block:
                current_role = "assistant"
            else:
                current_role = None
            continue

        # 继续累积当前消息
        if current_role:
            current_text.append(line)

    # 最后一条
    if current_role and current_text:
        messages.append((current_role, "\n".join(current_text)))

    return build_transcript(messages)


def build_transcript(messages: list) -> Optional[str]:
    """将 [(role, text), ...] 转换为 MemPalace 格式"""
    if len(messages) < 2:
        return None

    lines = []
    i = 0
    while i < len(messages):
        role, text = messages[i]
        if role == "user":
            lines.append(f"> {text.strip()}")
            if i + 1 < len(messages) and messages[i + 1][0] == "assistant":
                lines.append("")
                lines.append(messages[i + 1][1].strip())
                i += 2
            else:
                i += 1
        else:
            lines.append(text.strip())
            i += 1
        lines.append("")

    result = "\n".join(lines)
    return result if result.count(">") >= 1 else None


# ─────────────────────────────────────────────────────────────
#  Wing 分类规则
# ─────────────────────────────────────────────────────────────

WING_RULES = {
    "claude-code":  ["claude", "claude-code", ".claude"],
    "chatgpt":      ["chatgpt", "openai"],
    "deepseek":     ["deepseek"],
    "qwen":         ["qwen", "千问", "tongyi", "通义"],
    "gemini":       ["gemini", "google-ai"],
    "kiro":         ["kiro"],
    "qcode":        ["qcode", "q-coder", "qcoder"],
    "opencode":     ["opencode"],
    "antigravity":  ["antigravity", "anti-gravity"],
    "codex":        ["codex", "openai-codex"],
    "cursor":       ["cursor"],
}


def detect_wing(filepath: Path, content_hint: str = "") -> str:
    """根据文件路径和内容推断 Wing 名称"""
    path_str = str(filepath).lower() + content_hint.lower()

    for wing, keywords in WING_RULES.items():
        for kw in keywords:
            if kw in path_str:
                return wing

    return "general"


# ─────────────────────────────────────────────────────────────
#  主流程
# ─────────────────────────────────────────────────────────────

def scan_and_import(
    source_dir: Path,
    output_dir: Path,
    dry_run: bool = True,
    min_messages: int = 2,
):
    """
    扫描目录，转换所有支持的对话文件，
    输出到 output_dir/{wing}/ 目录下。
    """
    output_dir = Path(output_dir)
    stats = {}

    # 支持的文件扩展名
    EXTENSIONS = {".jsonl", ".json", ".md", ".txt", ".html"}

    for filepath in source_dir.rglob("*"):
        if not filepath.is_file():
            continue
        if filepath.suffix.lower() not in EXTENSIONS:
            continue

        wing = detect_wing(filepath)
        converted = detect_and_convert(filepath, wing)

        if not converted or converted.count(">") < min_messages:
            continue

        # 构建输出路径
        wing_dir = output_dir / wing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[^\w\-_.]', '_', filepath.stem)[:50]
        out_file = wing_dir / f"{safe_name}_{timestamp}.txt"

        if not dry_run:
            wing_dir.mkdir(parents=True, exist_ok=True)
            out_file.write_text(converted, encoding="utf-8")

        key = wing
        stats[key] = stats.get(key, 0) + 1

        action = "📦 [会写入]" if not dry_run else "🔍 [预览]"
        print(f"{action} {out_file.relative_to(output_dir)} ({converted.count('>')} 条对话)")

    # 统计
    print(f"\n{'='*50}")
    print(f"总计: {sum(stats.values())} 个文件")
    for wing, count in sorted(stats.items()):
        print(f"  {wing:15s}: {count} 个文件")

    if dry_run:
        print(f"\n💡 使用 --import 参数实际写入文件")

    return stats


def main():
    parser = argparse.ArgumentParser(description="AI对话记录统一导入器")
    parser.add_argument("--scan", type=str, required=True,
                        help="要扫描的源目录")
    parser.add_argument("--output", type=str, default="./ai-exports-normalized",
                        help="输出目录 (default: ./ai-exports-normalized)")
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="实际写入文件（默认只预览）")
    parser.add_argument("--min-messages", type=int, default=2,
                        help="最少消息数 (default: 2)")

    args = parser.parse_args()

    source = Path(args.scan).expanduser()
    output = Path(args.output).expanduser()

    if not source.exists():
        print(f"❌ 目录不存在: {source}")
        return 1

    print(f"\n🔍 扫描: {source}")
    print(f"📤 输出: {output}")
    print(f"🌓 模式: {'导入' if args.do_import else '预览 (dry-run)'}")
    print()

    scan_and_import(
        source_dir=source,
        output_dir=output,
        dry_run=not args.do_import,
        min_messages=args.min_messages,
    )

    return 0


if __name__ == "__main__":
    exit(main())
