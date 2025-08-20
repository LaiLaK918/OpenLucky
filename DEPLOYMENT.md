# 🚀 部署指南 / Deployment Guide

本文档提供了 OpenLucky 在不同环境下的详细部署说明。

This document provides detailed deployment instructions for OpenLucky in different environments.

---

## 🖥️ 本地部署 / Local Deployment

### 🛠️ 快速安装 / Quick Installation

**Linux/macOS:**
```bash
# 使用安装脚本 / Use installation script
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
REM 运行Windows安装脚本 / Run Windows installation script
install.bat
```

### 📝 手动安装 / Manual Installation

1. **环境准备 / Environment Preparation**
   ```bash
   # 创建虚拟环境 / Create virtual environment
   python -m venv openlucky-env
   
   # 激活虚拟环境 / Activate virtual environment
   source openlucky-env/bin/activate  # Linux/Mac
   openlucky-env\Scripts\activate     # Windows
   ```

2. **安装依赖 / Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **配置设置 / Configuration Setup**
   ```bash
   cp config.ini.template config.ini
   # 编辑 config.ini 添加API密钥
   # Edit config.ini to add API keys
   ```

---

## 🐳 Docker 部署 / Docker Deployment

### 🔨 单容器部署 / Single Container Deployment

1. **构建镜像 / Build Image**
   ```bash
   docker build -t openlucky:v1.0 .
   ```

2. **运行容器 / Run Container**
   ```bash
   # 创建必要目录 / Create necessary directories
   mkdir -p data logs
   
   # 运行容器 / Run container
   docker run -d \
     --name openlucky-bot \
     --restart unless-stopped \
     -v $(pwd)/config.ini:/app/config.ini:ro \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     openlucky:v1.0
   ```

3. **查看日志 / View Logs**
   ```bash
   docker logs -f openlucky-bot
   ```

### 🔧 Docker Compose 部署 / Docker Compose Deployment

1. **启动服务 / Start Services**
   ```bash
   # 启动所有服务 / Start all services
   docker-compose up -d
   
   # 查看服务状态 / Check service status
   docker-compose ps
   ```

2. **查看日志 / View Logs**
   ```bash
   # 查看所有服务日志 / View all service logs
   docker-compose logs -f
   
   # 查看特定服务日志 / View specific service logs
   docker-compose logs -f openlucky
   ```

3. **停止服务 / Stop Services**
   ```bash
   docker-compose down
   ```

---

## ☁️ 云服务器部署 / Cloud Server Deployment

### 🌐 VPS 部署建议 / VPS Deployment Recommendations

**推荐配置 / Recommended Configuration:**
- **CPU**: 1-2 cores
- **内存 / Memory**: 2GB+
- **存储 / Storage**: 20GB+
- **网络 / Network**: 稳定的网络连接

### 🔧 服务器配置 / Server Configuration

1. **系统更新 / System Update**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip git -y
   
   # CentOS/RHEL
   sudo yum update -y
   sudo yum install python3 python3-pip git -y
   ```

2. **防火墙配置 / Firewall Configuration**
   ```bash
   # 开放必要端口（如果需要Web界面）
   # Open necessary ports (if web interface needed)
   sudo ufw allow 22    # SSH
   sudo ufw allow 8080  # Web interface (optional)
   sudo ufw enable
   ```

3. **系统服务配置 / System Service Configuration**
   ```bash
   # 创建systemd服务文件 / Create systemd service file
   sudo tee /etc/systemd/system/openlucky.service > /dev/null <<EOF
   [Unit]
   Description=OpenLucky Trading Bot
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/OpenLucky
   ExecStart=/home/ubuntu/OpenLucky/openlucky-env/bin/python main.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # 启用并启动服务 / Enable and start service
   sudo systemctl enable openlucky
   sudo systemctl start openlucky
   ```

---

## 📊 监控和维护 / Monitoring & Maintenance

### 📈 系统监控 / System Monitoring

1. **服务状态检查 / Service Status Check**
   ```bash
   # 检查服务状态 / Check service status
   sudo systemctl status openlucky
   
   # 查看实时日志 / View real-time logs
   sudo journalctl -u openlucky -f
   ```

2. **资源使用监控 / Resource Usage Monitoring**
   ```bash
   # 内存使用 / Memory usage
   free -h
   
   # 磁盘使用 / Disk usage
   df -h
   
   # CPU使用 / CPU usage
   top -p $(pgrep -f "python.*main.py")
   ```

### 🔄 定期维护 / Regular Maintenance

1. **日志轮转 / Log Rotation**
   ```bash
   # 配置logrotate / Configure logrotate
   sudo tee /etc/logrotate.d/openlucky > /dev/null <<EOF
   /home/ubuntu/OpenLucky/*.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
       create 644 ubuntu ubuntu
   }
   EOF
   ```

2. **数据备份 / Data Backup**
   ```bash
   # 创建备份脚本 / Create backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   tar -czf "/backup/openlucky_backup_$DATE.tar.gz" \
       /home/ubuntu/OpenLucky/data/ \
       /home/ubuntu/OpenLucky/config.ini \
       /home/ubuntu/OpenLucky/*.log
   ```

3. **系统更新 / System Updates**
   ```bash
   # 定期更新依赖 / Regular dependency updates
   pip install --upgrade -r requirements.txt
   
   # 重启服务 / Restart service
   sudo systemctl restart openlucky
   ```

---

## 🔒 生产环境安全 / Production Security

### 🛡️ 安全加固 / Security Hardening

1. **SSH安全配置 / SSH Security Configuration**
   ```bash
   # 禁用密码登录，只允许密钥登录
   # Disable password login, only allow key login
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart ssh
   ```

2. **文件权限设置 / File Permission Settings**
   ```bash
   # 设置配置文件权限 / Set config file permissions
   chmod 600 config.ini
   chmod 755 *.py
   chmod 644 *.md
   ```

3. **自动安全更新 / Automatic Security Updates**
   ```bash
   # Ubuntu/Debian
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

### 📱 监控告警 / Monitoring & Alerts

1. **系统监控 / System Monitoring**
   - 使用 htop、iotop 监控系统资源
   - 配置邮件或短信告警
   - 设置磁盘空间告警

2. **应用监控 / Application Monitoring**
   - 监控交易执行状态
   - 跟踪API调用频率
   - 记录异常情况

---

## 🚀 性能优化 / Performance Optimization

### ⚡ 系统优化 / System Optimization

1. **内存优化 / Memory Optimization**
   ```bash
   # 配置swap / Configure swap
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **网络优化 / Network Optimization**
   - 使用CDN加速API访问
   - 配置DNS缓存
   - 优化TCP参数

### 📊 应用优化 / Application Optimization

1. **数据库优化 / Database Optimization**
   - 定期清理过期数据
   - 优化数据存储格式
   - 使用索引加速查询

2. **并发优化 / Concurrency Optimization**
   - 调整并发参数
   - 优化API调用频率
   - 使用连接池

---

## 🆘 故障排除 / Troubleshooting

### 🔍 常见问题 / Common Issues

1. **API连接问题 / API Connection Issues**
   ```bash
   # 测试网络连接 / Test network connection
   curl -I https://www.okx.com/api/v5/public/time
   curl -I https://api.x.ai/v1/models
   ```

2. **内存不足 / Out of Memory**
   ```bash
   # 检查内存使用 / Check memory usage
   ps aux --sort=-%mem | head
   
   # 重启服务释放内存 / Restart service to free memory
   sudo systemctl restart openlucky
   ```

3. **磁盘空间不足 / Disk Space Full**
   ```bash
   # 清理日志文件 / Clean log files
   find . -name "*.log" -mtime +7 -delete
   
   # 清理旧数据 / Clean old data
   find ./data -name "*.json" -mtime +30 -delete
   ```

### 📞 获取帮助 / Getting Help

如果遇到部署问题，请：

If you encounter deployment issues, please:

1. 📋 检查日志文件 / Check log files
2. 🔍 搜索已知问题 / Search known issues
3. 💬 在GitHub Discussions提问 / Ask in GitHub Discussions
4. 🐛 创建详细的Issue报告 / Create detailed Issue report

---

<div align="center">

**🍀 祝您部署顺利！/ Good Luck with Your Deployment! 🍀**

</div>
