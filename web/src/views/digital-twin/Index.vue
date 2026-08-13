<template>
  <div class="digital-twin-container">
    <el-tabs v-model="activeTab" type="border-card" class="twin-tabs">
      <el-tab-pane label="孪生看板" name="dashboard">
        <Dashboard v-if="activeTab === 'dashboard'" />
      </el-tab-pane>
      <el-tab-pane label="孪生实体" name="entity">
        <EntityList v-if="activeTab === 'entity'" />
      </el-tab-pane>
      <el-tab-pane label="孪生场景" name="scene">
        <SceneList v-if="activeTab === 'scene'" />
      </el-tab-pane>
      <el-tab-pane label="数据接入" name="data">
        <DataIngest v-if="activeTab === 'data'" />
      </el-tab-pane>
      <el-tab-pane label="孪生事件" name="event">
        <EventList v-if="activeTab === 'event'" />
      </el-tab-pane>
      <el-tab-pane label="仿真预测" name="simulation">
        <SimulationList v-if="activeTab === 'simulation'" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Dashboard from './dashboard/Index.vue'
import EntityList from './entity/Index.vue'
import SceneList from './scene/Index.vue'
import DataIngest from './data/Index.vue'
import EventList from './event/Index.vue'
import SimulationList from './simulation/Index.vue'

const activeTab = ref('dashboard')
</script>

<style lang="scss" scoped>
.digital-twin-container {
  padding: 16px;
  .twin-tabs {
    :deep(.el-tabs__content) {
      padding: 16px;
    }
  }
}
</style>
