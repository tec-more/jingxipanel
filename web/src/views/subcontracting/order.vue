<template>
  <div class="subcontracting-order">
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="工单编号">
          <el-input v-model="searchForm.order_no" placeholder="请输入工单编号" clearable />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="searchForm.supplier_name" placeholder="请输入供应商名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 140px">
            <el-option label="待审核" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="生产中" value="producing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>委外工单列表</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="order_no" label="工单编号" min-width="140" />
        <el-table-column prop="product_name" label="产品" min-width="150" />
        <el-table-column prop="supplier_name" label="供应商" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="100" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status] || 'info'">
              {{ statusLabelMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleView(row)">查看</el-button>
            <el-button type="success" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <el-empty description="暂无数据" />
        </template>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  order_no: '',
  supplier_name: '',
  status: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const statusTypeMap = {
  pending: 'warning',
  confirmed: 'primary',
  producing: '',
  completed: 'success',
  cancelled: 'danger'
}

const statusLabelMap = {
  pending: '待审核',
  confirmed: '已确认',
  producing: '生产中',
  completed: '已完成',
  cancelled: '已取消'
}

const fetchData = async () => {
  loading.value = true
  try {
    // TODO: 调用API获取数据
    tableData.value = []
    pagination.total = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; fetchData() }
const handleReset = () => {
  searchForm.order_no = ''
  searchForm.supplier_name = ''
  searchForm.status = null
  handleSearch()
}
const handleAdd = () => { ElMessage.info('新增功能待实现') }
const handleEdit = (row) => { ElMessage.info(`编辑: ${row.order_no}`) }
const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
    .then(() => { ElMessage.success('删除成功'); fetchData() })
    .catch(() => {})
}
const handleView = (row) => { ElMessage.info(`查看: ${row.order_no}`) }

onMounted(() => { fetchData() })
</script>

<style lang="scss" scoped>
.subcontracting-order {
  .search-card { margin-bottom: 16px;
    .search-form { display: flex; flex-wrap: wrap;
      .el-form-item { margin-bottom: 0; margin-right: 16px; }
    }
  }
  .table-card {
    .card-header { display: flex; justify-content: space-between; align-items: center; }
  }
  .pagination-wrapper { margin-top: 16px; display: flex; justify-content: flex-end; }
}
</style>