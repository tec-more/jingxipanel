<template>
  <div class="data-ingest">
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="never" header="实时数据查询">
          <el-form :inline="true" :model="queryForm">
            <el-form-item label="实体编码">
              <el-input v-model="queryForm.entity_code" placeholder="实体编码" />
            </el-form-item>
            <el-form-item label="指标">
              <el-input v-model="queryForm.metric_code" placeholder="指标编码（可空）" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchRealtime">查询最新值</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="realtimeData" border size="small" style="margin-top: 12px">
            <el-table-column prop="metric_code" label="指标编码" />
            <el-table-column prop="metric_name" label="指标名称" />
            <el-table-column prop="value" label="数值" width="100" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="quality" label="质量" width="80" />
            <el-table-column prop="collected_at" label="采集时间" width="170" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="历史数据查询">
          <el-form :model="historyForm" label-width="80px">
            <el-form-item label="实体编码">
              <el-input v-model="historyForm.entity_code" />
            </el-form-item>
            <el-form-item label="指标">
              <el-input v-model="historyForm.metric_code" placeholder="可空" />
            </el-form-item>
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="historyForm.timeRange"
                type="datetimerange"
                range-separator="-"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="YYYY-MM-DDTHH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="点数">
              <el-input-number v-model="historyForm.limit" :min="1" :max="5000" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchHistory">查询历史</el-button>
            </el-form-item>
          </el-form>
          <div v-if="historyData.length" style="margin-top: 12px">
            <div style="margin-bottom: 8px; color: #606266">共 {{ historyData.length }} 条记录</div>
            <el-table :data="historyData.slice(0, 20)" border size="small" max-height="240">
              <el-table-column prop="metric_code" label="指标" />
              <el-table-column prop="value" label="数值" width="100" />
              <el-table-column prop="unit" label="单位" width="80" />
              <el-table-column prop="collected_at" label="采集时间" width="170" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" header="数据写入" style="margin-top: 16px">
      <el-form :model="ingestForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="实体编码">
              <el-input v-model="ingestForm.entity_code" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="指标编码">
              <el-input v-model="ingestForm.metric_code" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="指标名称">
              <el-input v-model="ingestForm.metric_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="指标类型">
              <el-select v-model="ingestForm.metric_type" style="width: 100%">
                <el-option label="温度" value="temperature" />
                <el-option label="振动" value="vibration" />
                <el-option label="压力" value="pressure" />
                <el-option label="电流" value="current" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="数值">
              <el-input-number v-model="ingestForm.value" :controls="false" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="单位">
              <el-input v-model="ingestForm.unit" placeholder="如 ℃、MPa" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="采集时间">
              <el-date-picker v-model="ingestForm.collected_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="handleIngest">写入数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRealtimeData, getHistoryData, ingestData } from '@/api/digitalTwin'

const queryForm = reactive({ entity_code: '', metric_code: '' })
const realtimeData = ref([])

const historyForm = reactive({
  entity_code: '',
  metric_code: '',
  timeRange: [],
  limit: 500
})
const historyData = ref([])

const now = () => new Date().toISOString().slice(0, 19)
const ingestForm = reactive({
  entity_code: '',
  metric_code: '',
  metric_name: '',
  metric_type: 'temperature',
  value: 0,
  unit: '',
  collected_at: now()
})

const fetchRealtime = async () => {
  if (!queryForm.entity_code) {
    ElMessage.warning('请输入实体编码')
    return
  }
  const res = await getRealtimeData(queryForm.entity_code, queryForm.metric_code || undefined)
  realtimeData.value = res.data.points || []
}

const fetchHistory = async () => {
  if (!historyForm.entity_code) {
    ElMessage.warning('请输入实体编码')
    return
  }
  const params = {
    entity_code: historyForm.entity_code,
    metric_code: historyForm.metric_code || undefined,
    limit: historyForm.limit
  }
  if (historyForm.timeRange && historyForm.timeRange.length === 2) {
    params.start_time = historyForm.timeRange[0]
    params.end_time = historyForm.timeRange[1]
  }
  const res = await getHistoryData(params)
  historyData.value = res.data.points || []
}

const handleIngest = async () => {
  if (!ingestForm.entity_code || !ingestForm.metric_code) {
    ElMessage.warning('实体编码和指标编码必填')
    return
  }
  await ingestData({ ...ingestForm })
  ElMessage.success('数据已写入')
  // 刷新实时数据
  if (queryForm.entity_code === ingestForm.entity_code) {
    fetchRealtime()
  }
}

onMounted(() => {})
</script>
