# log-viewer

在浏览器中查看本地 `logs/` 目录下的日志文件（可用 `LOG_DIR` 指向其它目录，模拟远端落盘日志）。

## 产品功能（当前版本）

| 能力 | 说明 |
|------|------|
| **单进程 Web 查看** | 同一进程提供 REST API 与前端静态页，本地一条命令启动，无需前端构建工具。 |
| **日志目录可配置** | 默认读取仓库内 `logs/`；可通过 `LOG_DIR` 指向任意目录，便于对接「模拟远端落盘」或其它路径。 |
| **文件列表** | 递归列出日志目录下文件（忽略 `.gitkeep`），展示相对路径、大小、修改时间。 |
| **内容查看** | 点击文件在页面右侧展示文本；支持 **末尾 N 行（tail）** 或 **offset + limit 分页**（基于单次读入并解码后的行）。 |
| **大文件保护** | 通过 `LOG_MAX_READ_BYTES` 限制单次读取字节数，避免超大文件占满内存；超长时仅处理尾部一段并标记截断。 |
| **编码** | `LOG_ENCODING` 可设为 `utf-8`、`gbk` 等，适配不同来源日志。 |
| **路径安全** | 后端校验路径必须落在 `LOG_DIR` 内，防止路径穿越。 |
| **健康检查** | `GET /api/health` 供部署或探活使用。 |

## 目录结构

```text
log-viewer/
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── main.py           # FastAPI、挂载 frontend、注册路由
│   ├── settings.py       # LOG_DIR、编码、读取上限
│   └── routes_logs.py    # /api/files、/api/logs/...
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
└── logs/                 # 默认日志目录（放入 .log 等文本文件）
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器打开：<http://127.0.0.1:8000/>  
左侧列出 `logs/` 下文件，点击后在右侧查看；支持末尾行数（tail）或填写 offset/limit 分页（仅对已读入字节范围内解码后的行生效）。

## 环境变量

| 变量 | 说明 |
|------|------|
| `LOG_DIR` | 日志根目录；不设置则使用仓库内 `logs/` |
| `LOG_MAX_READ_BYTES` | 单次最多读取字节数，默认 `2000000` |
| `LOG_ENCODING` | 解码编码，如 `utf-8`、`gbk`，默认 `utf-8` |

示例见 [.env.example](.env.example)。

## API

- `GET /api/files`：文件列表（相对路径、大小、mtime）
- `GET /api/logs/{path}?tail=N`：末尾 N 行（默认 500）
- `GET /api/logs/{path}?offset=O&limit=L`：分页行
- `GET /api/health`：健康检查
