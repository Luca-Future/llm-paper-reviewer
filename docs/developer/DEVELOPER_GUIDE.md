# 开发者指南

## 环境设置

### 1. 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd paper-reviewer-ai

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
uv sync

# 复制配置文件
cp .env.example .env
```

### 2. 开发工具

推荐的开发工具：
- **IDE**: VS Code, PyCharm
- **版本控制**: Git
- **包管理**: UV
- **测试**: pytest
- **代码质量**: black, flake8, mypy

## 项目结构

```
paper-reviewer-ai/
├── adapters/           # 外部服务适配器
│   ├── ai/            # AI服务适配器
│   │   ├── __init__.py
│   │   ├── base.py     # AI适配器基类
│   │   ├── openai_adapter.py
│   │   └── deepseek_adapter.py
│   ├── parsers/       # 文件解析器
│   │   ├── __init__.py
│   │   ├── base.py     # 解析器基类
│   │   ├── pdf_parser.py
│   │   ├── text_parser.py
│   │   └── registry.py # 解析器注册器
│   └── storage/       # 存储适配器（未来）
├── core/              # 核心业务逻辑
│   ├── __init__.py
│   ├── analyzer.py    # 分析引擎
│   └── exceptions.py  # 自定义异常
├── domain/            # 领域模型
│   ├── __init__.py
│   ├── models/        # 领域实体
│   │   ├── __init__.py
│   │   ├── paper.py   # 论文模型
│   │   └── analysis.py # 分析结果模型
│   ├── services/      # 领域服务（未来）
│   └── repositories/  # 仓库接口（未来）
├── infrastructure/     # 基础设施
│   ├── __init__.py
│   ├── config/        # 配置管理
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── container.py   # 依赖注入容器
│   ├── logging/       # 日志配置
│   └── monitoring/    # 监控（未来）
├── interfaces/        # 用户接口
│   ├── cli/           # 命令行界面
│   │   ├── __init__.py
│   │   ├── main.py    # CLI入口
│   │   └── commands.py # CLI命令实现
│   ├── api/           # REST API（未来）
│   └── web/           # Web界面（未来）
├── prompts/           # 提示词模板
├── tests/             # 测试代码
│   ├── unit/          # 单元测试
│   ├── integration/   # 集成测试
│   └── e2e/           # 端到端测试
├── docs/              # 文档
└── scripts/           # 实用脚本
```

## 代码规范

### 1. Python代码风格

```python
# 遵循PEP 8
from typing import Optional, List, Dict, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExampleClass:
    """示例类，包含完整的文档字符串。"""

    name: str
    value: Optional[int] = None

    def process_data(self, data: List[str]) -> Dict[str, Any]:
        """处理数据的方法。

        Args:
            data: 输入数据列表

        Returns:
            处理后的结果字典

        Raises:
            ValueError: 当数据无效时
        """
        if not data:
            raise ValueError("Data cannot be empty")

        return {
            "processed": True,
            "count": len(data)
        }
```

### 2. 类型提示

- 所有函数和变量都要有类型提示
- 使用 `Optional` 表示可选类型
- 使用 `Union` 表示多类型
- 使用 `List`、`Dict`、`Tuple` 等集合类型

### 3. 文档字符串

- 所有公共函数和类都要有文档字符串
- 使用 Google 风格的文档字符串
- 包含参数、返回值和异常说明

### 4. 异常处理

```python
# 使用自定义异常
from core.exceptions import PaperAnalysisError

try:
    result = await analysis_engine.analyze_paper(paper)
except PaperAnalysisError as e:
    logger.error(f"Analysis failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise PaperAnalysisError(f"Unexpected error: {e}")
```

## 依赖注入使用

### 1. 注册服务

```python
from infrastructure.container import DIContainer, get_container
from adapters.ai import OpenAIAdapter
from adapters.parsers import PDFParser

# 注册服务
container = get_container()

# 注册工厂方法
container.register_factory('ai_adapter', lambda: OpenAIAdapter(config))
container.register_factory('pdf_parser', lambda: PDFParser(config))

# 注册单例
container.register_instance('config', settings)
```

### 2. 使用服务

```python
# 获取服务
ai_adapter = container.get('ai_adapter')
pdf_parser = container.get('pdf_parser')

# 使用服务
result = await ai_adapter.generate_response(prompt)
paper = await pdf_parser.parse(file_path)
```

## 测试编写

### 1. 单元测试

```python
import pytest
from unittest.mock import Mock, AsyncMock
from adapters.ai.openai_adapter import OpenAIAdapter
from core.exceptions import AIServiceError

@pytest.fixture
def mock_config():
    return Mock(
        api_key="test_key",
        model="gpt-4o",
        base_url="https://api.openai.com/v1"
    )

@pytest.fixture
def ai_adapter(mock_config):
    return OpenAIAdapter(mock_config)

@pytest.mark.asyncio
async def test_generate_response_success(ai_adapter):
    """测试成功的响应生成。"""
    ai_adapter.client = AsyncMock()
    ai_adapter.client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )

    result = await ai_adapter.generate_response("Test prompt")

    assert result == "Test response"
    ai_adapter.client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_generate_response_failure(ai_adapter):
    """测试响应生成失败。"""
    ai_adapter.client = AsyncMock()
    ai_adapter.client.chat.completions.create.side_effect = Exception("API Error")

    with pytest.raises(AIServiceError):
        await ai_adapter.generate_response("Test prompt")
```

### 2. 集成测试

```python
@pytest.mark.asyncio
async def test_full_analysis_flow():
    """测试完整的分析流程。"""
    from infrastructure.container import initialize_container
    from infrastructure.config.settings import Settings

    settings = Settings.from_env()
    initialize_container(settings)

    from domain.models.paper import Paper
    from core.analyzer import AnalysisOrchestrator

    paper = Paper(
        id="test",
        file_path="test.md",
        content="Test content",
        paper_type="text"
    )

    orchestrator = AnalysisOrchestrator(analysis_engine)
    result = await orchestrator.analyze_paper(paper)

    assert result.paper_id == paper.id
    assert result.title is not None
```

### 3. 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_analyzer.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=. --cov-report=html

# 运行测试并显示详细输出
uv run pytest -v
```

## 调试技巧

### 1. 日志记录

```python
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 使用不同级别的日志
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### 2. 断点调试

```python
# 在代码中设置断点
import pdb; pdb.set_trace()

# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

### 3. 性能分析

```python
import time
import cProfile

def profile_function():
    start_time = time.time()
    # 执行代码
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")

# 使用 cProfile
cProfile.run('your_function()')
```

## 添加新功能

### 1. 添加新的AI服务

1. 在 `adapters/ai/` 中创建新的适配器
2. 继承 `BaseAIAdapter` 类
3. 实现必要的方法
4. 在容器中注册新服务

```python
# adapters/ai/new_provider_adapter.py
from .base import BaseAIAdapter

class NewProviderAdapter(BaseAIAdapter):
    def __init__(self, config):
        super().__init__(config)
        # 初始化逻辑

    async def generate_response(self, prompt: str) -> str:
        # 实现响应生成逻辑
        pass

    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # 实现结构化响应生成逻辑
        pass
```

### 2. 添加新的文件格式支持

1. 在 `adapters/parsers/` 中创建新的解析器
2. 继承 `BaseParser` 类
3. 实现必要的方法
4. 在解析器注册器中注册

```python
# adapters/parsers/new_format_parser.py
from .base import BaseParser

class NewFormatParser(BaseParser):
    def __init__(self, config=None):
        super().__init__(config)
        self.supported_extensions = ['.new']

    def can_parse(self, file_path: str) -> bool:
        return file_path.endswith('.new')

    async def parse(self, file_path: str, **kwargs) -> Paper:
        # 实现解析逻辑
        pass
```

### 3. 添加新的CLI命令

1. 在 `interfaces/cli/commands.py` 中添加新方法
2. 在 `interfaces/cli/main.py` 中添加新的Click命令
3. 更新帮助文档

```python
# interfaces/cli/commands.py
class AnalysisCommands:
    async def new_command(self, param1: str, param2: int = None):
        """新命令的实现。"""
        # 命令逻辑
        pass

# interfaces/cli/main.py
@cli.command()
@click.argument('param1')
@click.option('--param2', type=int, help='Parameter 2')
def new_command(param1, param2):
    """新的CLI命令。"""
    async def _execute():
        commands = AnalysisCommands(ctx.obj['container'])
        await commands.new_command(param1, param2)

    asyncio.run(_execute())
```

## 常见问题

### 1. 依赖注入问题

**问题**：服务无法解析
**解决**：检查服务是否正确注册，依赖关系是否正确

### 2. 异步处理问题

**问题**：异步函数被同步调用
**解决**：使用 `await` 或 `asyncio.run()`

### 3. 配置加载问题

**问题**：环境变量无法加载
**解决**：检查 `.env` 文件格式和权限

### 4. 测试失败问题

**问题**：测试用例失败
**解决**：检查mock设置，确保依赖正确注入

## 贡献流程

1. Fork项目仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 编写代码和测试
4. 确保所有测试通过：`uv run pytest`
5. 更新相关文档
6. 提交更改：`git commit -m "Add new feature"`
7. 推送到分支：`git push origin feature/new-feature`
8. 创建Pull Request

## 代码审查清单

- [ ] 代码遵循PEP 8规范
- [ ] 所有函数都有类型提示
- [ ] 公共函数有完整的文档字符串
- [ ] 包含适当的单元测试
- [ ] 异常处理正确
- [ ] 日志记录适当
- [ ] 代码有适当的注释
- [ ] 功能经过测试验证
- [ ] 文档已更新
- [ ] 不引入安全漏洞

## 部署指南

### 1. 本地部署

```bash
# 安装依赖
uv sync

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行测试
uv run pytest

# 启动应用
python -m interfaces.cli.main info
```

### 2. 容器化部署

```dockerfile
# Dockerfile示例
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv

COPY . .
RUN uv sync --frozen

CMD ["python", "-m", "interfaces.cli.main", "info"]
```

### 3. 生产环境配置

- 使用环境变量管理敏感信息
- 配置适当的日志级别
- 设置资源限制
- 配置监控和告警

## 支持和联系

- 创建GitHub Issue报告问题
- 查看文档和FAQ
- 参与社区讨论