# AIDEX

## 技术栈与功能特性

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) 作为Python后端API。
    - 🔍 [Pydantic](https://docs.pydantic.dev) 用于数据验证和设置管理。
    - 🧰 [Beanie](https://beanie-odm.dev/) 用于MongoDB数据库交互（ODM）。
    - 💾 [MongoDB](https://www.mongodb.com) 作为NoSQL数据库。
- 🚀 [React](https://react.dev) 作为前端框架。
    - 💃 使用TypeScript、React Hooks、Vite等现代前端技术栈。
    - 🎨 [Chakra UI](https://chakra-ui.com) 作为前端组件库。
    - 🛣️ [@tanstack/react-router](https://tanstack.com/router) 用于前端路由管理。
    - 🔄 [@tanstack/react-query](https://tanstack.com/query) 用于数据获取和状态管理。
    - 🤖 自动生成的前端API客户端。
    - 🧪 [Playwright](https://playwright.dev) 用于端到端测试。
    - 🦇 支持深色模式。
- 🐋 [Docker Compose](https://www.docker.com) 用于开发和生产环境部署。
- 🔒 默认安全的密码哈希处理。
- 🔑 JWT (JSON Web Token) 认证机制。
- 📫 基于电子邮件的密码恢复功能。
- ✅ 使用 [Pytest](https://pytest.org) 进行测试。
- 📞 [Traefik](https://traefik.io) 作为反向代理/负载均衡器。
- 🚢 使用Docker Compose的部署说明，包括如何设置前端Traefik代理以处理自动HTTPS证书。
- 🏭 基于GitHub Actions的CI（持续集成）和CD（持续部署）。

### 登录界面

[![登录界面](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 管理员仪表盘

[![管理员仪表盘](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 创建用户界面

[![创建用户](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 项目列表界面

[![项目列表](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 用户设置界面

[![用户设置](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 深色模式界面

[![深色模式](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 交互式API文档

[![API文档](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

### 配置

您可以在`.env`文件中更新配置以自定义您的设置。

在部署之前，请确保更改至少以下值：

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `MONGO_PASSWORD`

您可以（并且应该）将这些作为环境变量从密钥传递。

阅读[deployment.md](./deployment.md)文档了解更多详情。

### 生成密钥

`.env`文件中的某些环境变量默认值为`changethis`。

您需要将它们更改为密钥，要生成安全密钥，可以运行以下命令：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制内容并将其用作密码/密钥。再次运行该命令生成另一个安全密钥。

## 后端开发

后端文档：[backend/README.md](./backend/README.md)。

## 前端开发

前端文档：[frontend/README.md](./frontend/README.md)。

## 部署

部署文档：[deployment.md](./deployment.md)。

这包括使用Docker Compose、自定义本地域名、`.env`配置等。

## 许可证

AideX项目基于MIT许可证的条款授权。
