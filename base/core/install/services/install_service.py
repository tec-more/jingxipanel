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
    async def _try_connect(
        cls,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        timeout: int = 5
    ) -> tuple[bool, str]:
        """尝试连接数据库，返回 (是否成功, 错误码)"""
        import asyncpg
        
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
            return True, ""
        except Exception as e:
            error_str = str(e).lower()
            error_type = type(e).__name__.lower()
            
            # 数据库不存在的判断
            is_db_not_exist = (
                "invalidcatalogname" in error_type or
                ("not exist" in error_str and "database" in error_str) or
                ("does not exist" in error_str and "database" in error_str) or
                (db_name.lower() in error_str and ("not exist" in error_str or "does not exist" in error_str))
            )
            
            if is_db_not_exist:
                return False, "database_not_exist"
            
            # 账户被锁定 (openGauss 特定)
            if "locked" in error_str:
                return False, "account_locked"
            
            # 连接被拒绝（主机/端口问题）
            is_connection_refused = (
                "connectiondoesnotexisterror" in error_type or
                "connection refused" in error_str or
                "could not connect" in error_str
            )
            if is_connection_refused:
                return False, "connection_refused"
            
            # 密码错误/认证失败 (openGauss: InvalidAuthorizationSpecificationError)
            is_auth_error = (
                "invalidpassworderror" in error_type or
                "invalidauthorizationspecificationerror" in error_type or
                "invalid password" in error_str or
                "authentication failed" in error_str or
                "password" in error_str and ("invalid" in error_str or "error" in error_str)
            )
            if is_auth_error:
                return False, "auth_failed"
            
            # 超时
            if "timeout" in error_str:
                return False, "timeout"
            
            return False, f"unknown:{type(e).__name__}"
    
    @classmethod
    async def _connect_template_db(
        cls,
        db_host: str,
        db_port: int,
        db_user: str,
        db_password: str,
        timeout: int = 5
    ) -> tuple:
        """连接到模板数据库，返回 (conn, template_db_name) 或 (None, None)"""
        import asyncpg
        
        for template_db in ["postgres", "template1"]:
            try:
                conn = await asyncpg.connect(
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    database=template_db,
                    timeout=timeout
                )
                return conn, template_db
            except Exception:
                continue
        
        return None, None
    
    @classmethod
    async def create_database(
        cls,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        charset: str = "UTF8",
        timeout: int = 10
    ) -> tuple[bool, str]:
        """创建数据库"""
        import asyncpg
        import re
        
        # 验证数据库名合法性（防止 SQL 注入）
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', db_name):
            return False, "数据库名不合法，只能包含字母、数字和下划线，且必须以字母或下划线开头"
        
        # 验证字符集
        valid_charsets = ['UTF8', 'LATIN1', 'GBK', 'GB18030', 'SQL_ASCII', 'UTF8MB4', 'GB18030']
        charset_upper = charset.upper()
        if charset_upper not in valid_charsets and charset_upper not in ['UTF8', 'UTF-8', 'UTF_8']:
            # 允许常见别名
            pass  # 宽松校验，让数据库自行处理
        
        # 连接到模板数据库
        conn, template_db = await cls._connect_template_db(
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            timeout=timeout
        )
        
        if conn is None:
            return False, "无法连接到模板数据库，请检查用户名密码及用户的 CREATE DATABASE 权限"
        
        try:
            # openGauss/PostgreSQL 创建数据库，指定字符集
            charset_val = charset_upper
            try:
                # 先尝试带 ENCODING 的版本（openGauss 兼容）
                await conn.execute(f'CREATE DATABASE "{db_name}" ENCODING = \'{charset_val}\'')
            except Exception as e:
                error_str = str(e).lower()
                # 如果 ENCODING 语法不兼容，尝试其他语法
                if "encoding" in error_str or "syntax" in error_str or "syntax error" in error_str:
                    try:
                        await conn.execute(f'CREATE DATABASE "{db_name}" WITH ENCODING = \'{charset_val}\'')
                    except Exception as e2:
                        # 最后尝试最简版本
                        if "encoding" in str(e2).lower() or "syntax" in str(e2).lower():
                            await conn.execute(f'CREATE DATABASE "{db_name}"')
                        else:
                            raise
                else:
                    raise
            
            logger.info(f"数据库 {db_name} 创建成功 (字符集: {charset_val})")
            return True, f"数据库 {db_name} 创建成功（字符集: {charset_val}）"
            
        except asyncpg.exceptions.DuplicateDatabaseError:
            return True, f"数据库 {db_name} 已存在"
        except asyncpg.exceptions.InsufficientPrivilegeError:
            return False, "创建数据库失败：权限不足，请检查用户是否有 CREATE DATABASE 权限"
        except Exception as e:
            return False, f"创建数据库失败：{str(e)}"
        finally:
            if conn:
                await conn.close()
    
    @classmethod
    async def test_database_connection(
        cls,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        charset: str = "UTF8",
        timeout: int = 5,
        auto_create_db: bool = False
    ) -> tuple[bool, str, int]:
        """测试数据库连接
        
        Args:
            auto_create_db: 如果数据库不存在且为 True，则自动创建
        """
        import time
        
        start_time = time.time()
        
        # Step 1: 直接尝试连接目标数据库
        ok, error_code = await cls._try_connect(
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            timeout=timeout
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        # 连接成功
        if ok:
            return True, "数据库连接成功", response_time
        
        # 根据错误码处理
        if error_code == "auth_failed":
            return False, "数据库连接失败：用户名或密码错误", 0
        
        if error_code == "account_locked":
            return False, "数据库连接失败：账户已被锁定，请使用 omm 管理员解锁或重置密码", 0
        
        if error_code == "connection_refused":
            return False, f"数据库连接失败：主机 {db_host}:{db_port} 无法访问", 0
        
        if error_code == "timeout":
            return False, f"数据库连接超时：超过 {timeout} 秒", 0
        
        # 数据库不存在
        if error_code == "database_not_exist":
            if auto_create_db:
                # Step 2: 尝试连接模板库创建数据库
                create_ok, create_msg = await cls.create_database(
                    db_host=db_host,
                    db_port=db_port,
                    db_name=db_name,
                    db_user=db_user,
                    db_password=db_password,
                    charset=charset
                )
                
                if not create_ok:
                    response_time = int((time.time() - start_time) * 1000)
                    return False, f"数据库 {db_name} 不存在，且自动创建失败：{create_msg}", response_time
                
                # Step 3: 创建成功，再次连接验证
                verify_ok, verify_error = await cls._try_connect(
                    db_host=db_host,
                    db_port=db_port,
                    db_name=db_name,
                    db_user=db_user,
                    db_password=db_password,
                    timeout=timeout
                )
                
                response_time = int((time.time() - start_time) * 1000)
                
                if verify_ok:
                    return True, f"数据库连接成功（已自动创建数据库 {db_name}）", response_time
                else:
                    return False, f"数据库创建成功但连接验证失败：{verify_error}", response_time
            else:
                response_time = int((time.time() - start_time) * 1000)
                return False, f"数据库 {db_name} 不存在，请勾选下方「自动创建数据库」复选框后重试", response_time
        
        # 其他未知错误
        if error_code.startswith("unknown:"):
            return False, f"数据库连接失败：{error_code[8:]}", response_time
        return False, f"数据库连接失败：{error_code}", response_time
    
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
        app_debug: bool = False,
        frontend_name: str = "",
        backend_name: str = ""
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
        config.set("app", "frontend_name", frontend_name)
        config.set("app", "backend_name", backend_name)
        
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
        settings.frontend_name = frontend_name
        settings.backend_name = backend_name
        
        # 更新 setting 模块级变量（TORTOISE_ORM 初始化时使用的是模块级变量）
        import base.common.setting as setting_module
        setting_module.db_host = db_host
        setting_module.db_port = db_port
        setting_module.db_name = db_name
        setting_module.db_user = db_user
        setting_module.db_password = db_password
        setting_module.minsize = minsize
        setting_module.maxsize = maxsize
        setting_module.timeout = timeout
        setting_module.command_timeout = command_timeout
        
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
            db_host = db_config["db_host"]
            db_port = db_config["db_port"]
            db_name = db_config["db_name"]
            db_user = db_config["db_user"]
            db_password = db_config["db_password"]
            db_charset = db_config.get("charset", "UTF8")
            auto_create_db = db_config.get("auto_create_db", True)
            
            # Step 0: 确保数据库存在（如果勾选了自动创建）
            if auto_create_db:
                # 尝试直接连接目标数据库
                ok, error_code = await cls._try_connect(
                    db_host=db_host,
                    db_port=db_port,
                    db_name=db_name,
                    db_user=db_user,
                    db_password=db_password,
                    timeout=5
                )
                
                if not ok and error_code == "database_not_exist":
                    # 数据库不存在，尝试创建
                    create_ok, create_msg = await cls.create_database(
                        db_host=db_host,
                        db_port=db_port,
                        db_name=db_name,
                        db_user=db_user,
                        db_password=db_password,
                        charset=db_charset
                    )
                    if not create_ok:
                        raise RuntimeError(f"数据库 {db_name} 不存在且自动创建失败：{create_msg}")
                    logger.info(f"安装流程：{create_msg}")
            
            # Step 1: 写入配置
            await cls.write_config(
                db_host=db_host,
                db_port=db_port,
                db_name=db_name,
                db_user=db_user,
                db_password=db_password,
                minsize=db_config.get("minsize", 5),
                maxsize=db_config.get("maxsize", 20),
                timeout=db_config.get("timeout", 30),
                command_timeout=db_config.get("command_timeout", 30),
                app_port=server_config.get("app_port", 9998),
                app_debug=server_config.get("app_debug", False),
                frontend_name=server_config.get("frontend_name", ""),
                backend_name=server_config.get("backend_name", "")
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
