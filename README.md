# log-viewer

在浏览器中查看本地 `logs/` 目录下的日志文件（可用 `LOG_DIR` 指向其它目录，模拟远端落盘日志）。

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
