<template>
  <div class="simulation-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="仿真编码">
          <el-input v-model="searchForm.sim_code" clearable />
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="searchForm.sim_name" clearable />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.sim_type" clearable style="width: 160px">
            <el-option label="状态预测" value="state_prediction" />
            <el-option label="故障预测" value="failure_forecast" />
            <el-option label="优化仿真" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable style="width: 120px">
            <el-option label="待执行" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="openAddDialog">新建仿真</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="sim_code" label="仿真编码" min-width="140" />
        <el-table-column prop="sim_name" label="名称" min-width="150" />
        <el-table-column prop="sim_type" label="类型" width="110">
          <template #default="{ row }">{{ typeMap[row.sim_type] || row.sim_type }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="160">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.progress || 0)" :status="row.status === 'failed' ? 'exception' : (row.status === 'completed' ? 'success' : '')" />
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetailDialog(row)">详情</el-button>
            <el-button v-if="row.status === 'running' || row.status === 'pending'" size="small" type="danger" @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建仿真任务" width="560px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="仿真编码" prop="sim_code">
          <el-input v-model="formData.sim_code" />
        </el-form-item>
        <el-form-item label="仿真名称" prop="sim_name">
          <el-input v-model="formData.sim_name" />
        </el-form-item>
        <el-form-item label="仿真类型" prop="sim_type">
          <el-select v-model="formData.sim_type" style="width: 100%">
            <el-option label="状态预测" value="state_prediction" />
            <el-option label="故障预测" value="failure_forecast" />
            <el-option label="优化仿真" value="optimization" />
          </el-select>
        </el-form-item>
        <el-form-item label="实体范围">
          <el-input v-model="entityCodesText" type="textarea" :rows="2" placeholder="实体编码列表，逗号分隔（留空则全部启用实体）" />
        </el-form-item>
        <el-form-item label="输入参数">
          <el-input v-model="inputParamsText" type="textarea" :rows="3" placeholder='JSON 格式，如 {"horizon_hours": 24}' />
        </el-form-item>
        <el-form-item label="创建人">
          <el-input v-model="formData.created_by" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSave">创建并启动</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="仿真结果详情" width="780px">
      <pre style="max-height: 500px; overflow: auto; background: #f5f7fa; padding: 12px; border-radius: 4px">{{ detailText }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSimulationList, createSimulation, cancelSimulation, getSimulationDetail } from '@/api/digitalTwin'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ sim_code: '', sim_name: '', sim_type: null, status: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const typeMap = { state_prediction: '状态预测', failure_forecast: '故障预测', optimization: '优化仿真' }
const statusMap = { pending: '待执行', running: '运行中', completed: '已完成', failed: '失败' }
const statusTypeMap = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const formData = reactive({
  sim_code: '',
  sim_name: '',
  sim_type: 'state_prediction',
  created_by: ''
})
const entityCodesText = ref('')
const inputParamsText = ref('')
const formRules = {
  sim_code: [{ required: true, message: '请输入仿真编码', trigger: 'blur' }],
  sim_name: [{ required: true, message: '请输入仿真名称', trigger: 'blur' }],
  sim_type: [{ required: true, message: '请选择仿真类型', trigger: 'change' }]
}

const detailDialogVisible = ref(false)
const detailText = ref('')

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getSimulationList({ page: pagination.page, page_size: pagination.pageSize, ...searchForm })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.sim_code = ''
  searchForm.sim_name = ''
  searchForm.sim_type = null
  searchForm.status = null
  handleSearch()
}

const openAddDialog = () => {
  formData.sim_code = ''
  formData.sim_name = ''
  formData.sim_type = 'state_prediction'
  formData.created_by = ''
  entityCodesText.value = ''
  inputParamsText.value = ''
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = { ...formData }
      // 构造 entity_scope
      const codes = entityCodesText.value.split(',').map(s => s.trim()).filter(Boolean)
      if (codes.length) {
        payload.entity_scope = { entity_codes: codes }
      }
      // 构造 input_params
      if (inputParamsText.value.trim()) {
        try {
          payload.input_params = JSON.parse(inputParamsText.value)
        } catch {
          ElMessage.warning('输入参数不是合法 JSON')
          submitLoading.value = false
          return
        }
      }
      await createSimulation(payload)
      ElMessage.success('仿真任务已创建并启动')
      dialogVisible.value = false
      fetchData()
    } catch (e) { console.error(e) } finally { submitLoading.value = false }
  })
}

const handleCancel = (row) => {
  ElMessageBox.confirm(`确认取消仿真 "${row.sim_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await cancelSimulation(row.id)
      ElMessage.success('已取消')
      fetchData()
    }).catch(() => {})
}

const openDetailDialog = async (row) => {
  const res = await getSimulationDetail(row.id)
  detailText.value = JSON.stringify(res.data, null, 2)
  detailDialogVisible.value = true
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.simulation-list {
  .search-card { margin-bottom: 16px;
    .el-form-item { margin-bottom: 0; margin-right: 16px; }
  }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>
