# 🍀 OpenLucky - AI-Powered Cryptocurrency Trading Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OKX API](https://img.shields.io/badge/OKX-API%20v5-orange.svg)](https://www.okx.com/docs-v5/)
[![xAI Grok](https://img.shields.io/badge/xAI-Grok--4-purple.svg)](https://x.ai/)
[![GitHub release](https://img.shields.io/badge/release-v1.0-green.svg)](https://github.com/yourusername/OpenLucky/releases)

**OpenLucky** 是一个基于人工智能的加密货币自动交易机器人，集成了 xAI Grok-4 模型和 OKX 交易所 API，提供24小时不间断的市场分析和交易决策，无人值守自动交易。

**OpenLucky** is an AI-powered cryptocurrency trading bot that integrates xAI Grok-4 model with OKX exchange API, providing 24/7 market analysis and trading decisions. Auto Trading.

---

## ⚠️ 重要风险警告 / Important Risk Warning

**🚨 交易风险提示 / Trading Risk Notice:**

本程序使用AI技术节省人力，提供24小时不知疲倦的市场分析和交易执行能力。AI的优势在于视角全面、决策理性、持续运行，但是：

**任何人和任何AI都无法保证交易盈利！** 加密货币交易存在极高风险，可能导致全部资金损失。使用本软件前请：

This program uses AI technology to save manpower and provide 24/7 tireless market analysis and trading execution capabilities. AI's advantages include comprehensive perspective, rational decision-making, and continuous operation, but:

**No person or AI can guarantee trading profits!** Cryptocurrency trading involves extremely high risks and may result in total loss of funds. Before using this software, please:

- 📚 **充分了解交易风险** / Fully understand trading risks
- 💰 **只投入可承受损失的资金** / Only invest funds you can afford to lose  
- 🧪 **先在模拟环境测试** / Test in simulation environment first
- 📖 **学习相关交易知识** / Learn relevant trading knowledge
- ⚖️ **遵守当地法律法规** / Comply with local laws and regulations

**使用本软件即表示您已理解并接受所有风险！**  
**By using this software, you acknowledge and accept all risks!**

---

## ✨ 核心特性 / Key Features

### 🤖 AI-Driven Analysis
- **🧠 xAI Grok-4 Integration**: 先进的大语言模型提供深度市场分析
- **📊 Multi-Timeframe Analysis**: 多时间框架技术指标分析
- **🎯 Structured Decision Making**: 结构化输出确保决策可靠性
- **📈 Real-time Market Sentiment**: 实时市场情绪分析

### 🔄 Automated Trading
- **⚡ 24/7 Operation**: 全天候自动化交易执行
- **🎛️ Configurable Intervals**: 可配置的执行间隔
- **🛡️ Risk Management**: 内置止盈止损机制
- **📋 Position Management**: 智能仓位管理和平仓策略

### 📡 Data Integration
- **🌐 Real-time Market Data**: OKX WebSocket 实时市场数据
- **📊 Technical Indicators**: 50+ 专业技术指标
- **💹 Volume Profile Analysis**: 成交量分布分析
- **📈 Performance Tracking**: 详细的交易绩效跟踪

### 🏗️ Architecture
- **🔌 Modular Design**: 模块化设计便于扩展
- **📝 Comprehensive Logging**: 完整的日志记录系统
- **🔧 Easy Configuration**: 简单的配置管理
- **🐳 Docker Support**: Docker 容器化部署支持

---

## 🚀 快速开始 / Quick Start

### 📋 系统要求 / System Requirements

- **Python**: 3.8+ 
- **Operating System**: Linux, macOS, Windows
- **Memory**: 至少 1GB RAM / At least 1GB RAM
- **Network**: 稳定的网络连接 / Stable internet connection

### 🛠️ 安装步骤 / Installation

1. **克隆仓库 / Clone Repository**
   ```bash
   git clone https://github.com/yourusername/OpenLucky.git
   cd OpenLucky
   ```

2. **安装依赖 / Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置API密钥 / Configure API Keys**
   ```bash
   cp config.ini.template config.ini
   # 编辑 config.ini，填入您的API密钥
   # Edit config.ini and fill in your API keys
   ```

4. **获取API密钥 / Get API Keys**
   - **OKX API**: [https://www.okx.com/account/my-api](https://www.okx.com/account/my-api)
   - **xAI API**: [https://console.x.ai/](https://console.x.ai/)

### 🏃‍♂️ 运行程序 / Running the Bot

1. **启动市场数据同步 / Start Market Data Sync**
   ```bash
   python okx_sync.py
   ```

2. **运行交易机器人 / Run Trading Bot**
   ```bash
   # 持续运行模式 / Continuous mode
   python main.py
   
   # 单次执行模式 / Single execution mode  
   python main.py --once
   
   # 自定义间隔 / Custom interval
   python main.py --interval 15
   ```

3. **查看历史记录 / View History (Optional)**
   ```bash
   python history.py
   ```

---

## 📁 项目结构 / Project Structure

```
OpenLucky/
├── 📄 main.py              # 主程序调度器 / Main orchestrator
├── 🤖 ai_analyze.py        # AI分析模块 / AI analysis module
├── 📊 okx_market.py        # 市场分析 / Market analysis
├── 💰 okx_account.py       # 账户报告 / Account reporting  
├── ⚡ okx_execute.py       # 交易执行 / Trade execution
├── 🔄 okx_sync.py          # 数据同步 / Data synchronization
├── ⏰ okx_time_utils.py    # 时间工具 / Time utilities
├── 📜 history.py           # 历史记录 / History viewer
├── ⚙️ config.ini.template  # 配置模板 / Config template
├── 📋 requirements.txt     # 依赖列表 / Dependencies
├── 📖 prompt.md            # AI提示词 / AI prompts
├── 📏 trade_rules.md       # 交易规则 / Trading rules
├── 🐳 Dockerfile          # Docker配置 / Docker config
├── 📚 docs/               # 文档目录 / Documentation
│   ├── okx-api-v5.md      # OKX API文档 / OKX API docs
│   ├── okx-api-tricks.md  # API使用技巧 / API tricks
│   └── xai_grok_structured_outputs.markdown
└── 📊 examples/           # 示例文件 / Example files
    ├── sample_account.md
    ├── sample_market.md
    └── sample_decision.json
```

---

## 🔮 开发路线图 / Development Roadmap

### 🎯 v1.0 (当前版本 / Current)
- ✅ xAI Grok-4 集成 / xAI Grok-4 Integration
- ✅ OKX 交易所支持 / OKX Exchange Support  
- ✅ 自动化交易执行 / Automated Trading Execution
- ✅ 实时市场分析 / Real-time Market Analysis
- ✅ 风险管理系统 / Risk Management System

### 🚀 v2.0 (计划中 / Planned)
- 🔄 **多AI模型支持** / Multiple AI Model Support
  - OpenAI GPT-4
  - Anthropic Claude
  - Google Gemini
  - 本地开源模型 / Local open-source models

### 🌐 v3.0 (未来版本 / Future)
- 🏦 **多交易平台支持** / Multiple Exchange Support
  - Binance
  - Bybit  
  - Coinbase
  - Kraken
  
### 💹 v4.0 (长期规划 / Long-term)
- 📈 **传统金融市场** / Traditional Financial Markets
  - 股票交易 / Stock Trading
  - 黄金期货 / Gold Futures
  - 外汇市场 / Forex Market
  - 商品期货 / Commodity Futures

---

## 📜 免责声明 / Disclaimer

本软件提供的AI分析仅供参考，不构成投资建议。加密货币交易涉及重大财务风险，可能导致部分或全部资金损失。使用本软件进行实际交易的所有风险由用户自行承担。

This software provides AI analysis for reference only and does not constitute investment advice. Cryptocurrency trading involves significant financial risks and may result in partial or total loss of funds. All risks associated with using this software for actual trading are borne by the user.

开发者不对任何交易损失、技术故障或其他问题承担责任。使用前请充分了解相关风险并谨慎决策。

The developers are not responsible for any trading losses, technical failures, or other issues. Please fully understand the risks and make prudent decisions before use.

---

<div align="center">

**🍀 祝您交易顺利！Good Luck with Your Trading! 🍀**

Made with ❤️ by t7aliang

⭐ **如果这个项目对您有帮助，请给我一个Star！**  
⭐ **If this project helps you, please give us a Star!**

---

## 💝 支持项目 / Support the Project

⭐ **如果你有幸赚了很多，请不吝捐赠，我还处于完全失业中，需要大家的支持和鼓励**

如果 OpenLucky 帮助您获得了收益，欢迎通过以下方式支持项目发展：

If OpenLucky has helped you achieve profits, welcome to support the project development through:

<div align="center">

### 💰 加密货币捐赠 / Cryptocurrency Donations

| USDT (Tron Network) | USDC (Polygon Network) |
|:-------------------:|:----------------------:|
| ![USDT-TRX](docs/OpenLucky-USDT-Tron.jpeg) | ![USDC-Polygon](docs/OpenLucky-USDC-Polygon.jpeg) |
| **USDT (TRC20)** | **USDC (Polygon)** |

</div>

您的每一份支持都是对开源项目最大的鼓励！🙏

Every bit of your support is the greatest encouragement for open source projects! 🙏

</div>