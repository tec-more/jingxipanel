<template>
  <div class="entity-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="实体编码">
          <el-input v-model="searchForm.entity_code" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="实体名称">
          <el-input v-model="searchForm.entity_name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.entity_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="设备" value="equipment" />
            <el-option label="产品" value="product" />
            <el-option label="工序" value="process" />
            <el-option label="产线" value="production_line" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.current_status" placeholder="全部" clearable style="width: 120px">
            <el-option label="正常" value="normal" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="openAddDialog">新增实体</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="entity_code" label="编码" min-width="120" />
        <el-table-column prop="entity_name" label="名称" min-width="150" />
        <el-table-column prop="entity_type" label="类型" width="100">
          <template #default="{ row }">{{ typeMap[row.entity_type] || row.entity_type }}</template>
        </el-table-column>
        <el-table-column prop="source_code" label="来源编码" min-width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.current_status] || 'info'">
              {{ statusMap[row.current_status] || row.current_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_sync_time" label="最后同步" width="170" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="openStatusDialog(row)">状态</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px" @close="handleDialogClose">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="实体编码" prop="entity_code">
              <el-input v-model="formData.entity_code" :disabled="isEdit" placeholder="唯一编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实体名称" prop="entity_name">
              <el-input v-model="formData.entity_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="实体类型" prop="entity_type">
              <el-select v-model="formData.entity_type" style="width: 100%">
                <el-option label="设备" value="equipment" />
                <el-option label="产品" value="product" />
                <el-option label="工序" value="process" />
                <el-option label="产线" value="production_line" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源编码">
              <el-input v-model="formData.source_code" placeholder="如设备编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="父实体编码">
              <el-input v-model="formData.parent_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据来源">
              <el-select v-model="formData.source_type" style="width: 100%">
                <el-option label="IoT" value="iot" />
                <el-option label="手工" value="manual" />
                <el-option label="仿真" value="simulated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="X 坐标">
              <el-input-number v-model="formData.position_x" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Y 坐标">
              <el-input-number v-model="formData.position_y" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Z 坐标">
              <el-input-number v-model="formData.position_z" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="刷新间隔">
          <el-input-number v-model="formData.refresh_interval" :min="1" />
          <span style="margin-left: 8px; color: #909399">秒</span>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 状态变更对话框 -->
    <el-dialog v-model="statusDialogVisible" title="更新实体状态" width="440px">
      <el-form label-width="80px">
        <el-form-item label="实体">
          <span>{{ currentEntity?.entity_name }} ({{ currentEntity?.entity_code }})</span>
        </el-form-item>
        <el-form-item label="当前状态">
          <el-tag :type="statusTypeMap[currentEntity?.current_status]">{{ statusMap[currentEntity?.current_status] }}</el-tag>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="statusForm.status" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="statusForm.reason" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleStatusSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEntityList, createEntity, updateEntity, deleteEntity, updateEntityStatus } from '@/api/digitalTwin'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ entity_code: '', entity_name: '', entity_type: null, current_status: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const defaultForm = () => ({
  id: null,
  entity_code: '',
  entity_name: '',
  entity_type: 'equipment',
  source_code: '',
  parent_code: '',
  position_x: 0,
  position_y: 0,
  position_z: 0,
  source_type: 'manual',
  refresh_interval: 30,
  description: '',
  is_active: true
})
const formData = reactive(defaultForm())

const formRules = {
  entity_code: [{ required: true, message: '请输入实体编码', trigger: 'blur' }],
  entity_name: [{ required: true, message: '请输入实体名称', trigger: 'blur' }],
  entity_type: [{ required: true, message: '请选择实体类型', trigger: 'change' }]
}

const statusMap = { normal: '正常', warning: '警告', error: '错误', maintenance: '维护中', offline: '离线' }
const statusTypeMap = { normal: 'success', warning: 'warning', error: 'danger', maintenance: 'info', offline: 'info' }
const typeMap = { equipment: '设备', product: '产品', process: '工序', production_line: '产线' }

const statusDialogVisible = ref(false)
const currentEntity = ref(null)
const statusForm = reactive({ status: 'normal', reason: '' })

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getEntityList({ page: pagination.page, page_size: pagination.pageSize, ...searchForm })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.entity_code = ''
  searchForm.entity_name = ''
  searchForm.entity_type = null
  searchForm.current_status = null
  handleSearch()
}

const openAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增孪生实体'
  Object.assign(formData, defaultForm())
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑孪生实体'
  Object.assign(formData, defaultForm(), row)
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = { ...formData }
      delete payload.id
      delete payload.created_at
      delete payload.updated_at
      delete payload.last_sync_time
      delete payload.properties
      if (isEdit.value) {
        await updateEntity(formData.id, payload)
        ElMessage.success('更新成功')
      } else {
        await createEntity(payload)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (e) { console.error(e) } finally { submitLoading.value = false }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除实体 "${row.entity_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await deleteEntity(row.id)
      ElMessage.success('删除成功')
      fetchData()
    }).catch(() => {})
}

const openStatusDialog = (row) => {
  currentEntity.value = row
  statusForm.status = row.current_status
  statusForm.reason = ''
  statusDialogVisible.value = true
}

const handleStatusSubmit = async () => {
  try {
    await updateEntityStatus(currentEntity.value.id, statusForm.status, statusForm.reason)
    ElMessage.success('状态已更新')
    statusDialogVisible.value = false
    fetchData()
  } catch (e) { console.error(e) }
}

const handleDialogClose = () => { formRef.value?.resetFields() }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.entity-list {
  .search-card { margin-bottom: 16px;
    .search-form { display: flex; flex-wrap: wrap;
      .el-form-item { margin-bottom: 0; margin-right: 16px; }
    }
  }
  .table-card { .card-header { display: flex; justify-content: space-between; align-items: center; } }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>
