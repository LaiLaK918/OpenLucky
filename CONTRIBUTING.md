# 🤝 贡献指南 / Contributing Guide

感谢您对 OpenLucky 项目的关注！欢迎所有形式的贡献，包括代码、文档、问题报告和功能建议。

Thank you for your interest in the OpenLucky project! We welcome all forms of contributions, including code, documentation, issue reports, and feature suggestions.

---

## 🚀 快速开始 / Quick Start

### 🔧 开发环境设置 / Development Environment Setup

1. **Fork 项目 / Fork the Project**
   ```bash
   # 在GitHub上点击Fork按钮
   # Click the Fork button on GitHub
   ```

2. **克隆您的Fork / Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/OpenLucky.git
   cd OpenLucky
   ```

3. **设置上游仓库 / Set Up Upstream**
   ```bash
   git remote add upstream https://github.com/originalowner/OpenLucky.git
   ```

4. **安装开发依赖 / Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   # 可选：安装开发工具 / Optional: Install development tools
   # pip install black flake8 pytest
   ```

---

## 📋 贡献类型 / Types of Contributions

### 🐛 问题报告 / Bug Reports

发现bug时，请创建详细的issue报告：

When you find a bug, please create a detailed issue report:

**包含信息 / Include Information:**
- 🖥️ 操作系统和Python版本 / OS and Python version
- 📋 复现步骤 / Steps to reproduce
- 🎯 期望行为 / Expected behavior
- 💥 实际行为 / Actual behavior
- 📄 错误日志 / Error logs
- ⚙️ 配置信息（隐藏API密钥）/ Configuration (hide API keys)

### 💡 功能建议 / Feature Requests

提出新功能建议时，请说明：

When suggesting new features, please explain:

- 🎯 **使用场景** / Use case: 为什么需要这个功能？
- 📝 **详细描述** / Detailed description: 功能应该如何工作？
- 🔧 **实现建议** / Implementation suggestions: 有技术实现想法吗？
- 🚀 **优先级** / Priority: 这个功能有多重要？

### 🔧 代码贡献 / Code Contributions

#### 📐 代码规范 / Code Standards

**Python代码风格 / Python Code Style:**
- 遵循 PEP 8 规范 / Follow PEP 8 guidelines
- 使用类型注解 / Use type hints
- 编写清晰的docstring / Write clear docstrings
- 保持函数简洁 / Keep functions concise

**示例 / Example:**
```python
def calculate_position_size(
    available_balance: float, 
    leverage: int, 
    price: float, 
    contract_value: float
) -> int:
    """
    计算合适的仓位大小
    Calculate appropriate position size
    
    Args:
        available_balance: 可用余额 / Available balance
        leverage: 杠杆倍数 / Leverage multiplier
        price: 当前价格 / Current price
        contract_value: 合约面值 / Contract value
        
    Returns:
        推荐的合约数量 / Recommended contract quantity
    """
    max_size = (available_balance * leverage) / (contract_value * price)
    return int(max_size * 0.7)  # 70% safety margin
```

#### 🔀 提交流程 / Submission Process

1. **创建功能分支 / Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **进行开发 / Make Changes**
   - 编写代码 / Write code
   - 添加测试 / Add tests (if applicable)
   - 更新文档 / Update documentation

3. **提交更改 / Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **同步上游更改 / Sync Upstream Changes**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

5. **推送分支 / Push Branch**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request / Create Pull Request**
   - 在GitHub上创建PR
   - 填写详细的PR描述
   - 关联相关的issue

#### 📝 提交信息规范 / Commit Message Convention

使用约定式提交格式 / Use Conventional Commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**类型 / Types:**
- `feat`: 新功能 / New feature
- `fix`: Bug修复 / Bug fix
- `docs`: 文档更新 / Documentation update
- `style`: 代码格式 / Code formatting
- `refactor`: 代码重构 / Code refactoring
- `test`: 测试相关 / Test related
- `chore`: 构建/工具相关 / Build/tooling related

**示例 / Examples:**
```
feat(ai): add support for GPT-4 model
fix(okx): handle WebSocket reconnection properly
docs(readme): update installation instructions
```

---

## 🧪 测试指南 / Testing Guidelines

### 🔍 测试类型 / Test Types

1. **单元测试 / Unit Tests**
   - 测试独立功能模块 / Test individual modules
   - 使用模拟数据 / Use mock data
   - 覆盖边界情况 / Cover edge cases

2. **集成测试 / Integration Tests**
   - 测试API连接 / Test API connections
   - 验证数据流程 / Verify data flow
   - 模拟交易环境 / Simulate trading environment

3. **手动测试 / Manual Testing**
   - 在测试环境运行 / Run in test environment
   - 验证输出格式 / Verify output formats
   - 检查日志完整性 / Check log completeness

### 🛡️ 安全测试 / Security Testing

- 验证API密钥不会泄露 / Verify API keys don't leak
- 检查配置文件权限 / Check config file permissions
- 测试异常情况处理 / Test exception handling

---

## 📚 文档贡献 / Documentation Contributions

### 📖 文档类型 / Documentation Types

1. **用户文档 / User Documentation**
   - 安装和配置指南 / Installation and configuration guides
   - 使用教程和示例 / Usage tutorials and examples
   - 常见问题解答 / FAQ

2. **开发者文档 / Developer Documentation**
   - API参考文档 / API reference documentation
   - 架构设计文档 / Architecture design documentation
   - 代码注释和docstring / Code comments and docstrings

3. **翻译贡献 / Translation Contributions**
   - 中英文双语维护 / Maintain bilingual Chinese-English
   - 确保翻译准确性 / Ensure translation accuracy
   - 保持格式一致性 / Maintain format consistency

---

## 🔄 发布流程 / Release Process

### 📋 版本规划 / Version Planning

使用语义化版本控制 / We use Semantic Versioning:

- **主版本号 / Major**: 不兼容的API更改 / Incompatible API changes
- **次版本号 / Minor**: 向后兼容的功能添加 / Backward compatible feature additions  
- **修订号 / Patch**: 向后兼容的bug修复 / Backward compatible bug fixes

### 🚀 发布检查清单 / Release Checklist

- [ ] 所有测试通过 / All tests pass
- [ ] 文档更新完整 / Documentation is complete
- [ ] CHANGELOG.md 已更新 / CHANGELOG.md updated
- [ ] 版本号已更新 / Version number updated
- [ ] 安全审查完成 / Security review completed

---

## 💬 社区交流 / Community Communication

### 📢 交流渠道 / Communication Channels

- **GitHub Issues**: 问题报告和功能请求 / Bug reports and feature requests
- **GitHub Discussions**: 社区讨论和经验分享 / Community discussions and experience sharing
- **Pull Requests**: 代码审查和技术讨论 / Code review and technical discussions

### 🤝 社区准则 / Community Guidelines

1. **友善尊重** / Be Respectful: 尊重所有贡献者和用户
2. **建设性沟通** / Constructive Communication: 提供有建设性的反馈
3. **技术导向** / Technical Focus: 保持讨论的技术性和专业性
4. **开放包容** / Open and Inclusive: 欢迎不同背景的贡献者

---

## 🎯 开发优先级 / Development Priorities

### 🔥 高优先级 / High Priority
- 🐛 Bug修复和稳定性改进 / Bug fixes and stability improvements
- 🔒 安全性增强 / Security enhancements
- 📊 性能优化 / Performance optimizations
- 📝 文档完善 / Documentation improvements

### 🚀 中优先级 / Medium Priority
- 🤖 新AI模型集成 / New AI model integration
- 🏦 新交易所支持 / New exchange support
- 🔧 开发工具改进 / Development tooling improvements
- 🧪 测试覆盖率提升 / Test coverage improvements

### 💡 低优先级 / Low Priority
- 🎨 UI/UX改进 / UI/UX improvements
- 🌐 国际化支持 / Internationalization support
- 📱 移动端适配 / Mobile adaptation
- 🔌 插件系统 / Plugin system

---

## 🙏 致谢 / Acknowledgments

感谢所有为 OpenLucky 项目做出贡献的开发者！

Thanks to all developers who contribute to the OpenLucky project!

您的每一个贡献都让这个项目变得更好。无论是代码、文档、问题报告还是功能建议，非常感激。

Every contribution you make helps improve this project. Whether it's code, documentation, bug reports, or feature suggestions, we greatly appreciate it.

---

## 📞 联系方式 / Contact

如果您有任何问题或建议，请通过以下方式联系我：

If you have any questions or suggestions, please contact us through:

- 📋 **GitHub Issues**: [项目Issues页面 / Project Issues Page](https://github.com/t7aliang/OpenLucky/issues)
- 💬 **GitHub Discussions**: [项目讨论页面 / Project Discussions Page](https://github.com/t7aliang/OpenLucky/discussions)

---

<div align="center">

**🍀 感谢您的贡献！/ Thank you for your contributions! 🍀**

Made with ❤️ by t7alaing

</div>
