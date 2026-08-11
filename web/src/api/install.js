import request, { createRequestWithTimeout } from '@/utils/request'

// 安装相关接口使用更长超时（创建数据库、建表等耗时操作）
const longRequest = createRequestWithTimeout(120000)
const dbTestRequest = createRequestWithTimeout(60000)

// 获取安装状态
export function getInstallStatus() {
  return request.get('/v1/install/status')
}

// 测试数据库连接（60秒超时：含创建数据库操作）
export function testDatabaseConnection(data) {
  return dbTestRequest.post('/v1/install/test-database', data)
}

// 执行安装（120秒超时：含建表、创建管理员等完整流程）
export function executeInstallation(data) {
  return longRequest.post('/v1/install/execute', data)
}

// 重置安装状态
export function resetInstallation() {
  return request.post('/v1/install/reset')
}
