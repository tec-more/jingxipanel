<template>
  <div class="agent-landing">
    <el-card shadow="never">
      <template #header>
        <span>智能体管理</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="item in modules" :key="item.path">
          <el-card shadow="hover" class="module-card" @click="$router.push(item.path)" style="cursor: pointer">
            <div class="module-icon">{{ item.icon }}</div>
            <div class="module-name">{{ item.name }}</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const modules = ref([
  { name: '智能体', path: '/panel/agent/list', icon: '🤖' },
  { name: '工作流', path: '/panel/agent/workflows', icon: '🔄' },
  { name: '对话流', path: '/panel/agent/dialog-flows', icon: '💬' },
  { name: '技能管理', path: '/panel/agent/skills', icon: '⚡' },
  { name: '工具管理', path: '/panel/agent/tools', icon: '🔧' },
  { name: '记忆管理', path: '/panel/agent/memory', icon: '🧠' },
  { name: 'RAG知识库', path: '/panel/agent/rag', icon: '📚' },
  { name: '执行记录', path: '/panel/agent/executions', icon: '📋' }
])
</script>

<style lang="scss" scoped>
.agent-landing {
  .module-card { text-align: center; margin-bottom: 16px;
    .module-icon { font-size: 32px; margin-bottom: 8px; }
    .module-name { font-size: 14px; color: #303133; }
  }
}
</style>
