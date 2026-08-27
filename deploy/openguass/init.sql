-- ============================================
-- openGauss 初始化脚本
-- 功能：设置 omm 密码、创建 admin 用户并赋予超级权限
-- 适用：jingxipanel 项目
-- ============================================

-- 1. 设置 omm 用户密码
-- 注意：如果 omm 用户不存在，该语句会报错，可忽略
ALTER USER omm IDENTIFIED BY 'Admin@123456';

-- 2. 创建 admin 用户（密码与 config.conf 中 db_password 一致）
CREATE USER admin PASSWORD 'Admin@123';

-- 3. 赋予 admin 系统管理员（超级用户）权限
--    包含：创建数据库、创建用户、删除、查询、复制等所有权限
ALTER USER admin SYSADMIN;

-- 4. 赋予 admin 所有数据库的操作权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO admin;

-- 5. 设置 admin 默认权限（针对未来新建的表）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO admin;

-- 验证结果
\du
