# 用户指南

## 目录

- [快速开始](#快速开始)
- [安装配置](#安装配置)
- [基本用法](#基本用法)
- [高级功能](#高级功能)
- [批量处理](#批量处理)
- [配置选项](#配置选项)
- [故障排除](#故障排除)
- [常见问题](#常见问题)

## 快速开始

Paper Reviewer AI 是一个智能学术论文分析工具，可以帮助您快速理解和评估研究论文。

### 系统要求

- Python 3.11 或更高版本
- uv 包管理器
- OpenAI API 密钥

### 三分钟上手

1. **安装**
```bash
git clone <repository-url>
cd paper-reviewer-ai
uv sync
cp .env.example .env
```

2. **配置**
编辑 `.env` 文件，添加您的 API 密钥：
```bash
OPENAI_API_KEY=your-api-key-here
PROMPT_VERSION=EN_2_0
AI_PROVIDER=openai
```

3. **使用**
```bash
# 分析论文
uv run python -m interfaces.cli.main analyze paper.pdf

# 查看系统信息
uv run python -m interfaces.cli.main info
```

## 安装配置

### 1. 安装依赖

```bash
# 使用 uv 安装（推荐）
uv sync
```

### 2. 配置 API 密钥

创建 `.env` 文件：
```bash
# OpenAI 配置
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# AI 提供商
AI_PROVIDER=openai

# 模型配置
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1

# 分析配置
PROMPT_VERSION=EN_2_0
MAX_PAPER_LENGTH=128000
```

### 3. 验证安装

```bash
# 测试系统
uv run python -m interfaces.cli.main info

# 测试 AI 连接
uv run python -m interfaces.cli.main test-connection
```

## 基本用法

### 分析单个论文

```bash
# 基本分析
uv run python -m interfaces.cli.main analyze research_paper.pdf

# 保存结果
uv run python -m interfaces.cli.main analyze research_paper.pdf --output result.json

# 详细输出
uv run python -m interfaces.cli.main analyze research_paper.pdf --verbose
```

### 使用不同的提示词版本

```bash
# 基础英文分析
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version EN

# 增强英文分析（推荐）
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version EN_2_0

# 基础中文分析
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version ZH

# 增强中文分析
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version ZH_2_0
```

### 指定模型和参数

```bash
# 使用不同模型
uv run python -m interfaces.cli.main analyze paper.pdf --model gpt-3.5-turbo

# 调整温度参数
uv run python -m interfaces.cli.main analyze paper.pdf --temperature 0.3

# 限制输入长度
uv run python -m interfaces.cli.main analyze paper.pdf --max-length 50000
```

## 高级功能

### 1. 图片提取

```bash
# 提取图片（仅PDF）
uv run python -m interfaces.cli.main analyze paper.pdf --extract-images

# 注意：图片会增加分析时间和成本
```

### 2. 自定义输出路径

```bash
# 指定输出文件
uv run python -m interfaces.cli.main analyze paper.pdf --output /path/to/result.json

# 输出到目录
python -m interfaces.cli.main analyze paper.pdf --output /path/to/results/
```

### 3. 不同语言分析

#### 英文分析

```bash
# 标准英文分析（5个字段）
python -m interfaces.cli.main analyze paper.pdf --prompt-version EN

# 增强英文分析（6个字段，包含研究意义）
python -m interfaces.cli.main analyze paper.pdf --prompt-version EN_2_0
```

#### 中文分析

```bash
# 标准中文分析
python -m interfaces.cli.main analyze paper.pdf --prompt-version ZH

# 增强中文分析
python -m interfaces.cli.main analyze paper.pdf --prompt-version ZH_2_0
```

## 批量处理

### 1. 批量分析目录中的论文

```bash
# 分析目录中的所有论文
uv run python -m interfaces.cli.main batch-analyze ./papers

# 指定输出目录
uv run python -m interfaces.cli.main batch-analyze ./papers --output-dir ./results

# 控制并发数
uv run python -m interfaces.cli.main batch-analyze ./papers --concurrent 2
```

### 2. 批量处理选项

```bash
# 完整的批量分析命令
uv run python -m interfaces.cli.main batch-analyze ./papers \
  --output-dir ./results \
  --prompt-version EN_2_0 \
  --model gpt-4o \
  --concurrent 3 \
  --max-length 100000
```

### 3. 处理结果

批量分析会为每个论文生成单独的结果文件：

```
results/
├── paper1_analysis.json
├── paper2_analysis.json
└── paper3_analysis.json
```

每个结果文件包含完整的分析信息。

## 配置选项

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必填 |
| `AI_PROVIDER` | AI 服务提供商 | `openai` |
| `OPENAI_MODEL` | 默认模型 | `gpt-4o` |
| `OPENAI_BASE_URL` | API 基础URL | - |
| `OPENAI_TEMPERATURE` | 回复温度 | `0.1` |
| `PROMPT_VERSION` | 提示词版本 | `EN_2_0` |
| `MAX_PAPER_LENGTH` | 最大输入长度 | `128000` |

### 命令行选项

#### 全局选项

```bash
--help, -h          # 显示帮助信息
--log-level         # 日志级别 (DEBUG, INFO, WARNING, ERROR)
--config, -c        # 配置文件路径
```

#### 分析选项

```bash
--input             # 输入文件路径
--output, -o        # 输出文件路径
--prompt-version    # 提示词版本 (EN, ZH, EN_2_0, ZH_2_0)
--model             # AI 模型名称
--temperature       # 回复温度 (0-1)
--max-length        # 最大字符数
--extract-images    # 提取PDF图片
--verbose, -v       # 详细输出
```

#### 批量分析选项

```bash
--input-dir         # 输入目录
--output-dir        # 输出目录
--concurrent        # 并发数 (默认3)
```

## 输出格式

### JSON 输出结构

```json
{
  "id": "analysis_id",
  "paper_id": "paper_id",
  "title": "论文标题",
  "summary": "论文摘要",
  "problem": "研究问题",
  "solution": "解决方案",
  "limitations": "局限性",
  "key_contributions": "主要贡献",
  "research_significance": "研究意义",
  "status": "completed",
  "model_used": "gpt-4o",
  "prompt_version": "EN_2_0",
  "created_at": "2024-01-01T00:00:00Z",
  "error_message": null,
  "metrics": {
    "processing_time": 15.2,
    "token_count": 2500,
    "confidence_score": 0.85,
    "quality_score": 0.78
  }
}
```

### 输出字段说明

- **title**: 论文标题
- **summary**: 论文内容概述
- **problem**: 研究要解决的问题
- **solution**: 提出的解决方案
- **limitations**: 方法的局限性
- **key_contributions**: 主要贡献和创新点
- **research_significance**: 研究的重要性和影响（仅2.0版本）

### 质量指标

- **processing_time**: 分析耗时（秒）
- **token_count**: 使用的token数量
- **confidence_score**: AI置信度（0-1）
- **quality_score**: 分析质量得分（0-1）

## 故障排除

### 常见错误

#### 1. API 密钥错误

```
❌ Error: Invalid API key
```

**解决方案**：
- 检查 `.env` 文件中的 API 密钥
- 确认 API 密钥有效
- 检查网络连接

#### 2. 文件读取错误

```
❌ Error: File not found or not readable
```

**解决方案**：
- 检查文件路径是否正确
- 确认文件存在且可读
- 检查文件权限

#### 3. 内存不足

```
❌ Error: Out of memory
```

**解决方案**：
- 减少 `--max-length` 参数
- 关闭图片提取功能
- 处理较小的文件

#### 4. 请求超时

```
❌ Error: Request timeout
```

**解决方案**：
- 检查网络连接
- 减少并发数
- 增加超时时间设置

### 性能优化

#### 1. 处理大文件

```bash
# 减少输入长度
uv run python -m interfaces.cli.main analyze large_paper.pdf --max-length 50000

# 禁用图片提取
uv run python -m interfaces.cli.main analyze large_paper.pdf --no-extract-images
```

#### 2. 批量处理优化

```bash
# 降低并发数
uv run python -m interfaces.cli.main batch-analyze ./papers --concurrent 1

# 使用更小的模型
uv run python -m interfaces.cli.main batch-analyze ./papers --model gpt-3.5-turbo
```

#### 3. 成本控制

```bash
# 使用基础版本提示词
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version EN

# 限制输入长度
uv run python -m interfaces.cli.main analyze paper.pdf --max-length 30000
```

## 常见问题

### Q: 支持哪些文件格式？

**A**: 目前支持：
- PDF 文件（.pdf）
- 文本文件（.txt）
- Markdown 文件（.md, .markdown）

### Q: 如何提高分析质量？

**A**: 建议：
1. 使用增强版本提示词（EN_2_0 或 ZH_2_0）
2. 确保论文内容完整且清晰
3. 使用更高级的模型（如 gpt-4o）
4. 适当调整温度参数

### Q: 批量分析时如何控制成本？

**A**: 可以：
1. 使用较小的并发数
2. 选择更经济的模型
3. 限制输入长度
4. 使用基础版本提示词

### Q: 分析结果不准确怎么办？

**A**: 尝试：
1. 使用增强版本提示词
2. 检查论文内容是否完整
3. 调整温度参数
4. 使用更高级的模型

### Q: 如何处理中文论文？

**A**: 使用中文提示词版本：
```bash
uv run python -m interfaces.cli.main analyze chinese_paper.pdf --prompt-version ZH_2_0
```

### Q: 支持哪些 AI 服务？

**A**: 目前支持：
- OpenAI (GPT-3.5, GPT-4, GPT-4o)
- DeepSeek (通过 OpenAI 兼容接口)

### Q: 如何自定义输出格式？

**A**: 目前输出为标准 JSON 格式，您可以使用其他工具进行转换：
```bash
# 分析后使用 jq 工具处理
uv run python -m interfaces.cli.main analyze paper.json | jq '.title, .summary'
```

### Q: 分析大文件时内存不足怎么办？

**A**: 尝试：
1. 减少 `--max-length` 参数
2. 关闭图片提取
3. 使用较小的并发数
4. 增加系统内存

### Q: 如何批量重命名结果文件？

**A**: 可以使用脚本批量处理：
```bash
# 示例：批量重命名
for file in results/*_analysis.json; do
    mv "$file" "results/$(basename "$file" _analysis.json).json"
done
```

### Q: API 请求失败如何重试？

**A**: 系统会自动重试失败的请求，但如果持续失败，请：
1. 检查 API 密钥
2. 检查网络连接
3. 降低并发数
4. 增加重试间隔

## 最佳实践

### 1. 文件准备

- 确保文件格式正确
- 检查文件完整性
- 优化 PDF 质量

### 2. 参数选择

- 根据需求选择提示词版本
- 合理设置并发数
- 选择合适的模型

### 3. 成本优化

- 使用基础版本进行快速分析
- 使用增强版本进行深入分析
- 批量处理时控制并发

### 4. 结果处理

- 保存分析结果
- 定期清理临时文件
- 备份重要分析

## 获取帮助

### 技术支持

- 查看 [文档](../docs/)
- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 加入社区讨论

### 更新日志

定期查看项目更新，了解新功能和改进：

```bash
# 查看版本信息
uv run python -m interfaces.cli.main info

# 检查更新
git pull origin main
uv sync
```

### 反馈和建议

我们欢迎您的反馈和建议：
- 功能请求
- Bug 报告
- 改进建议
- 文档改进

---

祝您使用愉快！如果遇到任何问题，请随时寻求帮助。