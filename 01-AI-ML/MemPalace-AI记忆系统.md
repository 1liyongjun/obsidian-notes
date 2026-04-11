---
title: "MemPalace - AI记忆系统"
source: GitHub
url: "https://github.com/milla-jovovich/mempalace"
author: "Milla Jovovich & Ben Sigman"
date: 2026-04-11
tags: [AI, LLM, Memory, Python, MCP, ChromaDB, OpenSource]
status: summarized
---

## 项目概览

**MemPalace** 是由《生化危机》女主角 Milla Jovovich（爱丽丝饰演者）与程序员好友 Ben Sigman 及 Claude 共同开发的 AI 记忆系统。

> "每个与AI的对话——每个决定、每个调试会话、每个架构辩论——都在会话结束时消失。六个月的工作，化为乌有。"

**核心指标**：
- GitHub ⭐ **40,763** | Fork **5,158**
- LongMemEval R@5 基准测试：**96.6%**（纯本地，无需API调用）
- License: MIT
- 语言: Python 3.9+

---

## 核心设计理念

### "记忆宫殿" 结构

借鉴古希腊雄辩家的"记忆宫殿"方法——将想法放在虚构建筑的房间里，行走时找到想法。MemPalace 将对话组织为：

```
Wings（翅膀）→ 人和项目
  └─ Halls（大厅）→ 记忆类型
       └─ Rooms（房间）→ 具体想法
            └─ Closets（衣柜）→ 细节
                 └─ Drawers（抽屉）→ 最小存储单元
```

**关键区别**：不由AI决定什么值得记忆——你保留每一个词，结构提供可导航的地图，而非扁平搜索索引。

### 存储模式

| 模式 | 说明 | LongMemEval分数 |
|------|------|----------------|
| **Raw（原始）** | 存储实际对话，不做摘要 | **96.6%** |
| AAAK（实验性） | 损耗性缩写压缩 | 84.2% |
| Rooms（房间） | 元数据过滤 | 待公布 |

### AAAK 方言（实验性）

一种损耗性缩写方言，将重复实体压缩为更少token：
- 设计用于**规模化**的重复实体压缩
- **不是存储默认模式**
- 在小规模场景下**不节省token**（README示例有误，已被社区纠正）
- 需要真正的tokenizer验证，不能用 `len(text)//3` 估算

> ⚠️ Milla & Ben 在 2026-04-07 发布后**48小时内**公开承认了README中的错误，包括AAAK示例和"30x无损压缩"的夸大说法，展现了良好的开源态度。

---

## 技术架构

### 核心技术栈

- **ChromaDB** — 向量数据库，语义搜索
- **Python 3.9+** — 仅需Python，无需API key
- **MCP (Model Context Protocol)** — 19个工具，通过MCP协议供AI调用

### 核心文件

| 文件 | 功能 |
|------|------|
| `cli.py` | CLI入口 |
| `mcp_server.py` | MCP服务器（19个工具） |
| `knowledge_graph.py` | 时序实体关系图（SQLite） |
| `palace_graph.py` | 房间导航图 |
| `dialect.py` | AAAK压缩方言 |
| `miner.py` | 项目文件摄入 |
| `convo_miner.py` | 对话摄入（按exchange pair分块） |
| `searcher.py` | ChromaDB语义搜索 |
| `layers.py` | 4层记忆栈 |

### 4层记忆栈

```
L0: Identity（身份）→ 每次会话加载
L1: People & Projects（人物和项目）→ 长期
L2: Recent Context（近期上下文）→ 自动摄入
L3: Archived（归档）→ 定期压缩
```

---

## 使用方式

### 快速开始

```bash
pip install mempalace

# 初始化
mempalace init ~/projects/myapp

# 挖掘数据
mempalace mine ~/projects/myapp                    # 项目代码和文档
mempalace mine ~/chats/ --mode convos              # 对话导出
mempalace mine ~/chats/ --mode convos --extract general  # 自动分类

# 搜索
mempalace search "why did we switch to GraphQL"

# AI记住
mempalace status
```

### MCP集成（推荐）

```bash
# Claude Code
claude plugin marketplace add milla-jovovich/mempalace
claude plugin install --scope user mempalace

# 其他MCP兼容工具
claude mcp add mempalace -- python -m mempalace.mcp_server
```

### 自动保存钩子

```json
{
  "hooks": {
    "Stop": [{"matcher": "", "hooks": [{"type": "command", "command": "/path/to/mempalace/hooks/mempal_save_hook.sh"}]}]
  }
}
```

---

## 基准测试对比

| 系统 | LongMemEval R@5 | API Required | 成本 |
|------|----------------|--------------|------|
| **MemPalace (hybrid)** | **100%** | 可选 | 免费 |
| Supermemory ASMR | ~99% | 是 | — |
| **MemPalace (raw)** | **96.6%** | **无** | **免费** |
| Mastra | 94.87% | 是 (GPT) | API费用 |
| Mem0 | ~85% | 是 | $19-249/月 |
| Zep | ~85% | 是 | $25/月+ |

---

## 成本对比

| 方案 | 年Token量 | 年度成本 |
|------|-----------|---------|
| 粘贴所有内容 | 19.5M | 不可能 |
| LLM摘要 | ~650K | ~$507 |
| **MemPalace wake-up** | **~170 tokens** | **~$0.70** |
| **MemPalace + 5次搜索** | **~13,500 tokens** | **~$10** |

---

## 重要安全提醒 ⚠️

> 2026-04-11 更新：社区发现已有假冒MemPalace网站出现，甚至包含恶意软件。**MemPalace 没有官网**，任何声称官网的网站都是假的。

---

## 关键亮点

- ✅ **纯本地运行**，不调用任何外部API，不上传任何数据
- ✅ **96.6%基准分**（LongMemEval R@5），最高记录
- ✅ **MIT开源**，可审计、可修改
- ✅ **MCP协议支持**，与Claude Code等工具原生集成
- ✅ **开源透明**：README有错立即承认并修正
- ⚠️ AAAK模式仍在实验，小规模场景效果不佳

---

## 相关链接

- GitHub: https://github.com/milla-jovovich/mempalace
- Discord: 官方社区
- PyPI: `pip install mempalace`

---

## 个人评价

这是AI记忆系统领域的一次有趣尝试。"记忆宫殿"的概念比传统向量检索更符合人类认知习惯。96.6%的基准分配合免费本地运行的特性，让它对个人开发者和小型团队很有吸引力。

但需要注意：
1. AAAK压缩仍不成熟，小规模使用反而增加复杂度
2. 实际使用体验需要验证——基准分不代表真实场景效果好
3. 警惕仿冒网站，仅通过PyPI或GitHub安装

---

*笔记整理：Claude AI | 2026-04-11*
