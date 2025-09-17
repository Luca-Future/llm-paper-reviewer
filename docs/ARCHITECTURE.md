# 项目架构文档

## 概述

Paper Reviewer AI 采用现代化的分层架构，结合了领域驱动设计（DDD）和依赖注入（DI）模式，确保代码的可维护性、可测试性和可扩展性。

## 架构原则

1. **分层架构**：清晰的关注点分离
2. **依赖注入**：松耦合和可测试性
3. **领域驱动**：以业务领域为核心的建模
4. **适配器模式**：外部系统的统一接口
5. **单一职责**：每个组件都有明确的职责

## 分层结构

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaces Layer                         │
│              (CLI, API, Web Interface)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                   (Orchestration, Commands)                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Core Layer                            │
│                 (Analysis Engine, Logic)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                            │
│            (Models, Business Rules, Services)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Adapters Layer                            │
│        (AI Services, Parsers, Storage, External APIs)     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                          │
│           (Configuration, Logging, DI Container)            │
└─────────────────────────────────────────────────────────────┘
```

## 各层职责

### 1. Interfaces Layer (接口层)
- **职责**：处理用户交互和外部接口
- **组件**：
  - `interfaces/cli/` - 命令行界面
  - `interfaces/api/` - REST API接口
  - `interfaces/web/` - Web界面（计划中）
- **依赖**：依赖Application Layer

### 2. Application Layer (应用层)
- **职责**：业务流程编排和用例执行
- **组件**：
  - `AnalysisCommands` - 分析命令执行
  - `AnalysisOrchestrator` - 分析协调器
- **依赖**：依赖Core Layer和Domain Layer

### 3. Core Layer (核心层)
- **职责**：核心业务逻辑和算法
- **组件**：
  - `BaseAnalysisEngine` - 分析引擎基类
  - `AIAnalysisEngine` - AI分析引擎实现
  - `AnalysisValidator` - 分析验证器
- **依赖**：依赖Domain Layer

### 4. Domain Layer (领域层)
- **职责**：领域模型和业务规则
- **组件**：
  - `domain/models/` - 领域实体和值对象
  - `domain/services/` - 领域服务
  - `domain/repositories/` - 仓库接口（未来）
- **依赖**：不依赖其他业务层

### 5. Adapters Layer (适配器层)
- **职责**：外部系统的适配和集成
- **组件**：
  - `adapters/ai/` - AI服务适配器（OpenAI, DeepSeek）
  - `adapters/parsers/` - 文件解析器（PDF, Text）
  - `adapters/storage/` - 存储适配器（未来）
- **依赖**：依赖Domain Layer的接口

### 6. Infrastructure Layer (基础设施层)
- **职责**：基础设施和横切关注点
- **组件**：
  - `infrastructure/config/` - 配置管理
  - `infrastructure/container.py` - 依赖注入容器
  - `infrastructure/logging/` - 日志记录
  - `infrastructure/monitoring/` - 监控（未来）
- **依赖**：支撑所有层级

## 核心设计模式

### 1. 依赖注入模式

**目的**：实现松耦合和可测试性

**实现**：
```python
# 容器注册服务
container.register_factory('ai_adapter', lambda: OpenAIAdapter(config))
container.register_factory('parser_registry', lambda: ParserRegistry())

# 服务解析
ai_adapter = container.get('ai_adapter')
```

**优势**：
- 依赖关系明确
- 易于单元测试
- 配置集中管理

### 2. 适配器模式

**目的**：统一不同外部服务的接口

**实现**：
```python
class BaseAIAdapter(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass

class OpenAIAdapter(BaseAIAdapter):
    async def generate_response(self, prompt: str) -> str:
        # OpenAI具体实现
        pass

class DeepSeekAdapter(BaseAIAdapter):
    async def generate_response(self, prompt: str) -> str:
        # DeepSeek具体实现
        pass
```

### 3. 工厂模式

**目的**：对象创建的封装

**实现**：
```python
class AIAdapterFactory:
    @staticmethod
    def create_adapter(config: AISettings) -> BaseAIAdapter:
        if config.provider == 'openai':
            return OpenAIAdapter(config)
        elif config.provider == 'deepseek':
            return DeepSeekAdapter(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
```

### 4. 策略模式

**目的**：算法的动态切换

**实现**：
```python
class AnalysisOrchestrator:
    def __init__(self, primary_engine: BaseAnalysisEngine,
                 fallback_engine: Optional[BaseAnalysisEngine] = None):
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        try:
            return await self.primary_engine.analyze_paper(paper)
        except Exception:
            if self.fallback_engine:
                return await self.fallback_engine.analyze_paper(paper)
            raise
```

## 关键组件

### 1. 依赖注入容器

**功能**：
- 服务注册和解析
- 生命周期管理
- 依赖关系解析

**特性**：
- 支持单例和工厂模式
- 自动依赖注入
- 循环依赖检测

### 2. 配置管理系统

**功能**：
- 环境变量加载
- 类型安全配置
- 多环境支持

**特性**：
- 使用dataclass进行类型验证
- 支持YAML和环境变量
- 配置验证和默认值

### 3. 分析引擎

**功能**：
- AI服务协调
- 结果解析和验证
- 错误处理和恢复

**特性**：
- 支持函数调用和文本生成
- 智能错误恢复
- 结果质量评估

### 4. 文件解析器

**功能**：
- 多格式文件解析
- 内容清理和优化
- 元数据提取

**特性**：
- 可扩展的解析器注册
- 智能文本处理
- 图片提取支持

## 数据流

### 单论文分析流程

```
输入文件 → ParserRegistry → 纸张对象 → AnalysisEngine → AI服务 → 分析结果 → 输出
```

### 批量分析流程

```
文件目录 → 文件发现 → 并发分析 → 结果收集 → 统计报告
```

## 扩展点

### 1. 新AI服务提供商
在 `adapters/ai/` 中添加新的适配器：
```python
class NewAIAdapter(BaseAIAdapter):
    # 实现必要的方法
    pass
```

### 2. 新文件格式支持
在 `adapters/parsers/` 中添加新的解析器：
```python
class NewFileParser(BaseParser):
    # 实现必要的方法
    pass
```

### 3. 新分析策略
在 `core/` 中扩展分析引擎：
```python
class NewAnalysisStrategy(BaseAnalysisEngine):
    # 实现分析逻辑
    pass
```

### 4. 新接口类型
在 `interfaces/` 中添加新的接口：
```python
# CLI、API、Web等新接口
```

## 测试策略

### 1. 单元测试
- 测试各个组件的独立功能
- 使用mock隔离外部依赖
- 覆盖核心业务逻辑

### 2. 集成测试
- 测试组件间的交互
- 验证依赖注入正确性
- 测试配置加载

### 3. 端到端测试
- 完整的分析流程测试
- CLI命令测试
- 错误场景测试

## 性能考虑

### 1. 并发处理
- 使用asyncio进行异步处理
- 批量分析支持并发控制
- 资源使用优化

### 2. 内存管理
- 大文件分块处理
- 图片大小限制
- 及时资源释放

### 3. 缓存策略
- 分析结果缓存（计划中）
- 配置缓存
- AI响应缓存（计划中）

## 安全考虑

### 1. API密钥管理
- 环境变量存储
- 不记录到日志
- 安全的配置加载

### 2. 输入验证
- 文件类型验证
- 路径遍历防护
- 大小限制

### 3. 错误处理
- 敏感信息过滤
- 友好的错误消息
- 异常记录

## 监控和日志

### 1. 结构化日志
- JSON格式日志
- 请求ID追踪
- 性能指标记录

### 2. 监控指标（计划）
- 分析成功率
- 处理时间统计
- 错误率监控

### 3. 健康检查
- 服务状态检查
- 依赖服务可用性
- 配置验证

## 未来规划

### 1. 短期目标
- Web界面开发
- 缓存机制实现
- 更多AI服务支持

### 2. 中期目标
- 分布式处理
- 用户管理系统
- 分析历史记录

### 3. 长期目标
- 插件系统
- 机器学习模型集成
- 企业级功能

## 总结

这个架构设计提供了：
- **可维护性**：清晰的分层和职责分离
- **可扩展性**：模块化设计和适配器模式
- **可测试性**：依赖注入和接口抽象
- **性能**：异步处理和并发支持
- **安全性**：输入验证和错误处理

通过遵循这些架构原则和模式，项目能够保持高质量和可持续发展。