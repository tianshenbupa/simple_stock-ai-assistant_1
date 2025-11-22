```markdown
# 股票投资 AI 助手

使用 LangChain 1.0.5 和 DeepSeek 构建的多代理股票投资分析系统。

## 🚀 主要特性

- **多代理协调系统** - 财务分析、市场分析、估值评估三个专家代理由主管理代理协调
- **财报 RAG 分析** - 集成 Chroma 向量数据库，实现财务报表的语义检索
- **实时市场数据** - 股票价格、市场情绪
- **FastAPI Web 服务** - 生产级别 RESTful API
- **DeepSeek LLM** - 开源高效的大语言模型

## 📋 系统需求

- Python 3.10+
- DeepSeek API Key（[获取地址](https://api.deepseek.com)）
- 8GB+ RAM

## 🔧 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

### 3. 准备财报数据

将 PDF 财报放入 `data/financial_reports/` 目录：

```bash
mkdir -p data/financial_reports
# 复制 PDF 文件到该目录
```

### 4. 启动服务

```bash
uvicorn main:app --reload
```

访问 API 文档：**http://localhost:8000/docs**

## 📚 API 使用示例

### 分析股票

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_ticker": "AAPL",
    "query": "苹果公司是否值得投资？"
  }'
```

**响应示例：**

```json
{
  "stock_ticker": "AAPL",
  "query": "苹果公司是否值得投资？",
  "timestamp": "2024-01-15T10:30:00",
  "analysis": "基于财务分析、市场情绪和估值评估，提供综合建议...",
  "recommendation": "买入",
  "target_price": 185.50
}
```

### 健康检查

```bash
curl "http://localhost:8000/health"
```

## 🏗️ 多代理系统架构

```
用户查询
   ↓
┌──────────────────────────────────┐
│   主管理代理 (Supervisor)        │
│  - 理解用户问题                  │
│  - 协调三个专家代理              │
└──┬─────────────┬─────────┬───────┘
   │             │         │
   ↓             ↓         ↓
┌────────┐  ┌────────┐  ┌──────────┐
│财务代理│  │市场代理│  │估值代理  │
│        │  │        │  │          │
│• 财报  │  │• 价格  │  │• PE 比率 │
│• 比率  │  │• 情绪  │  │• DCF    │
│• 趋势  │  │• 新闻  │  │• 价值   │
└────┬───┘  └────┬───┘  └────┬─────┘
     │           │           │
     └───────────┼───────────┘
                 ↓
        ┌────────────────────┐
        │ 综合分析和建议      │
        │ - 评分 (1-10)      │
        │ - 建议              │
        │ - 目标价格          │
        └────────────────────┘
```

## 📁 项目结构

```
stock-ai-assistant/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── .env.example             # 环境变量示例
├── .env                     # 环境变量（本地）
├── main.py                  # FastAPI 入口
│
├── config/
│   ├── settings.py          # 配置管理
│   └── prompts.py           # 提示词
│
├── data/
│   ├── financial_reports/   # 财报 PDF
│   └── vector_store/        # 向量数据库
│
└── src/
    ├── core/
    │   ├── llm.py           # DeepSeek LLM
    │   └── models.py        # 数据模型
    ├── rag/
    │   ├── loader.py        # PDF 加载
    │   └── retriever.py     # RAG 检索
    ├── tools/
    │   ├── financial.py     # 财务工具
    │   ├── market.py        # 市场工具
    │   └── valuation.py     # 估值工具
    └── agents/
        ├── financial_analyst.py    # 财务代理
        ├── market_analyst.py       # 市场代理
        ├── valuation_expert.py     # 估值代理
        └── supervisor.py           # 主管理代理
```

## 🛠️ 核心技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| **LangChain** | 1.0.5 | 代理框架 |
| **FastAPI** | 0.109.1 | Web 框架 |
| **DeepSeek** | Chat | LLM 模型 |
| **Chroma** | 0.5.0 | 向量数据库 |
| **Pydantic** | 2.7.1 | 数据验证 |

## 🔄 工作流程

1. **用户输入** - 提交股票代码和分析问题
2. **主管理代理** - 理解问题并决定调用哪些专家
3. **财务分析代理**
   - 从 RAG 系统检索相关财报
   - 分析财务指标和趋势
   - 返回财务评估结果
4. **市场分析代理**
   - 获取当前股票价格
   - 评估市场情绪
   - 返回市场分析结果
5. **估值专家代理**
   - 计算各种估值指标
   - 评估内在价值
   - 返回估值建议
6. **综合决策** - 主管理代理综合所有信息，生成最终投资建议

## 📝 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/analyze` | 分析股票 |
| GET | `/health` | 健康检查 |

### 请求示例

```json
{
  "stock_ticker": "AAPL",
  "query": "分析这支股票的投资价值"
}
```

### 响应示例

```json
{
  "stock_ticker": "AAPL",
  "query": "分析这支股票的投资价值",
  "timestamp": "2024-01-15T10:30:00.123456",
  "analysis": "基于财务、市场和估值分析的综合建议...",
  "recommendation": "买入",
  "target_price": 185.50
}
```

## ⚙️ 环境变量说明

```bash
# DeepSeek API
DEEPSEEK_API_KEY=你的 API Key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# RAG 配置
VECTOR_STORE_PATH=data/vector_store      # 向量数据库路径
PDF_DIRECTORY=data/financial_reports     # PDF 文件目录
CHUNK_SIZE=1000                          # 文本块大小
CHUNK_OVERLAP=200                        # 块重叠

# 服务器
HOST=0.0.0.0                             # 监听地址
PORT=8000                                # 端口
DEBUG=True                               # 调试模式
```

## 🚀 部署

### 开发环境

```bash
uvicorn main:app --reload
```

### 生产环境

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📖 使用说明

### 添加财报数据

1. 将 PDF 财报放入 `data/financial_reports/` 目录
2. 重启服务或调用 RAG 初始化接口
3. 系统会自动加载和索引 PDF

### 自定义提示词

编辑 `config/prompts.py` 修改各代理的系统提示词

### 扩展工具集

在 `src/tools/` 下添加新工具，然后在对应代理中注册

## 🔑 获取 DeepSeek API Key

1. 访问 https://api.deepseek.com
2. 注册账号
3. 获取 API Key
4. 添加到 `.env` 文件

## 💡 常见问题

### Q: 为什么没有检索到财报信息？
A: 确保：
- PDF 文件已放入 `data/financial_reports/` 目录
- PDF 文件格式正确
- 向量数据库已初始化

### Q: API 返回错误 401？
A: 检查 DeepSeek API Key 是否正确配置在 `.env` 文件中

### Q: 如何更新财报数据？
A: 将新的 PDF 文件放入 `data/financial_reports/` 并重启服务

## 📞 支持

遇到问题？检查以下内容：
- DeepSeek API Key 是否有效
- Python 版本是否 ≥ 3.10
- 所有依赖是否已安装
- `.env` 文件是否正确配置

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://langchain.com) - AI 代理框架
- [DeepSeek](https://deepseek.com) - LLM 模型
- [Chroma](https://trychroma.com) - 向量数据库
```