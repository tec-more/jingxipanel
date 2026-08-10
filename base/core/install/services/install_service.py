import os
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class InstallService:
    """安装服务"""
    
    INSTALL_MARKER_FILE = ".installed"
    
    @classmethod
    def is_installed(cls) -> bool:
        """检查系统是否已安装"""
        marker_path = cls._get_marker_path()
        return marker_path.exists()
    
    @classmethod
    def mark_as_installed(cls) -> None:
        """标记为已安装"""
        marker_path = cls._get_marker_path()
        marker_path.touch()
    
    @classmethod
    def remove_install_marker(cls) -> None:
        """移除安装标记（用于重新安装）"""
        marker_path = cls._get_marker_path()
        if marker_path.exists():
            marker_path.unlink()
    
    @classmethod
    def _get_marker_path(cls) -> Path:
        """获取标记文件路径"""
        from base.common.setting import settings
        return Path(settings.base_path) / cls.INSTALL_MARKER_FILE
    
    @classmethod
    async def test_database_connection(
        cls,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        timeout: int = 5
    ) -> tuple[bool, str, int]:
        """测试数据库连接"""
        import asyncpg
        import time
        
        start_time = time.time()
        
        try:
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                timeout=timeout
            )
            await conn.execute("SELECT 1")
            await conn.close()
            
            response_time = int((time.time() - start_time) * 1000)
            return True, "数据库连接成功", response_time
            
        except asyncpg.exceptions.ConnectionDoesNotExistError:
            return False, f"数据库连接失败：主机 {db_host}:{db_port} 无法访问", 0
        except asyncpg.exceptions.InvalidPasswordError:
            return False, "数据库连接失败：用户名或密码错误", 0
        except asyncpg.exceptions.InvalidCatalogNameError:
            return False, f"数据库连接失败：数据库 {db_name} 不存在", 0
        except TimeoutError:
            return False, f"数据库连接超时：超过 {timeout} 秒", 0
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return False, f"数据库连接失败：{str(e)}", response_time
    
    @classmethod
    async def write_config(
        cls,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        minsize: int = 5,
        maxsize: int = 20,
        timeout: int = 30,
        command_timeout: int = 30,
        app_port: int = 9998,
        app_debug: bool = False
    ) -> None:
        """写入配置文件"""
        import configparser
        from base.common.setting import settings
        
        config_path = Path(settings.base_path) / "config.conf"
        config = configparser.ConfigParser()
        
        if config_path.exists():
            config.read(config_path, encoding="utf-8")
        
        if not config.has_section("db"):
            config.add_section("db")
        
        config.set("db", "db_host", db_host)
        config.set("db", "db_port", str(db_port))
        config.set("db", "db_name", db_name)
        config.set("db", "db_user", db_user)
        config.set("db", "db_password", db_password)
        config.set("db", "minsize", str(minsize))
        config.set("db", "maxsize", str(maxsize))
        config.set("db", "timeout", str(timeout))
        config.set("db", "command_timeout", str(command_timeout))
        
        if not config.has_section("app"):
            config.add_section("app")
        
        config.set("app", "debug", str(app_debug).lower())
        
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)
        
        # 更新内存中的设置
        settings.db_host = db_host
        settings.db_port = db_port
        settings.db_name = db_name
        settings.db_user = db_user
        settings.db_password = db_password
        settings.minsize = minsize
        settings.maxsize = maxsize
        settings.timeout = timeout
        settings.command_timeout = command_timeout
        settings.debug = app_debug
        
        # 更新 TORTOISE_ORM 配置
        from base.common.setting import TORTOISE_ORM
        TORTOISE_ORM["connections"]["postgres"]["credentials"].update({
            "host": db_host,
            "port": db_port,
            "user": db_user,
            "password": db_password,
            "database": db_name,
            "minsize": minsize,
            "maxsize": maxsize,
            "timeout": timeout,
            "command_timeout": command_timeout,
        })
        
        logger.info(f"配置已写入: {config_path}")
    
    @classmethod
    async def initialize_database(cls) -> None:
        """初始化数据库"""
        from base.common.database import init_data
        await init_data()
        logger.info("数据库初始化完成")
    
    @classmethod
    async def create_admin_user(
        cls,
        username: str,
        password: str,
        email: str,
        alias: str = "系统管理员"
    ) -> None:
        """创建管理员用户"""
        from base.core.users.models.users import User
        from base.common.security import get_password_hash
        
        existing_user = await User.filter(username=username).first()
        if existing_user:
            logger.warning(f"用户 {username} 已存在，更新密码")
            existing_user.password = get_password_hash(password)
            existing_user.email = email
            existing_user.alias = alias
            existing_user.is_superuser = True
            existing_user.is_active = True
            await existing_user.save()
        else:
            await User.create(
                username=username,
                password=get_password_hash(password),
                email=email,
                alias=alias,
                is_superuser=True,
                is_active=True
            )
            logger.info(f"管理员用户 {username} 创建成功")
    
    @classmethod
    async def execute_installation(
        cls,
        db_config: dict,
        admin_config: dict,
        server_config: dict
    ) -> None:
        """执行完整安装流程"""
        try:
            # Step 1: 写入配置
            await cls.write_config(
                db_host=db_config["db_host"],
                db_port=db_config["db_port"],
                db_name=db_config["db_name"],
                db_user=db_config["db_user"],
                db_password=db_config["db_password"],
                minsize=db_config.get("minsize", 5),
                maxsize=db_config.get("maxsize", 20),
                timeout=db_config.get("timeout", 30),
                command_timeout=db_config.get("command_timeout", 30),
                app_port=server_config.get("app_port", 9998),
                app_debug=server_config.get("app_debug", False)
            )
            
            # Step 2: 初始化数据库
            await cls.initialize_database()
            
            # Step 3: 创建管理员
            await cls.create_admin_user(
                username=admin_config["username"],
                password=admin_config["password"],
                email=admin_config["email"],
                alias=admin_config.get("alias", "系统管理员")
            )
            
            # Step 4: 标记为已安装
            cls.mark_as_installed()
            
            logger.info("安装流程执行完成")
            
        except Exception as e:
            logger.error(f"安装流程执行失败: {e}")
            raise
