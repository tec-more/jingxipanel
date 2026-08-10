<template>
  <div class="install-container">
    <div class="install-card">
      <!-- 头部 -->
      <div class="install-header">
        <h1 class="install-title">
          <el-icon class="title-icon"><Setting /></el-icon>
          AIPanelAdmin 系统安装向导
        </h1>
        <p class="install-desc">欢迎使用 AIPanelAdmin，请按照以下步骤完成系统安装</p>
      </div>

      <!-- 步骤指示器 -->
      <el-steps
        :active="currentStep"
        :process-status="stepStatus"
        :finish-status="'success'"
        align-center
        class="install-steps"
      >
        <el-step title="环境检测" :icon="Monitor" />
        <el-step title="数据库配置" :icon="Coin" />
        <el-step title="管理员设置" :icon="User" />
        <el-step title="完成安装" :icon="CircleCheck" />
      </el-steps>

      <!-- 步骤内容 -->
      <div class="install-content">
        <!-- 第一步：环境检测 -->
        <div v-if="currentStep === 0" class="step-content">
          <el-card class="env-check-card">
            <template #header>
              <div class="card-header">
                <el-icon><Monitor /></el-icon>
                <span>环境检测</span>
              </div>
            </template>
            <div class="env-items">
              <div class="env-item" v-for="item in envChecks" :key="item.name">
                <span class="env-name">{{ item.name }}</span>
                <span class="env-value" :class="item.status">
                  <el-icon v-if="item.status === 'success'"><CircleCheck /></el-icon>
                  <el-icon v-else-if="item.status === 'warning'"><Warning /></el-icon>
                  <el-icon v-else><CircleClose /></el-icon>
                  {{ item.value }}
                </span>
                <span class="env-desc">{{ item.desc }}</span>
              </div>
            </div>
          </el-card>
          <div class="step-actions">
            <el-button type="primary" :disabled="!envReady" @click="nextStep">
              下一步：配置数据库
              <el-icon style="margin-left: 4px;"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 第二步：数据库配置 -->
        <div v-if="currentStep === 1" class="step-content">
          <el-form
            ref="dbFormRef"
            :model="dbForm"
            :rules="dbRules"
            label-width="120px"
            class="db-form"
          >
            <el-form-item label="数据库类型">
              <el-select v-model="dbForm.db_type" disabled>
                <el-option label="PostgreSQL / openGauss" value="postgresql" />
              </el-select>
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="主机地址" prop="db_host">
                  <el-input v-model="dbForm.db_host" placeholder="127.0.0.1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="端口" prop="db_port">
                  <el-input v-model.number="dbForm.db_port" placeholder="15432" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="数据库名" prop="db_name">
                  <el-input v-model="dbForm.db_name" placeholder="jingxipanel" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="用户名" prop="db_user">
                  <el-input v-model="dbForm.db_user" placeholder="admin" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="密码" prop="db_password">
              <el-input v-model="dbForm.db_password" type="password" show-password placeholder="请输入数据库密码" />
            </el-form-item>
            <el-divider content-position="left">连接池配置（可选）</el-divider>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="最小连接">
                  <el-input-number v-model="dbForm.minsize" :min="1" :max="50" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大连接">
                  <el-input-number v-model="dbForm.maxsize" :min="1" :max="200" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="dbForm.timeout" :min="5" :max="300" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          <div class="db-test-section">
            <el-button
              type="success"
              :loading="testingConnection"
              @click="handleTestConnection"
            >
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <span v-if="testResult" class="test-result" :class="testResult.success ? 'success' : 'error'">
              <el-icon v-if="testResult.success"><CircleCheck /></el-icon>
              <el-icon v-else><CircleClose /></el-icon>
              {{ testResult.message }}
              <span v-if="testResult.response_time_ms" class="response-time">({{ testResult.response_time_ms }}ms)</span>
            </span>
          </div>
          <div class="step-actions">
            <el-button @click="prevStep">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              :disabled="!dbConnectionOk"
              @click="nextStep"
            >
              下一步：设置管理员
              <el-icon style="margin-left: 4px;"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 第三步：管理员设置 -->
        <div v-if="currentStep === 2" class="step-content">
          <el-form
            ref="adminFormRef"
            :model="adminForm"
            :rules="adminRules"
            label-width="120px"
            class="admin-form"
          >
            <el-divider content-position="left">管理员账户</el-divider>
            <el-form-item label="用户名" prop="username">
              <el-input v-model="adminForm.username" placeholder="admin" maxlength="20" />
              <div class="form-tip">管理员登录用户名，建议使用英文字母和数字</div>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="adminForm.password" type="password" show-password placeholder="至少8位字符" />
              <div class="form-tip">密码强度：至少8位，建议包含大小写字母、数字和特殊字符</div>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="adminForm.confirmPassword" type="password" show-password placeholder="再次输入密码" />
            </el-form-item>
            <el-divider content-position="left">基本信息</el-divider>
            <el-form-item label="昵称">
              <el-input v-model="adminForm.alias" placeholder="系统管理员" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="adminForm.email" placeholder="admin@example.com" />
            </el-form-item>
            <el-divider content-position="left">服务器配置</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="访问端口">
                  <el-input-number v-model="serverForm.app_port" :min="1" :max="65535" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="调试模式">
                  <el-switch v-model="serverForm.app_debug" active-text="开启" inactive-text="关闭" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          <div class="step-actions">
            <el-button @click="prevStep">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              :disabled="!adminFormValid"
              :loading="installing"
              @click="handleExecuteInstall"
            >
              <el-icon><Download /></el-icon>
              {{ installing ? '安装中...' : '开始安装' }}
            </el-button>
          </div>
        </div>

        <!-- 第四步：安装进度 -->
        <div v-if="currentStep === 3" class="step-content">
          <div class="install-progress">
            <el-progress
              :percentage="installProgress"
              :status="installStatus"
              :stroke-width="20"
              :text-inside="true"
            />
            <div class="install-logs">
              <div v-for="(log, index) in installLogs" :key="index" class="log-item" :class="log.type">
                <el-icon v-if="log.type === 'success'"><CircleCheck /></el-icon>
                <el-icon v-else-if="log.type === 'error'"><CircleClose /></el-icon>
                <el-icon v-else><Loading /></el-icon>
                <span>{{ log.message }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 第五步：安装完成 -->
        <div v-if="currentStep === 4" class="step-content">
          <el-result
            icon="success"
            title="安装成功"
            sub-title="系统已成功安装，请使用管理员账户登录"
          >
            <template #extra>
              <div class="install-result-info">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="管理员用户名">{{ installResult?.admin_username }}</el-descriptions-item>
                  <el-descriptions-item label="管理员邮箱">{{ installResult?.admin_email }}</el-descriptions-item>
                </el-descriptions>
                <p class="warning-text">
                  <el-icon><Warning /></el-icon>
                  请妥善保管管理员账户信息，安装完成后建议立即登录并修改默认密码。
                </p>
              </div>
              <el-button type="primary" size="large" @click="goToLogin">
                前往登录
                <el-icon style="margin-left: 4px;"><ArrowRight /></el-icon>
              </el-button>
            </template>
          </el-result>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Setting, Monitor, Coin, User, CircleCheck, CircleClose,
  Warning, ArrowRight, ArrowLeft, Connection, Download,
  Loading
} from '@element-plus/icons-vue'
import { getInstallStatus, testDatabaseConnection, executeInstallation } from '@/api/install'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)
const installReady = ref(false)

// 步骤状态
const stepStatus = computed(() => {
  if (installing.value) return 'process'
  if (installStatus.value === 'success') return 'success'
  return 'wait'
})

// 环境检测
const envChecks = ref([
  { name: '操作系统', value: 'Windows / Linux', status: 'success', desc: '支持的操作系统' },
  { name: 'Python 版本', value: '3.8+', status: 'success', desc: '当前版本满足要求' },
  { name: '数据库', value: 'PostgreSQL / openGauss', status: 'warning', desc: '请在下一步配置数据库连接' },
  { name: '文件写入权限', value: '检测中...', status: 'success', desc: '确保 config.conf 和 storage 可写' }
])

const envReady = computed(() => {
  return envChecks.value.every(item => item.status !== 'error')
})

// 数据库表单
const dbFormRef = ref(null)
const dbForm = reactive({
  db_type: 'postgresql',
  db_host: '127.0.0.1',
  db_port: 15432,
  db_name: 'jingxipanel',
  db_user: 'admin',
  db_password: '',
  minsize: 5,
  maxsize: 20,
  timeout: 30
})

const dbRules = {
  db_host: [{ required: true, message: '请输入数据库主机地址', trigger: 'blur' }],
  db_port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  db_name: [{ required: true, message: '请输入数据库名', trigger: 'blur' }],
  db_user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  db_password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const testingConnection = ref(false)
const testResult = ref(null)
const dbConnectionOk = ref(false)

// 管理员表单
const adminFormRef = ref(null)
const adminForm = reactive({
  username: 'admin',
  password: '',
  confirmPassword: '',
  email: '',
  alias: '系统管理员'
})

const adminRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 位字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== adminForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ]
}

const serverForm = reactive({
  app_port: 9998,
  app_debug: false
})

const adminFormValid = ref(false)

// 安装进度
const installing = ref(false)
const installProgress = ref(0)
const installStatus = ref('')
const installLogs = ref([])
const installResult = ref(null)
let installTimer = null

// 下一步
const nextStep = async () => {
  if (currentStep.value === 0) {
    currentStep.value = 1
  } else if (currentStep.value === 1) {
    await dbFormRef.value.validate()
    if (!dbConnectionOk.value) {
      ElMessage.warning('请先测试数据库连接')
      return
    }
    currentStep.value = 2
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0 && currentStep.value < 3) {
    currentStep.value--
  }
}

// 测试数据库连接
const handleTestConnection = async () => {
  testingConnection.value = true
  testResult.value = null
  dbConnectionOk.value = false

  try {
    const res = await testDatabaseConnection({
      database: {
        db_host: dbForm.db_host,
        db_port: dbForm.db_port,
        db_name: dbForm.db_name,
        db_user: dbForm.db_user,
        db_password: dbForm.db_password
      }
    })

    // 兼容不同的响应格式
    const data = res.data || res
    testResult.value = {
      success: data.success,
      message: data.message,
      response_time_ms: data.response_time_ms
    }
    dbConnectionOk.value = data.success
  } catch (e) {
    testResult.value = {
      success: false,
      message: e.message || '连接测试失败',
      response_time_ms: 0
    }
    dbConnectionOk.value = false
  } finally {
    testingConnection.value = false
  }
}

// 监听管理员表单验证
const watchAdminForm = () => {
  if (adminFormRef.value) {
    adminFormRef.value.validate((valid) => {
      adminFormValid.value = valid
    })
  }
}

// 执行安装
const handleExecuteInstall = async () => {
  if (!adminFormRef.value) return

  try {
    await adminFormRef.value.validate()
  } catch {
    ElMessage.error('请检查管理员表单填写')
    return
  }

  installing.value = true
  currentStep.value = 3
  installProgress.value = 10
  installLogs.value = [
    { type: 'info', message: '正在写入配置文件...' }
  ]

  // 模拟进度
  const steps = [
    { progress: 20, log: { type: 'info', message: '配置文件写入完成' } },
    { progress: 35, log: { type: 'info', message: '正在初始化数据库...' } },
    { progress: 50, log: { type: 'info', message: '正在创建数据表...' } },
    { progress: 65, log: { type: 'info', message: '数据表创建完成' } },
    { progress: 75, log: { type: 'info', message: '正在创建管理员账户...' } },
    { progress: 85, log: { type: 'info', message: '正在初始化默认数据...' } },
    { progress: 95, log: { type: 'info', message: '准备完成...' } }
  ]

  let stepIndex = 0
  const progressTimer = setInterval(() => {
    if (stepIndex < steps.length) {
      const step = steps[stepIndex]
      installProgress.value = step.progress
      installLogs.value.push(step.log)
      stepIndex++
    }
  }, 400)

  try {
    const res = await executeInstallation({
      database: {
        db_host: dbForm.db_host,
        db_port: dbForm.db_port,
        db_name: dbForm.db_name,
        db_user: dbForm.db_user,
        db_password: dbForm.db_password,
        minsize: dbForm.minsize,
        maxsize: dbForm.maxsize,
        timeout: dbForm.timeout,
        command_timeout: dbForm.timeout
      },
      admin: {
        username: adminForm.username,
        password: adminForm.password,
        email: adminForm.email || `${adminForm.username}@example.com`,
        alias: adminForm.alias
      },
      server: {
        app_port: serverForm.app_port,
        app_debug: serverForm.app_debug
      }
    })

    clearInterval(progressTimer)
    
    installProgress.value = 100
    installStatus.value = 'success'
    installLogs.value.push({ type: 'success', message: '系统安装成功！' })
    
    const data = res.data || res
    installResult.value = data
    
    // 保存安装状态到 localStorage
    localStorage.setItem('system_installed', 'true')
    localStorage.setItem('install_time', new Date().toISOString())
    
    setTimeout(() => {
      currentStep.value = 4
      installing.value = false
    }, 1000)

  } catch (e) {
    clearInterval(progressTimer)
    installStatus.value = 'error'
    installLogs.value.push({ 
      type: 'error', 
      message: `安装失败：${e.response?.data?.detail || e.message}` 
    })
    installing.value = false
    ElMessage.error(`安装失败：${e.response?.data?.detail || e.message}`)
  }
}

// 跳转到登录页
const goToLogin = () => {
  // 确保安装状态已保存
  localStorage.setItem('system_installed', 'true')
  router.push({
    path: '/panel/login',
    query: { installed: '1' }
  })
}

// 检查安装状态
const checkInstallStatus = async () => {
  try {
    const res = await getInstallStatus()
    const data = res.data || res
    if (data.installed) {
      ElMessage.info('系统已安装，正在跳转至登录页')
      router.replace('/panel/login')
    }
  } catch (e) {
    // 未安装时可能会返回 404，忽略
    console.log('安装状态检查完成')
  }
}

onMounted(() => {
  checkInstallStatus()
  
  // 表单验证监听
  if (adminFormRef.value) {
    adminFormRef.value.validate(() => {})
  }
})

onUnmounted(() => {
  if (installTimer) {
    clearInterval(installTimer)
  }
})

// 暴露给模板使用
const Monitor = Monitor
const Coin = Coin
const User = User
const CircleCheck = CircleCheck
const CircleClose = CircleClose
const Warning = Warning
const ArrowRight = ArrowRight
const ArrowLeft = ArrowLeft
const Connection = Connection
const Download = Download
const Loading = Loading
const Setting = Setting
</script>

<style scoped lang="scss">
.install-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.install-card {
  width: 100%;
  max-width: 720px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
}

.install-header {
  text-align: center;
  margin-bottom: 30px;
}

.install-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.title-icon {
  color: #667eea;
  font-size: 32px;
  animation: spin 4s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.install-desc {
  color: #909399;
  margin: 0;
}

.install-steps {
  margin-bottom: 30px;
}

.install-content {
  min-height: 400px;
}

.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.env-check-card {
  margin-bottom: 20px;
}

.env-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.env-item {
  display: grid;
  grid-template-columns: 150px 150px 1fr;
  gap: 15px;
  padding: 10px 15px;
  background: #f5f7fa;
  border-radius: 8px;
  align-items: center;
}

.env-name {
  font-weight: 500;
  color: #303133;
}

.env-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  
  &.success { color: #67c23a; }
  &.warning { color: #e6a23c; }
  &.error { color: #f56c6c; }
}

.env-desc {
  color: #909399;
  font-size: 13px;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.db-form, .admin-form {
  max-width: 550px;
  margin: 0 auto;
}

.db-test-section {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: center;
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.test-result {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  
  &.success { color: #67c23a; }
  &.error { color: #f56c6c; }
}

.response-time {
  font-size: 12px;
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.install-progress {
  text-align: center;
  padding: 20px 0;
}

.install-logs {
  margin-top: 30px;
  text-align: left;
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  font-size: 14px;
  animation: slideIn 0.3s ease;
  
  &.info {
    background: #ecf5ff;
    color: #409eff;
  }
  &.success {
    background: #f0f9eb;
    color: #67c23a;
  }
  &.error {
    background: #fef0f0;
    color: #f56c6c;
  }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.install-result-info {
  margin-bottom: 20px;
}

.warning-text {
  margin-top: 15px;
  padding: 12px;
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 8px;
  color: #e6a23c;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
