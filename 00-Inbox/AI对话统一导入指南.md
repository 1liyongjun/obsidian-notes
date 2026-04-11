# AI 对话记录统一导入与管理方案

> 针对 DeepSeek、千问（Qwen）、Gemini、Kiro、QCode、OpenCode、Antigravity、Codex 等多平台对话记录的完整导入流程。

---

## 📊 各平台导出方式一览

| 平台 | 导出方式 | 推荐格式 | 获取难度 |
|------|----------|----------|----------|
| **DeepSeek** | Chrome 扩展 [DeepSeek Chat Exporter](https://chromewebstore.google.com/detail/deepseek-chat-exporter/cohbpcihoiahgokbjkgkecodljploimg) | JSON / Markdown | ⭐ 简单 |
| **Qwen (千问)** | [Tampermonkey 脚本](https://greasyfork.org/zh-CN/scripts/542188) (支持通义千问/Kimi/DeepSeek等) | JSON / Markdown | ⭐ 简单 |
| **Gemini** | 官网 → 设置 → 导出数据 | JSON | ⭐ 简单 |
| **Kiro** | AnySpecs CLI (`anyspecs export --source kiro`) 或 Kiro CLI (`kiro-cli chat --list-sessions`) | Markdown / JSON | ⭐⭐ 中等 |
| **QCode** | 应用内导出 或 AnySpecs CLI | JSON | ⭐⭐ 中等 |
| **OpenCode** | Claude Code 兼容模式 → AnySpecs CLI | JSONL | ⭐⭐ 中等 |
| **Antigravity** | 应用内导出 或 AnySpecs CLI | JSONL | ⭐⭐ 中等 |
| **Codex** | AnySpecs CLI (`anyspecs export --source codex`) | JSONL / Markdown | ⭐⭐ 中等 |
| **Claude Code** | `~/.claude/projects/*/sessions/` | JSONL (原生) | ⭐ 直接用 |
| **ChatGPT** | 官网 → 设置 → 导出数据 → `conversations.json` | JSON (原生) | ⭐ 简单 |

---

## 🛠️ 第一步：安装必要工具

```bash
# 1. 安装 MemPalace（AI记忆系统）
pip install mempalace

# 2. 安装 AnySpecs CLI（统一导出工具，支持 Kiro/Codex/OpenCode等）
pip install anyspecs

# 3. 初始化 MemPalace 记忆宫殿
mempalace init ~/mempalace
```

---

## 📥 第二步：批量导出各平台对话

### 2.1 Claude Code（原生支持）

```bash
# Claude Code 的会话日志就是 JSONL，直接挖掘
mempalace mine ~/.claude/projects/ --mode convos --wing claude-code
```

### 2.2 Kiro / QCode / OpenCode / Antigravity / Codex

```bash
# 安装 AnySpecs CLI 后：
anyspecs list --source kiro      # 列出 Kiro 会话
anyspecs list --source codex     # 列出 Codex 会话

# 导出为 Markdown（推荐，便于转换）
anyspecs export --source kiro --format markdown --output ~/ai-exports/kiro/
anyspecs export --source codex --format markdown --output ~/ai-exports/codex/
anyspecs export --source opencode --format markdown --output ~/ai-exports/opencode/

# 或者一次性导出所有
anyspecs export --all-projects --format markdown --output ~/ai-exports/
```

### 2.3 DeepSeek / Qwen / Gemini（网页版）

**方法 A：使用扩展导出**

1. 安装 [Tampermonkey](https://www.tampermonkey.net/)
2. 安装 [AI对话导出脚本](https://greasyfork.org/zh-CN/scripts/542188)
3. 打开 DeepSeek/Qwen/Gemini 对话页面，点击导出按钮
4. 选择 JSON 或 Markdown 格式
5. 保存到 `~/ai-exports/deepseek/`、`~/ai-exports/qwen/` 等目录

**方法 B：手动整理**

```
DeepSeek 导出目录结构：
~/ai-exports/deepseek/
  ├── 对话1.json
  ├── 对话2.json
  └── 对话3.md

Qwen 导出目录结构：
~/ai-exports/qwen/
  ├── 编程问题.json
  └── 写作助手.md
```

### 2.4 ChatGPT

```
官网 → 右下角头像 → Settings → Data controls → Export data
→ 会收到 email，下载 conversations.json
→ 解压后放到 ~/ai-exports/chatgpt/
```

---

## 🔄 第三步：统一格式转换

### 使用统一转换脚本

```bash
# 先预览（dry-run，不实际写入）
python ai-convo-unified-importer.py \
    --scan ~/ai-exports \
    --output ~/ai-exports-normalized

# 确认无误后，实际写入
python ai-convo-unified-importer.py \
    --scan ~/ai-exports \
    --output ~/ai-exports-normalized \
    --import
```

### 手动整理（如果转换脚本失败）

每条对话保存为 `.txt` 文件，格式如下：

```text
> 用户的第一条消息

助手的第一条回复

> 用户的第二条消息

助手继续回复

> 第三条消息

助手的第三条回复
```

---

## 📦 第四步：导入 MemPalace

### 4.1 按平台分 Wing 导入

```bash
# DeepSeek
mempalace mine ~/ai-exports-normalized/deepseek/ --mode convos --wing deepseek

# Qwen
mempalace mine ~/ai-exports-normalized/qwen/ --mode convos --wing qwen

# Gemini
mempalace mine ~/ai-exports-normalized/gemini/ --mode convos --wing gemini

# Kiro
mempalace mine ~/ai-exports-normalized/kiro/ --mode convos --wing kiro

# QCode
mempalace mine ~/ai-exports-normalized/qcode/ --mode convos --wing qcode

# OpenCode
mempalace mine ~/ai-exports-normalized/opencode/ --mode convos --wing opencode

# Antigravity
mempalace mine ~/ai-exports-normalized/antigravity/ --mode convos --wing antigravity

# Codex
mempalace mine ~/ai-exports-normalized/codex/ --mode convos --wing codex

# Claude Code
mempalace mine ~/ai-exports-normalized/claude-code/ --mode convos --wing claude-code

# ChatGPT
mempalace mine ~/ai-exports-normalized/chatgpt/ --mode convos --wing chatgpt
```

### 4.2 或者一键导入所有

```bash
# 先按平台分目录，再用通配符
mempalace mine ~/ai-exports-normalized/deepseek/ --mode convos --wing deepseek
mempalace mine ~/ai-exports-normalized/qwen/ --mode convos --wing qwen
# ... 重复上述命令
```

---

## 🗂️ 第五步：管理结构

### 推荐 Wing 划分

```
mempalace/
├── wing: claude-code     ← 你自己的 Claude Code 对话
├── wing: chatgpt         ← ChatGPT 对话
├── wing: deepseek        ← DeepSeek 对话
├── wing: qwen            ← 通义千问对话
├── wing: gemini          ← Google Gemini 对话
├── wing: kiro            ← Kiro IDE 对话
├── wing: qcode           ← QCode 对话
├── wing: opencode        ← OpenCode 对话
├── wing: antigravity     ← Antigravity 对话
├── wing: codex           ← OpenAI Codex 对话
└── wing: general         ← 其他 / 未分类
```

### 常用管理命令

```bash
# 查看记忆状态
mempalace status

# 跨平台搜索（比如问："之前用 Gemini 讨论的那个算法问题"）
mempalace search "算法优化"

# 只在某个平台搜索
mempalace search "auth" --wing claude-code

# 查看某个项目的所有对话
mempalace search "项目名" --wing deepseek

# 增量导入（新对话）
mempalace mine ~/ai-exports/deepseek/new/ --mode convos --wing deepseek
```

---

## 🔍 第六步：实际使用

### 场景 1：问 AI "之前我们讨论过什么"

```bash
# 直接问
mempalace search "我们讨论过的架构方案"
```

### 场景 2：跨平台整合回答

```
在 Claude Code 中：
> "我之前在 DeepSeek 问过一个 Python 异步编程的问题，结论是什么来着？"

→ Claude Code 通过 MCP 调用 mempalace_search
→ 返回 DeepSeek 当时的对话记录
→ 汇总回答
```

### 场景 3：设置定时备份

```bash
# 每周自动挖掘一次新对话
0 2 * * 0 /usr/bin/find ~/ai-exports -name "*.json" -newer ~/.mempalace/last-import -exec python ~/ai-convo-unified-importer.py --scan ~/ai-exports --import \;
```

---

## ⚠️ 常见问题

### Q: 某些平台导不出数据怎么办？

**A:** 对于没有原生导出的工具：
1. 检查应用内是否有"导出聊天记录"选项
2. 使用屏幕录制 + Whisper 转文字（不推荐，质量低）
3. 联系工具开发者请求导出功能
4. 对于本地 CLI 工具（如 OpenCode），检查 `~/.opencode/` 等默认数据目录

### Q: 导出格式不被识别怎么办？

**A:** 手动转换为 `> 用户消息` 格式（见上方"手动整理"部分），MemPalace 的 `normalize.py` 会直接识别这种格式。

### Q: 数据量很大，导入很慢？

**A:** MemPalace 使用 ChromaDB 本地向量数据库，首次导入较慢但只需一次。之后增量导入会快很多。

---

## 📁 推荐目录结构

```
~/ai-memory/
├── exports/                    # 原始导出（各平台）
│   ├── deepseek/
│   ├── qwen/
│   ├── gemini/
│   ├── kiro/
│   ├── qcode/
│   ├── opencode/
│   ├── antigravity/
│   ├── codex/
│   ├── claude-code/           # 从 ~/.claude 复制
│   └── chatgpt/               # 从导出包解压
│
├── normalized/                # 统一格式后的文件
│   ├── deepseek/
│   ├── qwen/
│   └── ...
│
├── mempalace/                 # MemPalace 记忆库
│   ├── palace/
│   └── config.json
│
└── scripts/
    └── ai-convo-unified-importer.py  # 统一转换脚本
```

---

*整理：Claude AI | 工具：MemPalace + AnySpecs CLI*
