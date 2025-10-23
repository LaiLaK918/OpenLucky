# 🔒 Security Guidelines / 安全说明

The OpenLucky project values user fund security and privacy protection. Please carefully read the following security guidelines.

OpenLucky 项目重视用户的资金安全和隐私保护。请仔细阅读以下安全指南。

---

## 🔑 API Key Security / API 密钥安全

### ⚠️ Critical Security Principles / 关键安全原则

1. **Never Share API Keys / 绝不分享 API 密钥**

   - Do not share your API keys in any public places / 不要在任何公共场所分享您的 API 密钥
   - Do not commit API keys to version control systems / 不要将 API 密钥提交到版本控制系统
   - Do not expose API keys in screenshots or logs / 不要在截图或日志中暴露 API 密钥

2. **Principle of Least Privilege / 最小权限原则**

   - Only grant necessary API permissions / 只授予必要的 API 权限
   - Regularly review and rotate API keys / 定期审查和轮换 API 密钥
   - Use IP whitelist to restrict access / 使用 IP 白名单限制访问

3. **Secure Storage / 安全存储**
   - Set config.ini file permissions to owner-read only / 将 `config.ini` 文件权限设置为仅所有者可读
   - Consider using environment variables to store sensitive information / 考虑使用环境变量存储敏感信息
   - Regularly backup configuration files (removing sensitive information) / 定期备份配置文件（去除敏感信息）

### 🔧 OKX API Security Configuration / OKX API 安全配置

**Recommended API Permission Settings / 推荐的 API 权限设置:**

✅ **Required Permissions / 需要的权限:**

- 📊 **Read / 读取**: Account info, market data, order info / 账户信息、市场数据、订单信息
- 💼 **Trade / 交易**: Place orders, cancel orders, query orders / 下单、撤单、查询订单

❌ **Unnecessary Permissions / 不需要的权限:**

- 💸 **Withdraw / 提币**: Never enable! / 绝对不要开启！
- 🔄 **Transfer / 转账**: Not required / 不需要

**API Key Configuration Recommendations / API 密钥配置建议:**

```ini
[OKX]
# Use dedicated trading API key, not main account key / 使用专门的交易API密钥，不要使用主账户密钥
api_key = your_trading_api_key
api_secret = your_trading_api_secret
api_passphrase = your_trading_passphrase
```

### 🌐 xAI API Security / xAI API 安全

**xAI API Security Points / xAI API 安全要点:**

- 🔑 Only for AI analysis, no fund operations / 仅用于 AI 分析，不涉及资金操作
- 📊 Does not transmit sensitive account information / 不会传输敏感的账户信息
- 🛡️ Uses HTTPS encrypted transmission / 使用 HTTPS 加密传输

---

## 🛡️ System Security / 系统安全

### 🔒 Local Security / 本地安全

1. **File Permissions / 文件权限**

   ```bash
   # Set config file readable by owner only / 设置配置文件仅所有者可读
   chmod 600 config.ini

   # Set data directory permissions / 设置数据目录权限
   chmod 755 data/
   chmod 644 data/*.json
   ```

2. **Environment Isolation / 环境隔离**

   ```bash
   # Use virtual environment / 使用虚拟环境
   python -m venv openlucky-env
   source openlucky-env/bin/activate  # Linux/Mac
   # openlucky-env\Scripts\activate   # Windows
   ```

3. **Network Security / 网络安全**
   - Use firewall to protect system / 使用防火墙保护系统
   - Regularly update system and dependencies / 定期更新系统和依赖
   - Monitor unusual network activity / 监控异常网络活动

### 🐳 Docker Security / Docker 安全

**Docker Security Best Practices / Docker 安全最佳实践:**

1. **Run as Non-root User / 非 root 用户运行**

   ```dockerfile
   # Dockerfile already configured with non-root user / Dockerfile 已配置非root用户
   USER appuser
   ```

2. **Read-only Mount Config Files / 只读挂载配置文件**

   ```bash
   docker run -v ./config.ini:/app/config.ini:ro openlucky
   ```

3. **Network Isolation / 网络隔离**
   ```yaml
   # docker-compose.yml already configured with dedicated network / docker-compose.yml 已配置专用网络
   networks:
     - openlucky-network
   ```

---

## 🚨 Risk Management / 风险管理

### 💰 Fund Security / 资金安全

1. **Test Environment First / 测试环境优先**

   - Always test in OKX simulation environment first / 始终先在 OKX 模拟环境测试
   - Use real funds only after verifying all functions / 验证所有功能正常后再使用真实资金

2. **Fund Allocation Strategy / 资金分配策略**

   - Only use funds you can afford to lose / 只使用可承受损失的资金
   - Recommend initial investment not exceeding 5-10% of total assets / 建议初始投入不超过总资产的 5-10%
   - Set strict stop-loss limits / 设置严格的止损限制

3. **Monitoring and Control / 监控和控制**
   - Regularly check trading logs / 定期检查交易日志
   - Monitor account balance changes / 监控账户余额变化
   - Set up alerts for unusual situations / 设置异常情况警报

### 📊 Technical Risks / 技术风险

1. **Network Connection / 网络连接**

   - Ensure stable network connection / 确保稳定的网络连接
   - Configure emergency measures for network failures / 配置网络异常时的应急措施
   - Monitor API connection status / 监控 API 连接状态

2. **Data Integrity / 数据完整性**
   - Regularly verify market data accuracy / 定期验证市场数据准确性
   - Check technical indicator calculation correctness / 检查技术指标计算正确性
   - Backup important historical data / 备份重要的历史数据

---

## 🆘 Emergency Procedures / 应急处理

### 🛑 Emergency Stop / 紧急停止

**How to immediately stop the trading bot / 如何立即停止交易机器人:**

1. **Keyboard Interrupt / 键盘中断**

   ```bash
   # Press Ctrl+C in the running terminal / 在运行终端按 Ctrl+C
   ```

2. **Process Termination / 进程终止**

   ```bash
   # Find process ID / 查找进程ID
   ps aux | grep python

   # Terminate process / 终止进程
   kill -TERM <process_id>
   ```

3. **Docker Stop / Docker 停止**
   ```bash
   # Stop Docker container / 停止Docker容器
   docker stop openlucky-bot
   ```

### 🔧 Troubleshooting / 故障排除

**Common Issues and Solutions / 常见问题和解决方案:**

1. **API Connection Failure / API 连接失败**

   - Check network connection / 检查网络连接
   - Verify API key validity / 验证 API 密钥有效性
   - Check API permission settings / 检查 API 权限设置

2. **Data Sync Issues / 数据同步问题**

   - Restart data sync program / 重启数据同步程序
   - Check disk space / 检查磁盘空间
   - Clean corrupted data files / 清理损坏的数据文件

3. **Trading Execution Errors / 交易执行异常**
   - Check account balance sufficiency / 检查账户余额充足性
   - Verify trading parameter correctness / 验证交易参数正确性
   - Check detailed error logs / 查看详细错误日志

---

## 📞 Security Issue Reporting / 安全问题报告

If you discover security vulnerabilities, please report them through:

如果您发现安全漏洞，请通过以下方式报告：

### 🔐 Private Reporting / 私密报告

**Please do not report security issues in public issues! / 请不要在公开 issue 中报告安全问题！**

1. **GitHub Security Advisory**: Use GitHub's security advisory feature / 使用 GitHub 的安全咨询功能
2. **Private Contact**: Through project maintainer's private contact / 通过项目维护者的私人联系方式

### 📋 Report Content / 报告内容

Please include in your security report: / 请在安全报告中包含：

- 🎯 Detailed vulnerability description / 漏洞详细描述
- 🔧 Steps to reproduce / 复现步骤
- 💥 Potential impact / 潜在影响
- 🛠️ Fix suggestions (if any) / 修复建议

---

## 🔄 Security Updates / 安全更新

I try to: / 我会：

- 📅 **Quick response**: Confirm security reports within 24 hours / **快速响应**: 24 小时内确认安全报告
- 🔧 **Timely fixes**: Release security patches within 7 days / **及时修复**: 7 天内发布安全补丁
- 📢 **Transparent communication**: Notify users of security updates promptly / **透明沟通**: 及时通知用户安全更新

---

<div align="center">

**🔒 Your security is our top priority! / 您的安全是首要任务！**

</div>
