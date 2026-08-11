from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from base.core.install.schemas.install import (
    InstallRequest,
    InstallStatusResponse,
    TestConnectionRequest,
    TestConnectionResponse
)
from base.core.install.services.install_service import InstallService
from base.common.response import success_response
from base.common.setting import settings
import os
import sys
import platform
import subprocess

router = APIRouter(prefix="/v1/install", tags=["系统安装"])


def _trigger_restart(delay_seconds: int = 3):
    """
    触发应用自动重启（跨平台，兼容开发模式）。

    创建一个 detached 子进程，延迟指定秒数后终止当前进程并启动新进程。
    支持 Windows / Linux / macOS，自动处理 uvicorn reload 父子进程。

    进程关系说明：
      - 生产模式（无 reload）：当前进程 = 实际服务进程，直接 kill 当前 PID
      - 开发模式（有 reload）：当前进程 = worker 子进程，父进程 = uvicorn reloader
        只 kill worker 会被父进程重新 fork，所以要 kill 父进程（以及其下的整个进程树）
    """
    python_executable = sys.executable
    base_dir = str(settings.base_path)
    script_path = os.path.join(base_dir, "run.py")
    app_port = str(getattr(settings, "app_port", 9998))

    current_pid = os.getpid()
    try:
        parent_pid = os.getppid()
    except AttributeError:
        parent_pid = None

    # 判断是否在 uvicorn reload 模式下（当前进程是 worker 子进程）
    is_reload_worker = _is_uvicorn_reload_worker(parent_pid)

    if is_reload_worker and parent_pid:
        # 开发模式：终止 uvicorn reloader 父进程（会连带杀掉 worker）
        target_pid = parent_pid
        is_dev_mode = True
    else:
        # 生产模式：终止当前进程
        target_pid = current_pid
        is_dev_mode = False

    system = platform.system()

    if system == "Windows":
        _restart_windows(
            base_dir, script_path, python_executable,
            current_pid, target_pid, delay_seconds, is_dev_mode, app_port
        )
    else:
        _restart_unix(
            base_dir, script_path, python_executable,
            current_pid, target_pid, delay_seconds, is_dev_mode, app_port
        )


def _is_uvicorn_reload_worker(parent_pid) -> bool:
    """
    判断当前进程是否是 uvicorn reload 模式下的 worker 子进程。
    依据：父进程的命令行包含 "uvicorn" 或 run.py 启动脚本（即父进程是 reloader）。
    """
    if not parent_pid:
        return False
    system = platform.system()
    try:
        if system == "Windows":
            # Windows: 使用 wmic 查询父进程命令行
            result = subprocess.run(
                ["wmic", "process", "where", f"ProcessId={parent_pid}", "get", "CommandLine", "/value"],
                capture_output=True, text=True, timeout=5
            )
            line = result.stdout.strip()
            return ("uvicorn" in line.lower()) or ("run.py" in line)
        else:
            # Linux / macOS: 使用 ps -p PID -o args=
            result = subprocess.run(
                ["ps", "-p", str(parent_pid), "-o", "args="],
                capture_output=True, text=True, timeout=5
            )
            line = result.stdout.strip()
            return ("uvicorn" in line.lower()) or ("run.py" in line)
    except Exception:
        # 失败时安全回退：按生产模式处理（只 kill 当前 PID）
        return False


def _restart_windows(base_dir, script_path, python_executable, current_pid, target_pid, delay, is_dev, app_port):
    """Windows 平台重启脚本"""
    dev_env = "set UVICORN_RELOAD=true\r\n" if is_dev else ""
    # 当 target_pid != current_pid（即 dev 模式）时，先 kill 父进程，再确保当前进程也被 kill
    if target_pid != current_pid:
        kill_cmds = f"""echo [重启脚本] 正在终止 uvicorn reloader 父进程 PID={target_pid}（含子进程）...
taskkill /PID {target_pid} /F /T >nul 2>&1
echo [重启脚本] 正在兜底终止 worker 进程 PID={current_pid}...
taskkill /PID {current_pid} /F /T >nul 2>&1
"""
    else:
        kill_cmds = f"""echo [重启脚本] 正在终止服务进程 PID={target_pid}...
taskkill /PID {target_pid} /F /T >nul 2>&1
"""

    bat_content = f"""@echo off
chcp 65001 >nul 2>&1
echo [重启脚本] 等待 {delay} 秒...
timeout /t {delay} /nobreak >nul
{kill_cmds}echo [重启脚本] 等待端口 {app_port} 释放...
:wait_port
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":{app_port} " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 goto wait_port
echo [重启脚本] 端口已释放，正在启动新进程...
cd /d "{base_dir}"
set UVICORN_PORT={app_port}
{dev_env}"{python_executable}" "{script_path}"
"""
    bat_path = os.path.join(base_dir, "_restart.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)

    subprocess.Popen(
        ['cmd', '/c', bat_path],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
        close_fds=True,
        cwd=base_dir
    )


def _restart_unix(base_dir, script_path, python_executable, current_pid, target_pid, delay, is_dev, app_port):
    """Linux / macOS 平台重启脚本"""
    dev_env = "export UVICORN_RELOAD=true\n" if is_dev else ""

    if target_pid != current_pid:
        # dev 模式：先 kill 父进程（uvicorn reloader）进程组，再兜底 kill 当前进程
        kill_cmds = f"""echo "[重启脚本] 正在终止 uvicorn reloader 父进程 PID={target_pid}（含子进程）..."
# 终止整个进程组
pkill -TERM -P {target_pid} 2>/dev/null
kill -TERM {target_pid} 2>/dev/null
sleep 2
# 强制清理残余
pkill -9 -P {target_pid} 2>/dev/null
kill -9 {target_pid} 2>/dev/null
echo "[重启脚本] 正在兜底终止 worker 进程 PID={current_pid}..."
kill -9 {current_pid} 2>/dev/null
"""
    else:
        # 生产模式：终止当前进程及其子进程
        kill_cmds = f"""echo "[重启脚本] 正在终止服务进程 PID={target_pid}..."
pkill -TERM -P {target_pid} 2>/dev/null
kill -TERM {target_pid} 2>/dev/null
sleep 2
pkill -9 -P {target_pid} 2>/dev/null
kill -9 {target_pid} 2>/dev/null
"""

    sh_content = f"""#!/bin/bash
echo "[重启脚本] 等待 {delay} 秒..."
sleep {delay}
{kill_cmds}echo "[重启脚本] 等待端口 {app_port} 释放..."
while lsof -i :{app_port} -t > /dev/null 2>&1; do
    sleep 1
done
# 如果 lsof 不可用，用额外等待替代
sleep 2
echo "[重启脚本] 端口已释放，正在启动新进程..."
cd "{base_dir}"
export UVICORN_PORT={app_port}
{dev_env}exec "{python_executable}" "{script_path}"
"""
    sh_path = os.path.join(base_dir, "_restart.sh")
    with open(sh_path, 'w', encoding='utf-8') as f:
        f.write(sh_content)
    os.chmod(sh_path, 0o755)

    subprocess.Popen(
        ['bash', sh_path],
        start_new_session=True,
        cwd=base_dir
    )


@router.get("/env-check", summary="环境检测")
async def env_check():
    """检测运行环境，返回操作系统、Python版本、文件权限等信息"""
    import platform
    import sys
    from pathlib import Path
    from base.common.setting import settings

    # 操作系统检测
    os_name = platform.system()
    os_version = platform.version()
    if os_name == "Windows":
        os_display = f"Windows {os_version.split('.')[0]}"
    elif os_name == "Linux":
        os_display = f"Linux {platform.release()}"
    else:
        os_display = f"{os_name} {os_version}"

    # Python版本检测
    python_version = sys.version.split()[0]
    python_ok = sys.version_info >= (3, 8)

    # 文件写入权限检测
    checks = []
    base_path = Path(settings.base_path) if hasattr(settings, 'base_path') else Path.cwd()

    # 检测 config.conf 写入权限
    config_path = base_path / "config.conf"
    config_writable = False
    config_status = "warning"
    config_desc = "配置文件写入检测"
    try:
        test_file = base_path / ".write_test_config"
        test_file.touch()
        test_file.unlink()
        config_writable = True
        config_status = "success"
        config_desc = "config.conf 可写"
    except Exception:
        config_status = "error"
        config_desc = "config.conf 不可写"

    checks.append({
        "name": "配置文件写入权限",
        "value": config_status == "success" and "可写" or "不可写",
        "status": config_status,
        "desc": config_desc
    })

    # 检测 storage 目录写入权限
    storage_path = base_path / "storage"
    storage_writable = False
    storage_status = "warning"
    storage_desc = "存储目录检测"
    try:
        storage_path.mkdir(exist_ok=True)
        test_file = storage_path / ".write_test_storage"
        test_file.touch()
        test_file.unlink()
        storage_writable = True
        storage_status = "success"
        storage_desc = "storage 目录可写"
    except Exception:
        storage_status = "error"
        storage_desc = "storage 目录不可写"

    checks.append({
        "name": "存储目录写入权限",
        "value": storage_status == "success" and "可写" or "不可写",
        "status": storage_status,
        "desc": storage_desc
    })

    # 检测 logs 目录
    logs_path = base_path / "logs"
    logs_status = "warning"
    logs_desc = "日志目录检测"
    try:
        logs_path.mkdir(exist_ok=True)
        test_file = logs_path / ".write_test_logs"
        test_file.touch()
        test_file.unlink()
        logs_status = "success"
        logs_desc = "logs 目录可写"
    except Exception:
        logs_status = "error"
        logs_desc = "logs 目录不可写"

    checks.append({
        "name": "日志目录写入权限",
        "value": logs_status == "success" and "可写" or "不可写",
        "status": logs_status,
        "desc": logs_desc
    })

    # 检测数据库端口是否可用（仅检测端口是否空闲，不检测数据库本身）
    db_port = settings.db_port if hasattr(settings, 'db_port') else 15432
    port_available = True
    port_status = "warning"
    port_desc = f"数据库端口 {db_port} 待配置后检测"
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', db_port))
        if result == 0:
            port_available = True
            port_status = "success"
            port_desc = f"端口 {db_port} 已被占用（数据库可能已在运行）"
        else:
            port_available = True
            port_status = "warning"
            port_desc = f"端口 {db_port} 空闲（请在下一步配置数据库连接）"
        sock.close()
    except Exception:
        port_status = "warning"
        port_desc = f"端口 {db_port} 状态未知"

    checks.append({
        "name": "数据库端口",
        "value": f"{db_port}",
        "status": port_status,
        "desc": port_desc
    })

    # 汇总
    all_ok = all(c["status"] != "error" for c in checks)
    has_warning = any(c["status"] == "warning" for c in checks)

    return success_response({
        "os": {
            "name": os_name,
            "version": os_version,
            "display": os_display,
            "status": "success",
            "desc": "支持的操作系统"
        },
        "python": {
            "version": python_version,
            "status": "success" if python_ok else "error",
            "desc": "当前版本满足要求" if python_ok else "Python 版本过低，需要 3.8+"
        },
        "checks": checks,
        "overall_status": "success" if all_ok else ("warning" if has_warning else "error"),
        "message": "环境检测通过" if all_ok else ("部分检测项警告" if has_warning else "环境检测失败")
    })


@router.get("/status", summary="获取安装状态")
async def get_install_status():
    """获取系统安装状态"""
    installed = InstallService.is_installed()
    
    return success_response({
        "installed": installed,
        "current_step": 4 if installed else 0,
        "message": "系统已安装" if installed else "系统未安装，需要执行安装"
    })


@router.post("/test-database", response_model=TestConnectionResponse, summary="测试数据库连接")
async def test_database_connection(request: TestConnectionRequest):
    """测试数据库连接"""
    db = request.database
    
    success, message, response_time = await InstallService.test_database_connection(
        db_host=db.db_host,
        db_port=db.db_port,
        db_name=db.db_name,
        db_user=db.db_user,
        db_password=db.db_password,
        charset=db.charset,
        timeout=5,
        auto_create_db=db.auto_create_db
    )
    
    return TestConnectionResponse(
        success=success,
        message=message,
        response_time_ms=response_time
    )


@router.post("/execute", summary="执行安装")
async def execute_installation(request: InstallRequest):
    """执行系统安装"""
    if InstallService.is_installed():
        raise HTTPException(
            status_code=400,
            detail="系统已安装，如需重新安装请先清除安装标记"
        )
    
    # 先测试数据库连接（传入 auto_create_db 选项）
    db = request.database
    success, message, _ = await InstallService.test_database_connection(
        db_host=db.db_host,
        db_port=db.db_port,
        db_name=db.db_name,
        db_user=db.db_user,
        db_password=db.db_password,
        charset=db.charset,
        auto_create_db=db.auto_create_db
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"数据库连接失败：{message}"
        )
    
    # 执行安装
    try:
        await InstallService.execute_installation(
            db_config={
                "db_host": db.db_host,
                "db_port": db.db_port,
                "db_name": db.db_name,
                "db_user": db.db_user,
                "db_password": db.db_password,
                "charset": db.charset,
                "minsize": db.minsize,
                "maxsize": db.maxsize,
                "timeout": db.timeout,
                "command_timeout": db.command_timeout,
                "auto_create_db": db.auto_create_db
            },
            admin_config={
                "username": request.admin.username,
                "password": request.admin.password,
                "email": request.admin.email,
                "alias": request.admin.alias
            },
            server_config={
                "app_port": request.server.app_port,
                "app_debug": request.server.app_debug,
                "frontend_name": request.server.frontend_name,
                "backend_name": request.server.backend_name
            }
        )

        # 安装成功后触发自动重启（延迟3秒，确保响应已发送）
        _trigger_restart(delay_seconds=3)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "系统安装成功，正在自动重启...",
                "data": {
                    "admin_username": request.admin.username,
                    "admin_email": request.admin.email,
                    "need_restart": True
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"安装失败：{str(e)}"
        )


@router.post("/reset", summary="重置安装状态（谨慎使用）")
async def reset_installation():
    """重置安装状态，允许重新安装"""
    InstallService.remove_install_marker()
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "安装标记已移除，可以重新执行安装"
        }
    )
