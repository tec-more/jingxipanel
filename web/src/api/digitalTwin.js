import request from '@/utils/request'

const BASE = '/v1/digital-twin'

// ==================== 孪生实体 ====================
export const getEntityList = (params) => request.get(`${BASE}/entity`, { params })
export const getEntityDetail = (id) => request.get(`${BASE}/entity/${id}`)
export const createEntity = (data) => request.post(`${BASE}/entity`, data)
export const updateEntity = (id, data) => request.put(`${BASE}/entity/${id}`, data)
export const deleteEntity = (id) => request.delete(`${BASE}/entity/${id}`)
export const updateEntityStatus = (id, status, reason) => request.post(`${BASE}/entity/${id}/status`, { status, reason })
export const updateEntityProperties = (id, properties) => request.post(`${BASE}/entity/${id}/properties`, { properties })

// ==================== 孪生场景 ====================
export const getSceneList = (params) => request.get(`${BASE}/scene`, { params })
export const getSceneDetail = (id) => request.get(`${BASE}/scene/${id}`)
export const createScene = (data) => request.post(`${BASE}/scene`, data)
export const updateScene = (id, data) => request.put(`${BASE}/scene/${id}`, data)
export const deleteScene = (id) => request.delete(`${BASE}/scene/${id}`)
export const setSceneEntities = (id, entityIds) => request.post(`${BASE}/scene/${id}/entities`, { entity_ids: entityIds })

// ==================== 孪生数据 ====================
export const getRealtimeData = (entityCode, metricCode) => request.get(`${BASE}/data/realtime`, { params: { entity_code: entityCode, metric_code: metricCode } })
export const getHistoryData = (params) => request.get(`${BASE}/data/history`, { params })
export const ingestData = (data) => request.post(`${BASE}/data/ingest`, data)
export const ingestBatchData = (points) => request.post(`${BASE}/data/ingest/batch`, { points })

// ==================== 孪生事件 ====================
export const getEventList = (params) => request.get(`${BASE}/event`, { params })
export const getEventDetail = (id) => request.get(`${BASE}/event/${id}`)
export const createEvent = (data) => request.post(`${BASE}/event`, data)
export const resolveEvent = (id, data) => request.post(`${BASE}/event/${id}/resolve`, data)

// ==================== 孪生仿真 ====================
export const getSimulationList = (params) => request.get(`${BASE}/simulation`, { params })
export const getSimulationDetail = (id) => request.get(`${BASE}/simulation/${id}`)
export const createSimulation = (data) => request.post(`${BASE}/simulation`, data)
export const cancelSimulation = (id) => request.post(`${BASE}/simulation/${id}/cancel`)

// ==================== 看板统计 ====================
export const getDashboardOverview = () => request.get(`${BASE}/dashboard/overview`)
export const getStatusDistribution = () => request.get(`${BASE}/dashboard/status-distribution`)
export const getAlarmSummary = () => request.get(`${BASE}/dashboard/alarm-summary`)
