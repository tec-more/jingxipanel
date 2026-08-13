<template>
  <div class="scene-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="场景编码">
          <el-input v-model="searchForm.scene_code" clearable />
        </el-form-item>
        <el-form-item label="场景名称">
          <el-input v-model="searchForm.scene_name" clearable />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.scene_type" clearable style="width: 140px">
            <el-option label="工厂" value="factory" />
            <el-option label="车间" value="workshop" />
            <el-option label="产线" value="production_line" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="openAddDialog">新增场景</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="scene_code" label="编码" min-width="120" />
        <el-table-column prop="scene_name" label="名称" min-width="150" />
        <el-table-column prop="scene_type" label="类型" width="100">
          <template #default="{ row }">{{ typeMap[row.scene_type] || row.scene_type }}</template>
        </el-table-column>
        <el-table-column label="实体数量" width="100" align="center">
          <template #default="{ row }">{{ (row.entity_ids || []).length }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="openEntitiesDialog(row)">关联实体</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="场景编码" prop="scene_code">
          <el-input v-model="formData.scene_code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="场景名称" prop="scene_name">
          <el-input v-model="formData.scene_name" />
        </el-form-item>
        <el-form-item label="场景类型" prop="scene_type">
          <el-select v-model="formData.scene_type" style="width: 100%">
            <el-option label="工厂" value="factory" />
            <el-option label="车间" value="workshop" />
            <el-option label="产线" value="production_line" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="缩略图">
          <el-input v-model="formData.thumbnail" placeholder="缩略图路径" />
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

    <el-dialog v-model="entitiesDialogVisible" title="关联实体" width="640px">
      <el-table :data="allEntities" border max-height="400" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="entity_code" label="编码" />
        <el-table-column prop="entity_name" label="名称" />
        <el-table-column prop="entity_type" label="类型" width="100" />
        <el-table-column prop="current_status" label="状态" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="entitiesDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEntities">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSceneList, createScene, updateScene, deleteScene, setSceneEntities, getEntityList } from '@/api/digitalTwin'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ scene_code: '', scene_name: '', scene_type: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const defaultForm = () => ({
  id: null, scene_code: '', scene_name: '', scene_type: 'custom',
  thumbnail: '', description: '', is_active: true
})
const formData = reactive(defaultForm())
const formRules = {
  scene_code: [{ required: true, message: '请输入场景编码', trigger: 'blur' }],
  scene_name: [{ required: true, message: '请输入场景名称', trigger: 'blur' }]
}

const typeMap = { factory: '工厂', workshop: '车间', production_line: '产线', custom: '自定义' }

const entitiesDialogVisible = ref(false)
const allEntities = ref([])
const selectedIds = ref([])
const currentScene = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getSceneList({ page: pagination.page, page_size: pagination.pageSize, ...searchForm })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.scene_code = ''
  searchForm.scene_name = ''
  searchForm.scene_type = null
  handleSearch()
}

const openAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增孪生场景'
  Object.assign(formData, defaultForm())
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑孪生场景'
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
      delete payload.entity_ids
      if (isEdit.value) {
        await updateScene(formData.id, payload)
        ElMessage.success('更新成功')
      } else {
        await createScene(payload)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (e) { console.error(e) } finally { submitLoading.value = false }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除场景 "${row.scene_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await deleteScene(row.id)
      ElMessage.success('删除成功')
      fetchData()
    }).catch(() => {})
}

const openEntitiesDialog = async (row) => {
  currentScene.value = row
  const res = await getEntityList({ page: 1, page_size: 200 })
  allEntities.value = res.data.items || []
  selectedIds.value = row.entity_ids || []
  entitiesDialogVisible.value = true
  // 设置默认选中
  setTimeout(() => {
    const tableRef = entitiesTableRef.value
    if (tableRef) {
      allEntities.value.forEach(item => {
        if ((row.entity_ids || []).includes(item.id)) {
          tableRef.toggleRowSelection(item, true)
        }
      })
    }
  }, 100)
}

const entitiesTableRef = ref(null)

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(i => i.id)
}

const handleSaveEntities = async () => {
  await setSceneEntities(currentScene.value.id, selectedIds.value)
  ElMessage.success('关联实体已更新')
  entitiesDialogVisible.value = false
  fetchData()
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.scene-list {
  .search-card { margin-bottom: 16px;
    .el-form-item { margin-bottom: 0; margin-right: 16px; }
  }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>
