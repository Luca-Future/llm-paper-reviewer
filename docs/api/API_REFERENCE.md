# API 参考文档

## 概述

本文档提供了 Paper Reviewer AI 的完整 API 参考，包括所有公共类、方法和函数的详细说明。

## 目录

- [领域模型](#领域模型)
- [核心组件](#核心组件)
- [适配器](#适配器)
- [基础设施](#基础设施)
- [接口层](#接口层)
- [异常类](#异常类)

## 领域模型

### Paper

```python
@dataclass
class Paper:
    """论文领域模型。"""

    id: str
    file_path: str
    content: str
    paper_type: PaperType
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    extracted_images: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: str) -> 'Paper':
        """从文件路径创建Paper对象。"""
        pass

    def get_word_count(self) -> int:
        """获取论文字数。"""
        pass

    def get_reading_time(self) -> int:
        """获取预估阅读时间（分钟）。"""
        pass
```

**方法**：
- `from_file(file_path: str) -> Paper`: 从文件路径创建Paper对象
- `get_word_count() -> int`: 计算论文总字数
- `get_reading_time() -> int`: 估算阅读时间（按250字/分钟）

### PaperAnalysis

```python
@dataclass
class PaperAnalysis:
    """论文分析结果模型。"""

    id: str
    paper_id: str
    title: str
    summary: str
    problem: str
    solution: str
    limitations: str
    key_contributions: str
    research_significance: Optional[str] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    # ... 其他字段
```

**方法**：
- `get_quality_score() -> float`: 计算分析质量得分
- `to_dict() -> Dict[str, Any]`: 转换为字典格式
- `is_complete() -> bool`: 检查分析是否完整

## 核心组件

### BaseAnalysisEngine

```python
class BaseAnalysisEngine(ABC):
    """分析引擎基类。"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """分析论文。"""
        pass

    @abstractmethod
    async def batch_analyze(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """批量分析论文。"""
        pass
```

### AIAnalysisEngine

```python
class AIAnalysisEngine(BaseAnalysisEngine):
    """AI分析引擎实现。"""

    def __init__(self, ai_adapter: BaseAIAdapter, config: Dict[str, Any]):
        super().__init__(config)
        self.ai_adapter = ai_adapter
        self.prompt_manager = PromptManager(config)

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """使用AI分析论文。"""
        pass

    async def _generate_analysis(self, content: str, prompt: str, tools: Optional[Dict[str, Any]]) -> str:
        """生成分析内容。"""
        pass

    def _parse_analysis_result(self, result: str, prompt_version: str) -> Dict[str, Any]:
        """解析分析结果。"""
        pass
```

### AnalysisOrchestrator

```python
class AnalysisOrchestrator:
    """分析协调器。"""

    def __init__(self, primary_engine: AnalysisEngine, fallback_engine: Optional[AnalysisEngine] = None):
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """协调论文分析。"""
        pass

    async def batch_analyze(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """批量协调论文分析。"""
        pass
```

## 适配器

### BaseAIAdapter

```python
class BaseAIAdapter(ABC):
    """AI适配器基类。"""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """生成文本响应。"""
        pass

    @abstractmethod
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """生成结构化响应。"""
        pass

    def estimate_tokens(self, text: str) -> int:
        """估算token数量。"""
        pass
```

### OpenAIAdapter

```python
class OpenAIAdapter(BaseAIAdapter):
    """OpenAI适配器实现。"""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate_response(self, prompt: str) -> str:
        """使用OpenAI生成响应。"""
        pass

    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """使用OpenAI生成结构化响应。"""
        pass
```

### BaseParser

```python
class BaseParser(ABC):
    """解析器基类。"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """检查是否可以解析文件。"""
        pass

    @abstractmethod
    async def parse(self, file_path: str, **kwargs) -> Paper:
        """解析文件。"""
        pass

    def validate_file(self, file_path: str) -> bool:
        """验证文件是否可读。"""
        pass
```

### PDFParser

```python
class PDFParser(BaseParser):
    """PDF解析器实现。"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.supported_extensions = ['.pdf']

    async def parse(self, file_path: str, extract_images: bool = False, remove_headers_footers: bool = True) -> Paper:
        """解析PDF文件。"""
        pass

    def _remove_headers_footers(self, page_texts: List[str]) -> List[str]:
        """移除页眉页脚。"""
        pass

    def _extract_images_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """提取页面中的图片。"""
        pass
```

### TextParser

```python
class TextParser(BaseParser):
    """文本解析器实现。"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.supported_extensions = ['.txt', '.md', '.markdown']

    async def parse(self, file_path: str, **kwargs) -> Paper:
        """解析文本文件。"""
        pass

    def detect_paper_structure(self, content: str) -> Dict[str, Any]:
        """检测论文结构。"""
        pass

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """提取元数据。"""
        pass
```

## 基础设施

### Settings

```python
@dataclass
class Settings:
    """应用配置。"""

    ai: AISettings = field(default_factory=AISettings)
    analysis: AnalysisSettings = field(default_factory=AnalysisSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)

    @classmethod
    def from_env(cls) -> 'Settings':
        """从环境变量加载配置。"""
        pass

    @classmethod
    def from_yaml(cls, file_path: str) -> 'Settings':
        """从YAML文件加载配置。"""
        pass
```

### DIContainer

```python
class DIContainer:
    """依赖注入容器。"""

    def __init__(self, config: Settings):
        self.config = config
        self.services: Dict[str, ServiceDescriptor] = {}
        self._register_services()

    def register_factory(self, name: str, factory: Callable, singleton: bool = True):
        """注册服务工厂。"""
        pass

    def register_instance(self, name: str, instance: Any):
        """注册服务实例。"""
        pass

    def get(self, name: str) -> Any:
        """获取服务实例。"""
        pass

    def create_orchestrator(self, fallback_engine: Optional[BaseAnalysisEngine] = None) -> AnalysisOrchestrator:
        """创建分析协调器。"""
        pass
```

### ApplicationContainer

```python
class ApplicationContainer:
    """应用级容器。"""

    _instance: Optional['ApplicationContainer'] = None
    _container: Optional[DIContainer] = None

    def initialize(self, config: Settings):
        """初始化容器。"""
        pass

    def get(self, service_name: str) -> Any:
        """获取服务。"""
        pass

    @classmethod
    def get_instance(cls) -> 'ApplicationContainer':
        """获取全局实例。"""
        pass
```

## 接口层

### AnalysisCommands

```python
class AnalysisCommands:
    """CLI命令实现。"""

    def __init__(self, container):
        self.container = container
        self.orchestrator = container.get_container().create_orchestrator()
        self.parser_registry = container.get('parser_registry')
        self.config = container.get_container().config

    async def analyze_paper(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        prompt_version: Optional[str] = None,
        model: Optional[str] = None,
        max_length: Optional[int] = None,
        extract_images: bool = False
    ) -> PaperAnalysis:
        """分析单个论文。"""
        pass

    async def batch_analyze_papers(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        prompt_version: Optional[str] = None,
        model: Optional[str] = None,
        max_length: Optional[int] = None,
        concurrent: int = 3
    ) -> List[PaperAnalysis]:
        """批量分析论文。"""
        pass

    async def test_connection(self) -> bool:
        """测试AI服务连接。"""
        pass

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息。"""
        pass
```

## 异常类

### PaperAnalysisError

```python
class PaperAnalysisError(Exception):
    """论文分析错误基类。"""
    pass
```

### PaperParseError

```python
class PaperParseError(PaperAnalysisError):
    """论文解析错误。"""
    pass
```

### AIServiceError

```python
class AIServiceError(PaperAnalysisError):
    """AI服务错误。"""
    pass
```

### ConfigurationError

```python
class ConfigurationError(PaperAnalysisError):
    """配置错误。"""
    pass
```

## 枚举类

### AnalysisStatus

```python
class AnalysisStatus(Enum):
    """分析状态枚举。"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

### PaperType

```python
class PaperType(Enum):
    """论文类型枚举。"""

    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"
```

## 使用示例

### 基本用法

```python
from infrastructure.config.settings import Settings
from infrastructure.container import initialize_container
from domain.models.paper import Paper

# 初始化
settings = Settings.from_env()
initialize_container(settings)
from infrastructure.container import get_container
container = get_container()

# 创建论文对象
paper = Paper.from_file("example.pdf")

# 分析论文
orchestrator = container.create_orchestrator()
analysis = await orchestrator.analyze_paper(paper)

# 获取结果
print(f"Title: {analysis.title}")
print(f"Summary: {analysis.summary}")
```

### 批量分析

```python
from interfaces.cli.commands import AnalysisCommands
from infrastructure.container import ApplicationContainer

# 使用命令
container = ApplicationContainer.get_instance()
commands = AnalysisCommands(container)

# 批量分析
results = await commands.batch_analyze_papers(
    input_dir="./papers",
    output_dir="./results",
    concurrent=3
)

# 查看结果
for result in results:
    print(f"Paper: {result.title}")
    print(f"Status: {result.status}")
```

### 自定义适配器

```python
from adapters.ai.base import BaseAIAdapter

class CustomAIAdapter(BaseAIAdapter):
    async def generate_response(self, prompt: str) -> str:
        # 自定义AI服务实现
        return "Custom response"

    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # 自定义结构化响应实现
        return {"response": "Custom structured response"}

# 注册自定义适配器
container.register_factory('custom_ai_adapter', lambda: CustomAIAdapter(config))
```

## 最佳实践

### 1. 配置管理

```python
# 推荐的配置方式
settings = Settings.from_env()
# 而不是
settings = Settings(ai=AISettings(api_key="hardcoded_key"))
```

### 2. 错误处理

```python
try:
    analysis = await orchestrator.analyze_paper(paper)
except PaperAnalysisError as e:
    logger.error(f"Analysis failed: {e}")
    # 处理特定错误
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # 处理未知错误
```

### 3. 资源管理

```python
# 使用异步上下文管理器
async with create_async_session() as session:
    # 执行异步操作
    pass

# 确保资源释放
try:
    result = await some_async_operation()
finally:
    await cleanup_resources()
```

### 4. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await analysis_engine.analyze_paper(paper)
    logger.info(f"Analysis completed successfully for paper {paper.id}")
except Exception as e:
    logger.error(f"Analysis failed for paper {paper.id}: {e}")
    raise
```

## 版本兼容性

### 当前版本 (v2.0.0)

- Python 3.11+
- 所有API均为异步
- 使用依赖注入
- 支持多种AI服务

### 版本升级指南

从 v1.0.0 升级到 v2.0.0：

1. 更新导入路径
2. 使用异步API
3. 配置依赖注入
4. 更新错误处理

## 限制和注意事项

1. **文件大小限制**：单个文件最大128KB字符
2. **并发限制**：默认最多3个并发分析
3. **API限制**：受AI服务提供商的限制
4. **内存使用**：大文件可能导致内存使用增加