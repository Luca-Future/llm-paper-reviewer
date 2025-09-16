# 论文审阅 AI

一款智能学术论文分析工具，使用AI自动总结和评审研究论文。支持PDF和文本文件，具备多语言分析功能。

## 功能特性

- **🤖 AI驱动分析**：使用OpenAI语言模型进行深度论文分析
- **📄 多格式支持**：处理PDF、TXT和Markdown文件
- **🌍 多语言支持**：支持中英文分析，提供语言适配的输出
- **🔍 结构化输出**：生成包含摘要、问题、解决方案和局限性的综合分析
- **⚙️ 可配置提示词**：多种分析提示词版本满足不同需求
- **🖼️ 图片提取**：可选的PDF图片提取功能
- **📝 智能文本处理**：自动识别并移除页眉页脚，提升分析质量

## 安装说明

### 系统要求

- Python >= 3.11
- uv 包管理器
- OpenAI API密钥

### 安装步骤

1. 克隆此仓库：
```bash
git clone <repository-url>
cd paper-reviewer-ai
```

2. 使用 uv 安装依赖：
```bash
uv sync
```

3. 设置环境变量：
```bash
cp .env.example .env
```

4. 编辑`.env`文件并添加您的OpenAI API密钥：
```bash
OPENAI_API_KEY=your-openai-api-key-here
PROMPT_VERSION=EN  # 选项：EN, ZH, EN_2_0, ZH_2_0
```

## 快速开始

### 分析论文

```bash
# 分析PDF文件（自动转换为markdown）
python paper_analyzer.py paper.pdf

# 分析文本/markdown文件
python paper_analyzer.py paper.md

# 保存分析结果到JSON文件
python paper_analyzer.py paper.pdf -o analysis.json

# 使用中文分析
python paper_analyzer.py paper.pdf --prompt-version ZH_2_0
```

### PDF转Markdown

```bash
# PDF转markdown（不提取图片）
python pdf_parser.py paper.pdf output.md --no-images

# PDF转markdown（提取图片）
python pdf_parser.py paper.pdf output.md
```

## 使用示例

### 基础分析
```bash
python paper_analyzer.py research_paper.pdf
```

### 高级分析（使用增强提示词）
```bash
python paper_analyzer.py research_paper.pdf --prompt-version EN_2_0 -o detailed_analysis.json
```

### 中文分析
```bash
python paper_analyzer.py research_paper.pdf --prompt-version ZH_2_0
```

## 输出格式

分析生成结构化输出，包括：

- **标题**：论文标题
- **摘要**：论文内容全面概述
- **问题**：研究问题或挑战
- **解决方案**：使用的方法论和技术路线
- **局限性**：技术限制和未解决问题
- **主要贡献**：对领域的主要贡献
- **研究意义**（增强版本）：工作的影响和重要性

## 提示词版本

### 1.0版本（基础版）
- **EN/ZH**：标准5字段分析
- 快速了解论文内容

### 2.0版本（增强版）
- **EN_2_0/ZH_2_0**：增强6字段分析
- 包含研究意义评估
- 更详细的分析要求

## 配置说明

### 环境变量

- `OPENAI_API_KEY`：您的OpenAI API密钥（必需）
- `PROMPT_VERSION`：默认提示词版本（EN, ZH, EN_2_0, ZH_2_0）
- `OPENAI_MODEL`：默认模型（默认：gpt-4o）
- `OPENAI_TEMPERATURE`：响应随机性（默认：0.1）

### 命令行选项

```bash
python paper_analyzer.py <input_file> [OPTIONS]

选项：
  --output, -o        JSON结果输出文件路径
  --model             OpenAI模型名称（默认：gpt-4o）
  --temperature       响应温度（0-1，默认：0.1）
  --max-length        最大分析字符数（默认：8000）
  --prompt-version    提示词版本（EN, ZH, EN_2_0, ZH_2_0）
```

## 文件支持

### 输入格式
- **PDF**：自动文本提取和页眉页脚移除
- **TXT**：纯文本文件
- **MD/Markdown**：Markdown格式文件

### 输出格式
- **控制台**：带分区标题的格式化文本输出
- **JSON**：结构化数据，便于程序化使用

## 架构设计

### 核心组件

1. **PDF解析器**：处理PDF到markdown转换，智能文本清理
2. **论文分析器**：使用LangChain和OpenAI模型的AI分析引擎
3. **提示词系统**：不同语言和版本的可配置分析模板

### 数据流程

```
输入文件 → PDF解析器（如需要） → 文本处理 → AI分析 → 结构化输出
```

## 系统要求

- Python >= 3.11
- langchain >= 0.3.27
- langchain-openai >= 0.3.33
- pymupdf >= 1.26.4
- python-dotenv >= 1.1.1

## 贡献指南

1. Fork此仓库
2. 创建功能分支
3. 进行您的更改
4. 如适用，添加测试
5. 提交pull request

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件了解详情。

## 致谢

- OpenAI提供语言模型
- LangChain团队提供优秀的编排框架
- PyMuPDF提供强大的PDF处理能力