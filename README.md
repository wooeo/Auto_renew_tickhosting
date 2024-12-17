# Tick Hosting Auto Renew

自动续期 Tick Hosting 免费服务器的脚本，使用 GitHub Actions 每96小时自动运行一次。

## 功能特点

- 自动登录 Tick Hosting
- 自动点击续期按钮
- 验证续期是否成功
- 每96小时自动运行
- 支持手动触发运行

## 使用方法

### 1. 获取 Cookie

1. 登录 [Tick Hosting](https://tickhosting.com/auth/login)
2. 打开浏览器开发者工具（F12）
3. 切换到 Network 标签页
4. 刷新页面
5. 在请求中找到 `pterodactyl_session` cookie 的值

### 2. 设置 GitHub Actions

1. Fork 这个仓库
2. 在仓库中设置 Secret：
   - 进入仓库的 Settings
   - 点击 Secrets and variables -> Actions
   - 点击 New repository secret
   - Name: `PTERODACTYL_SESSION`
   - Value: 您获取到的 pterodactyl_session cookie 值

### 3. 验证运行

- Actions 将每96小时(4天)自动运行一次
- 您可以在 Actions 页面查看运行状态和日志
- 需要立即运行时，可以在 Actions 页面手动触发

## 项目结构

```
.
├── .github/workflows/    # GitHub Actions 配置
│   └── auto_renew.yml   # 工作流配置文件
├── auto_renew.py        # 主程序脚本
├── requirements.txt     # Python 依赖
└── README.md           # 项目说明
```

## 依赖

- Python 3.x
- Selenium
- Chrome 浏览器

## 本地运行

如果需要在本地运行测试：

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置环境变量：
```bash
# Windows
set PTERODACTYL_SESSION=你的cookie值

# Linux/Mac
export PTERODACTYL_SESSION=你的cookie值
```

3. 运行脚本：
```bash
python auto_renew.py
```

## 注意事项

- 请确保 cookie 值保密，不要泄露给他人
- 如果登录失败，请更新 cookie 值
- 建议定期检查 Actions 运行日志，确保脚本正常运行
- 如果需要修改运行频率，可以调整 `.github/workflows/auto_renew.yml` 中的 cron 表达式
