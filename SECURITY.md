# 🔒 安全说明 / Security Guidelines

OpenLucky 项目重视用户的资金安全和隐私保护。请仔细阅读以下安全指南。

The OpenLucky project values user fund security and privacy protection. Please carefully read the following security guidelines.

---

## 🔑 API 密钥安全 / API Key Security

### ⚠️ 关键安全原则 / Critical Security Principles

1. **绝不分享API密钥** / Never Share API Keys
   - 不要在任何公共场所分享您的API密钥
   - 不要将API密钥提交到版本控制系统
   - 不要在截图或日志中暴露API密钥

2. **最小权限原则** / Principle of Least Privilege
   - 只授予必要的API权限
   - 定期审查和轮换API密钥
   - 使用IP白名单限制访问

3. **安全存储** / Secure Storage
   - 将 `config.ini` 文件权限设置为仅所有者可读
   - 考虑使用环境变量存储敏感信息
   - 定期备份配置文件（去除敏感信息）

### 🔧 OKX API 安全配置 / OKX API Security Configuration

**推荐的API权限设置 / Recommended API Permission Settings:**

✅ **需要的权限 / Required Permissions:**
- 📊 **读取** / Read: 账户信息、市场数据、订单信息
- 💼 **交易** / Trade: 下单、撤单、查询订单

❌ **不需要的权限 / Unnecessary Permissions:**
- 💸 **提币** / Withdraw: 绝对不要开启！/ Never enable!
- 🔄 **转账** / Transfer: 不需要 / Not required

**API密钥配置建议 / API Key Configuration Recommendations:**

```ini
[OKX]
# 使用专门的交易API密钥，不要使用主账户密钥
# Use dedicated trading API key, not main account key
api_key = your_trading_api_key
api_secret = your_trading_api_secret
api_passphrase = your_trading_passphrase
```

### 🌐 xAI API 安全 / xAI API Security

**xAI API 安全要点 / xAI API Security Points:**

- 🔑 仅用于AI分析，不涉及资金操作 / Only for AI analysis, no fund operations
- 📊 不会传输敏感的账户信息 / Does not transmit sensitive account information
- 🛡️ 使用HTTPS加密传输 / Uses HTTPS encrypted transmission

---

## 🛡️ 系统安全 / System Security

### 🔒 本地安全 / Local Security

1. **文件权限 / File Permissions**
   ```bash
   # 设置配置文件仅所有者可读 / Set config file readable by owner only
   chmod 600 config.ini
   
   # 设置数据目录权限 / Set data directory permissions
   chmod 755 data/
   chmod 644 data/*.json
   ```

2. **环境隔离 / Environment Isolation**
   ```bash
   # 使用虚拟环境 / Use virtual environment
   python -m venv openlucky-env
   source openlucky-env/bin/activate  # Linux/Mac
   # openlucky-env\Scripts\activate   # Windows
   ```

3. **网络安全 / Network Security**
   - 使用防火墙保护系统 / Use firewall to protect system
   - 定期更新系统和依赖 / Regularly update system and dependencies
   - 监控异常网络活动 / Monitor unusual network activity

### 🐳 Docker 安全 / Docker Security

**Docker安全最佳实践 / Docker Security Best Practices:**

1. **非root用户运行 / Run as Non-root User**
   ```dockerfile
   # Dockerfile 已配置非root用户
   # Dockerfile already configured with non-root user
   USER appuser
   ```

2. **只读挂载配置文件 / Read-only Mount Config Files**
   ```bash
   docker run -v ./config.ini:/app/config.ini:ro openlucky
   ```

3. **网络隔离 / Network Isolation**
   ```yaml
   # docker-compose.yml 已配置专用网络
   # docker-compose.yml already configured with dedicated network
   networks:
     - openlucky-network
   ```

---

## 🚨 风险管理 / Risk Management

### 💰 资金安全 / Fund Security

1. **测试环境优先 / Test Environment First**
   - 始终先在OKX模拟环境测试 / Always test in OKX simulation environment first
   - 验证所有功能正常后再使用真实资金 / Use real funds only after verifying all functions

2. **资金分配策略 / Fund Allocation Strategy**
   - 只使用可承受损失的资金 / Only use funds you can afford to lose
   - 建议初始投入不超过总资产的5-10% / Recommend initial investment not exceeding 5-10% of total assets
   - 设置严格的止损限制 / Set strict stop-loss limits

3. **监控和控制 / Monitoring and Control**
   - 定期检查交易日志 / Regularly check trading logs
   - 监控账户余额变化 / Monitor account balance changes
   - 设置异常情况警报 / Set up alerts for unusual situations

### 📊 技术风险 / Technical Risks

1. **网络连接 / Network Connection**
   - 确保稳定的网络连接 / Ensure stable network connection
   - 配置网络异常时的应急措施 / Configure emergency measures for network failures
   - 监控API连接状态 / Monitor API connection status

2. **数据完整性 / Data Integrity**
   - 定期验证市场数据准确性 / Regularly verify market data accuracy
   - 检查技术指标计算正确性 / Check technical indicator calculation correctness
   - 备份重要的历史数据 / Backup important historical data

---

## 🆘 应急处理 / Emergency Procedures

### 🛑 紧急停止 / Emergency Stop

**如何立即停止交易机器人 / How to immediately stop the trading bot:**

1. **键盘中断 / Keyboard Interrupt**
   ```bash
   # 在运行终端按 Ctrl+C
   # Press Ctrl+C in the running terminal
   ```

2. **进程终止 / Process Termination**
   ```bash
   # 查找进程ID / Find process ID
   ps aux | grep python
   
   # 终止进程 / Terminate process
   kill -TERM <process_id>
   ```

3. **Docker停止 / Docker Stop**
   ```bash
   # 停止Docker容器 / Stop Docker container
   docker stop openlucky-bot
   ```

### 🔧 故障排除 / Troubleshooting

**常见问题和解决方案 / Common Issues and Solutions:**

1. **API连接失败 / API Connection Failure**
   - 检查网络连接 / Check network connection
   - 验证API密钥有效性 / Verify API key validity
   - 检查API权限设置 / Check API permission settings

2. **数据同步问题 / Data Sync Issues**
   - 重启数据同步程序 / Restart data sync program
   - 检查磁盘空间 / Check disk space
   - 清理损坏的数据文件 / Clean corrupted data files

3. **交易执行异常 / Trading Execution Errors**
   - 检查账户余额充足性 / Check account balance sufficiency
   - 验证交易参数正确性 / Verify trading parameter correctness
   - 查看详细错误日志 / Check detailed error logs

---

## 📞 安全问题报告 / Security Issue Reporting

如果您发现安全漏洞，请通过以下方式报告：

If you discover security vulnerabilities, please report them through:

### 🔐 私密报告 / Private Reporting

**请不要在公开issue中报告安全问题！**  
**Please do not report security issues in public issues!**

1. **GitHub Security Advisory**: 使用GitHub的安全咨询功能
2. **私人联系**: 通过项目维护者的私人联系方式

### 📋 报告内容 / Report Content

请在安全报告中包含：

Please include in your security report:

- 🎯 漏洞详细描述 / Detailed vulnerability description
- 🔧 复现步骤 / Steps to reproduce
- 💥 潜在影响 / Potential impact
- 🛠️ 修复建议 / Fix suggestions (if any)

---

## 🔄 安全更新 / Security Updates

我会：

I try to:

- 📅 **快速响应**: 24小时内确认安全报告 / Quick response: Confirm security reports within 24 hours
- 🔧 **及时修复**: 7天内发布安全补丁 / Timely fixes: Release security patches within 7 days
- 📢 **透明沟通**: 及时通知用户安全更新 / Transparent communication: Notify users of security updates promptly

---

<div align="center">

**🔒 您的安全是首要任务！**  
**Your security is our top priority!**

</div>
