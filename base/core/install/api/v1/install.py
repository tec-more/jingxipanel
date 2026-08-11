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

router = APIRouter(prefix="/v1/install", tags=["系统安装"])


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
                "app_debug": request.server.app_debug
            }
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "系统安装成功",
                "data": {
                    "admin_username": request.admin.username,
                    "admin_email": request.admin.email
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
