<template>
  <div class="twin-dashboard">
    <!-- 概览卡片 -->
    <el-row :gutter="16" class="overview-row">
      <el-col :span="4" v-for="card in overviewCards" :key="card.key">
        <el-card shadow="hover" class="overview-card">
          <div class="card-value" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="card-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card shadow="never" header="实体状态分布">
          <div v-loading="loadingStatus">
            <div v-for="item in statusDistribution" :key="item.status" class="status-bar-item">
              <span class="status-label">
                <el-tag :type="statusTypeMap[item.status] || 'info'" size="small">{{ statusMap[item.status] || item.status }}</el-tag>
              </span>
              <el-progress :percentage="getPercent(item.count)" :stroke-width="14" :format="() => `${item.count}`" />
            </div>
            <el-empty v-if="!statusDistribution.length" description="暂无数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" header="告警事件汇总">
          <div v-loading="loadingAlarm">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="事件总数">{{ alarmSummary.total || 0 }}</el-descriptions-item>
              <el-descriptions-item label="未处理">{{ alarmSummary.unresolved || 0 }}</el-descriptions-item>
            </el-descriptions>
            <div style="margin-top: 16px">
              <div v-for="(cnt, level) in (alarmSummary.by_level || {})" :key="level" class="alarm-level-item">
                <el-tag :type="levelTypeMap[level]" size="small">{{ levelMap[level] || level }}</el-tag>
                <span style="margin-left: 12px">{{ cnt }} 条未处理</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getDashboardOverview, getStatusDistribution, getAlarmSummary } from '@/api/digitalTwin'

const overview = ref({})
const statusDistribution = ref([])
const alarmSummary = ref({})
const loadingStatus = ref(false)
const loadingAlarm = ref(false)

const statusMap = { normal: '正常', warning: '警告', error: '错误', maintenance: '维护中', offline: '离线' }
const statusTypeMap = { normal: 'success', warning: 'warning', error: 'danger', maintenance: 'info', offline: 'info' }
const levelMap = { info: '信息', warning: '警告', error: '错误', critical: '严重' }
const levelTypeMap = { info: 'info', warning: 'warning', error: 'danger', critical: 'danger' }

const overviewCards = computed(() => [
  { key: 'entities', label: '孪生实体', value: overview.value.total_entities || 0, color: '#409eff' },
  { key: 'active', label: '启用实体', value: overview.value.active_entities || 0, color: '#67c23a' },
  { key: 'scenes', label: '孪生场景', value: overview.value.total_scenes || 0, color: '#909399' },
  { key: 'unresolved', label: '未处理事件', value: overview.value.unresolved_events || 0, color: '#e6a23c' },
  { key: 'running', label: '运行中仿真', value: overview.value.running_simulations || 0, color: '#f56c6c' }
])

const getPercent = (count) => {
  const total = statusDistribution.value.reduce((s, i) => s + i.count, 0) || 1
  return Math.round(count / total * 100)
}

const fetchOverview = async () => {
  const res = await getDashboardOverview()
  overview.value = res.data || {}
}
const fetchStatus = async () => {
  loadingStatus.value = true
  try {
    const res = await getStatusDistribution()
    statusDistribution.value = res.data || []
  } finally { loadingStatus.value = false }
}
const fetchAlarm = async () => {
  loadingAlarm.value = true
  try {
    const res = await getAlarmSummary()
    alarmSummary.value = res.data || {}
  } finally { loadingAlarm.value = false }
}

onMounted(() => {
  fetchOverview()
  fetchStatus()
  fetchAlarm()
})
</script>

<style lang="scss" scoped>
.twin-dashboard {
  .overview-row { margin-bottom: 0; }
  .overview-card {
    text-align: center;
    .card-value { font-size: 28px; font-weight: 600; }
    .card-label { color: #909399; margin-top: 4px; font-size: 13px; }
  }
  .status-bar-item {
    display: flex; align-items: center; margin-bottom: 12px;
    .status-label { width: 80px; }
    .el-progress { flex: 1; }
  }
  .alarm-level-item {
    margin-bottom: 10px;
  }
}
</style>
