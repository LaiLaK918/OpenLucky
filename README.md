# 🍀 OpenLucky - AI-Powered Cryptocurrency Trading Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OKX API](https://img.shields.io/badge/OKX-API%20v5-orange.svg)](https://www.okx.com/docs-v5/)
[![xAI Grok](https://img.shields.io/badge/xAI-Grok--4-purple.svg)](https://x.ai/)
[![GitHub release](https://img.shields.io/badge/release-v1.0-green.svg)](https://github.com/yourusername/OpenLucky/releases)

**OpenLucky** is an AI-powered cryptocurrency trading bot that integrates xAI Grok-4 model with OKX exchange API, providing 24/7 market analysis and trading decisions with automated trading capabilities.

**OpenLucky** 是一个基于人工智能的加密货币自动交易机器人，集成了 xAI Grok-4 模型和 OKX 交易所 API，提供 24 小时不间断的市场分析和交易决策，无人值守自动交易。

---

## ⚠️ Important Risk Warning / 重要风险警告

**🚨 Trading Risk Notice / 交易风险提示:**

This program uses AI technology to save manpower and provide 24/7 tireless market analysis and trading execution capabilities. AI's advantages include comprehensive perspective, rational decision-making, and continuous operation, but:

**No person or AI can guarantee trading profits!** Cryptocurrency trading involves extremely high risks and may result in total loss of funds. Before using this software, please:

本程序使用 AI 技术节省人力，提供 24 小时不知疲倦的市场分析和交易执行能力。AI 的优势在于视角全面、决策理性、持续运行，但是：

**任何人和任何 AI 都无法保证交易盈利！** 加密货币交易存在极高风险，可能导致全部资金损失。使用本软件前请：

- 📚 **Fully understand trading risks / 充分了解交易风险**
- 💰 **Only invest funds you can afford to lose / 只投入可承受损失的资金**
- 🧪 **Test in simulation environment first / 先在模拟环境测试**
- 📖 **Learn relevant trading knowledge / 学习相关交易知识**
- ⚖️ **Comply with local laws and regulations / 遵守当地法律法规**

**By using this software, you acknowledge and accept all risks!**  
**使用本软件即表示您已理解并接受所有风险！**

---

## ✨ Key Features / 核心特性

### 🤖 AI-Driven Analysis

- **🧠 xAI Grok-4 Integration**: Advanced large language model for deep market analysis / 先进的大语言模型提供深度市场分析
- **📊 Multi-Timeframe Analysis**: Multi-timeframe technical indicator analysis / 多时间框架技术指标分析
- **🎯 Structured Decision Making**: Structured output ensures decision reliability / 结构化输出确保决策可靠性
- **📈 Real-time Market Sentiment**: Real-time market sentiment analysis / 实时市场情绪分析

### 🔄 Automated Trading

- **⚡ 24/7 Operation**: Round-the-clock automated trading execution / 全天候自动化交易执行
- **🎛️ Configurable Intervals**: Configurable execution intervals / 可配置的执行间隔
- **🛡️ Risk Management**: Built-in take-profit and stop-loss mechanisms / 内置止盈止损机制
- **📋 Position Management**: Intelligent position management and closing strategies / 智能仓位管理和平仓策略

### 📡 Data Integration

- **🌐 Real-time Market Data**: OKX WebSocket real-time market data / OKX WebSocket 实时市场数据
- **📊 Technical Indicators**: 50+ professional technical indicators / 50+ 专业技术指标
- **💹 Volume Profile Analysis**: Volume distribution analysis / 成交量分布分析
- **📈 Performance Tracking**: Detailed trading performance tracking / 详细的交易绩效跟踪

### 🏗️ Architecture

- **🔌 Modular Design**: Modular design for easy extension / 模块化设计便于扩展
- **📝 Comprehensive Logging**: Complete logging system / 完整的日志记录系统
- **🔧 Easy Configuration**: Simple configuration management / 简单的配置管理
- **🐳 Docker Support**: Docker containerized deployment support / Docker 容器化部署支持

---

## 🚀 Quick Start / 快速开始

### 📋 System Requirements / 系统要求

- **Python**: 3.8+
- **Operating System**: Linux, macOS, Windows
- **Memory**: At least 1GB RAM / 至少 1GB RAM
- **Network**: Stable internet connection / 稳定的网络连接

### 🛠️ Installation / 安装步骤

1. **Clone Repository / 克隆仓库**

   ```bash
   git clone https://github.com/yourusername/OpenLucky.git
   cd OpenLucky
   ```

2. **Install Dependencies / 安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys / 配置 API 密钥**

   ```bash
   cp config.ini.template config.ini
   # Edit config.ini and fill in your API keys
   # 编辑 config.ini，填入您的API密钥
   ```

4. **Get API Keys / 获取 API 密钥**
   - **OKX API**: [https://www.okx.com/account/my-api](https://www.okx.com/account/my-api)
   - **xAI API**: [https://console.x.ai/](https://console.x.ai/)

### 🏃‍♂️ Running the Bot / 运行程序

1. **Start Market Data Sync / 启动市场数据同步**

   ```bash
   python okx_sync.py
   ```

2. **Run Trading Bot / 运行交易机器人**

   ```bash
   # Continuous mode / 持续运行模式
   python main.py

   # Single execution mode / 单次执行模式
   python main.py --once

   # Custom interval / 自定义间隔
   python main.py --interval 15
   ```

3. **View History (Optional) / 查看历史记录（可选）**
   ```bash
   python history.py
   ```

---

## 📁 Project Structure / 项目结构

```
OpenLucky/
├── 📄 main.py              # Main orchestrator / 主程序调度器
├── 🤖 ai_analyze.py        # AI analysis module / AI分析模块
├── 📊 okx_market.py        # Market analysis / 市场分析
├── 💰 okx_account.py       # Account reporting / 账户报告
├── ⚡ okx_execute.py       # Trade execution / 交易执行
├── 🔄 okx_sync.py          # Data synchronization / 数据同步
├── ⏰ okx_time_utils.py    # Time utilities / 时间工具
├── 📜 history.py           # History viewer / 历史记录
├── ⚙️ config.ini.template  # Config template / 配置模板
├── 📋 requirements.txt     # Dependencies / 依赖列表
├── 📖 prompt.md            # AI prompts / AI提示词
├── 📏 trade_rules.md       # Trading rules / 交易规则
├── 🐳 Dockerfile          # Docker config / Docker配置
├── 📚 docs/               # Documentation / 文档目录
│   ├── okx-api-v5.md      # OKX API docs / OKX API文档
│   ├── okx-api-tricks.md  # API tricks / API使用技巧
│   └── xai_grok_structured_outputs.markdown
└── 📊 examples/           # Example files / 示例文件
    ├── sample_account.md
    ├── sample_market.md
    └── sample_decision.json
```

---

## 🔮 Development Roadmap / 开发路线图

### 🎯 v1.0 (Current / 当前版本)

- ✅ xAI Grok-4 Integration / xAI Grok-4 集成
- ✅ OKX Exchange Support / OKX 交易所支持
- ✅ Automated Trading Execution / 自动化交易执行
- ✅ Real-time Market Analysis / 实时市场分析
- ✅ Risk Management System / 风险管理系统

### 🚀 v2.0 (Planned / 计划中)

- 🔄 **Multiple AI Model Support / 多 AI 模型支持**
  - OpenAI GPT-4
  - Anthropic Claude
  - Google Gemini
  - Local open-source models / 本地开源模型

### 🌐 v3.0 (Future / 未来版本)

- 🏦 **Multiple Exchange Support / 多交易平台支持**
  - Binance
  - Bybit
  - Coinbase
  - Kraken

### 💹 v4.0 (Long-term / 长期规划)

- 📈 **Traditional Financial Markets / 传统金融市场**
  - Stock Trading / 股票交易
  - Gold Futures / 黄金期货
  - Forex Market / 外汇市场
  - Commodity Futures / 商品期货

---

## 📜 Disclaimer / 免责声明

This software provides AI analysis for reference only and does not constitute investment advice. Cryptocurrency trading involves significant financial risks and may result in partial or total loss of funds. All risks associated with using this software for actual trading are borne by the user.

本软件提供的 AI 分析仅供参考，不构成投资建议。加密货币交易涉及重大财务风险，可能导致部分或全部资金损失。使用本软件进行实际交易的所有风险由用户自行承担。

The developers are not responsible for any trading losses, technical failures, or other issues. Please fully understand the risks and make prudent decisions before use.

开发者不对任何交易损失、技术故障或其他问题承担责任。使用前请充分了解相关风险并谨慎决策。

---

<div align="center">

**🍀 Good Luck with Your Trading! / 祝您交易顺利！🍀**

Made with ❤️ by t7aliang

⭐ **If this project helps you, please give us a Star!**  
⭐ **如果这个项目对您有帮助，请给我一个 Star！**

---

## 💝 Support the Project / 支持项目

⭐ **If you are fortunate enough to make a lot of money, please feel free to donate. I am still completely unemployed and need everyone's support and encouragement.**

⭐ **如果你有幸赚了很多，请不吝捐赠，我还处于完全失业中，需要大家的支持和鼓励**

If OpenLucky has helped you achieve profits, welcome to support the project development through:

如果 OpenLucky 帮助您获得了收益，欢迎通过以下方式支持项目发展：

<div align="center">

### 💰 Cryptocurrency Donations / 加密货币捐赠

|            USDT (Tron Network)             |              USDC (Polygon Network)               |
| :----------------------------------------: | :-----------------------------------------------: |
| ![USDT-TRX](docs/OpenLucky-USDT-Tron.jpeg) | ![USDC-Polygon](docs/OpenLucky-USDC-Polygon.jpeg) |
|              **USDT (TRC20)**              |                **USDC (Polygon)**                 |

</div>

Every bit of your support is the greatest encouragement for open source projects! 🙏

您的每一份支持都是对开源项目最大的鼓励！🙏

</div>
