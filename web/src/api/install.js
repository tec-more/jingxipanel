import request from '@/utils/request'

// 获取安装状态
export function getInstallStatus() {
  return request.get('/v1/install/status')
}

// 测试数据库连接
export function testDatabaseConnection(data) {
  return request.post('/v1/install/test-database', data)
}

// 执行安装
export function executeInstallation(data) {
  return request.post('/v1/install/execute', data)
}

// 重置安装状态
export function resetInstallation() {
  return request.post('/v1/install/reset')
}
