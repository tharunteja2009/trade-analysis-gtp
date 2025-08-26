# 📈 AI-Powered Stock Trade Analysis

A sophisticated stock analysis application that leverages AI agents to provide comprehensive market insights and investment recommendations for Indian stocks. Built with AutoGen multi-agent framework and Streamlit.

## 🌟 Features

- **🤖 Multi-Agent AI Analysis**: Specialized AI agents for data collection and analysis
- **📊 Real-time Market Data**: Live stock prices, volume, 52-week ranges
- **📈 Financial Intelligence**: P/E ratio, market cap, profit margins, fundamentals
- **🎯 Smart Recommendations**: AI-powered BUY/SELL/HOLD analysis
- **🌐 Beautiful Web Interface**: Responsive Streamlit application
- **💼 Indian Stock Focus**: NSE/BSE stocks with proper formatting

## 🛠️ Technology Stack

- **AI Framework**: AutoGen Agent Chat
- **Data Source**: yfinance API
- **Web Framework**: Streamlit
- **Language**: Python 3.10+
- **Environment**: Conda

## 📁 Project Structure

```
trade-analysis-gtp/
├── main.py                    # Console version
├── streamlit_app.py          # Web application
├── utils/
│   └── number_formatter.py  # Number formatting utilities
└── ai/
    ├── agents/              # AI agents
    ├── teams/              # Agent orchestration
    └── tools/              # Data collection tools
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/tharunteja2009/trade-analysis-gtp.git
cd trade-analysis-gtp

# Create conda environment
conda create -n trade-analysis-gtp python=3.10
conda activate trade-analysis-gtp

# Install dependencies
pip install streamlit yfinance autogen-agentchat autogen-core
```

### 2. Run Application

**Web Interface (Recommended):**
```bash
conda run --live-stream --name trade-analysis-gtp streamlit run streamlit_app.py
```
Visit: http://localhost:8501

**Console Version:**
```bash
conda run --live-stream --name trade-analysis-gtp python main.py
```

## 📱 Usage

1. **Enter stock symbol** (e.g., TCS, HDFC Bank, RELIANCE, INFY)
2. **Click "Analyze Stock"** 

### Sample Stocks
- **TCS** - Tata Consultancy Services
- **HDFC Bank** - HDFC Bank Limited  
- **RELIANCE** - Reliance Industries
- **INFY** - Infosys Limited
- **CDSL** - Central Depository Services

### Multi-Agent Architecture
1. **Data Collection Agent**: Fetches stock data
2. **Analysis Agent**: Provides investment recommendations
3. **Team Orchestration**: Coordinates agent workflow

---

**Happy Trading! 📈** *Always do your own research before investing.*
