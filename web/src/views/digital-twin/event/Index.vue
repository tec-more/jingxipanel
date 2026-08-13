<template>
  <div class="event-list">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="事件编码">
          <el-input v-model="searchForm.event_code" clearable />
        </el-form-item>
        <el-form-item label="实体编码">
          <el-input v-model="searchForm.entity_code" clearable />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.event_type" clearable style="width: 140px">
            <el-option label="状态变更" value="state_change" />
            <el-option label="告警" value="alarm" />
            <el-option label="维护" value="maintenance" />
            <el-option label="异常" value="anomaly" />
          </el-select>
        </el-form-item>
        <el-form-item label="级别">
          <el-select v-model="searchForm.event_level" clearable style="width: 120px">
            <el-option label="信息" value="info" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_resolved" clearable style="width: 100px">
            <el-option label="未处理" :value="false" />
            <el-option label="已处理" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="event_code" label="事件编码" min-width="140" />
        <el-table-column prop="entity_name" label="实体" min-width="120" />
        <el-table-column prop="event_type" label="类型" width="100">
          <template #default="{ row }">{{ typeMap[row.event_type] || row.event_type }}</template>
        </el-table-column>
        <el-table-column label="级别" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="levelTypeMap[row.event_level] || 'info'">{{ levelMap[row.event_level] || row.event_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态变更" width="160">
          <template #default="{ row }">
            <span v-if="row.from_status || row.to_status">{{ row.from_status }} → {{ row.to_status }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" show-overflow-tooltip />
        <el-table-column label="处理状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_resolved ? 'success' : 'danger'">{{ row.is_resolved ? '已处理' : '未处理' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.is_resolved" size="small" type="primary" @click="openResolveDialog(row)">处理</el-button>
            <span v-else style="color: #909399">已处理</span>
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

    <el-dialog v-model="resolveDialogVisible" title="处理孪生事件" width="480px">
      <el-form label-width="80px">
        <el-form-item label="事件">
          <span>{{ currentEvent?.event_code }} - {{ currentEvent?.title }}</span>
        </el-form-item>
        <el-form-item label="处理人">
          <el-input v-model="resolveForm.resolved_by" />
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="resolveForm.resolve_remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getEventList, resolveEvent } from '@/api/digitalTwin'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ event_code: '', entity_code: '', event_type: null, event_level: null, is_resolved: null })
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const typeMap = { state_change: '状态变更', alarm: '告警', maintenance: '维护', anomaly: '异常' }
const levelMap = { info: '信息', warning: '警告', error: '错误', critical: '严重' }
const levelTypeMap = { info: 'info', warning: 'warning', error: 'danger', critical: 'danger' }

const resolveDialogVisible = ref(false)
const currentEvent = ref(null)
const resolveForm = reactive({ resolved_by: '', resolve_remark: '' })

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getEventList({ page: pagination.page, page_size: pagination.pageSize, ...searchForm })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.event_code = ''
  searchForm.entity_code = ''
  searchForm.event_type = null
  searchForm.event_level = null
  searchForm.is_resolved = null
  handleSearch()
}

const openResolveDialog = (row) => {
  currentEvent.value = row
  resolveForm.resolved_by = ''
  resolveForm.resolve_remark = ''
  resolveDialogVisible.value = true
}

const handleResolve = async () => {
  await resolveEvent(currentEvent.value.id, { ...resolveForm })
  ElMessage.success('事件已处理')
  resolveDialogVisible.value = false
  fetchData()
}

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.event-list {
  .search-card { margin-bottom: 16px;
    .el-form-item { margin-bottom: 0; margin-right: 16px; }
  }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>
