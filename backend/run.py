"""开发环境启动入口。

在 backend 目录下执行：
    .venv\\Scripts\\python.exe run.py

等价于：
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --port 8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],
    )
