<script setup>
import { ref, onMounted, markRaw } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStatsSummary, getStatsTrend, getStatsLocations } from '../api/stats'
import { Document, Warning, Tools, CircleCheck } from '@element-plus/icons-vue'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent])

const summary  = ref(null)
const trendOpt = ref(null)
const locOpt   = ref(null)
const pieOpt   = ref(null)
const loading  = ref(true)

const statCards = ref([])

async function load() {
  loading.value = true
  try {
    const [s, t, l] = await Promise.all([getStatsSummary(), getStatsTrend(), getStatsLocations()])
    summary.value = s

    statCards.value = [
      { label: '总记录', value: s.total,       color: 'var(--color-primary)', bg: '#eff4ff', icon: markRaw(Document) },
      { label: '待维修', value: s.pending,     color: 'var(--color-warning)', bg: '#fffbeb', icon: markRaw(Warning) },
      { label: '维修中', value: s.in_progress, color: 'var(--color-info)',    bg: '#f0f9ff', icon: markRaw(Tools) },
      { label: '已完成', value: s.completed,   color: 'var(--color-success)', bg: '#f0fdf4', icon: markRaw(CircleCheck) },
    ]

    trendOpt.value = {
      title: { text: '近30天维修趋势', left: 'center', textStyle: { fontSize: 14, color: '#1f2937', fontWeight: 600 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: t.dates, axisLabel: { rotate: 45, fontSize: 10, color: '#6b7280' }, axisLine: { lineStyle: { color: '#e5e7eb' } } },
      yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#f3f4f6' } } },
      series: [{
        data: t.counts, type: 'line', smooth: true,
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(26,86,219,0.15)' }, { offset: 1, color: 'rgba(26,86,219,0)' }] } },
        itemStyle: { color: '#1a56db' }, lineStyle: { width: 2.5 },
      }],
      grid: { left: 40, right: 20, bottom: 60, top: 50 },
    }

    locOpt.value = {
      title: { text: '点位维修次数 TOP10', left: 'center', textStyle: { fontSize: 14, color: '#1f2937', fontWeight: 600 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#f3f4f6' } } },
      yAxis: { type: 'category', data: l.names.slice().reverse(), axisLabel: { width: 120, overflow: 'truncate', color: '#6b7280' } },
      series: [{ data: l.counts.slice().reverse(), type: 'bar', barMaxWidth: 24, itemStyle: { color: '#0ea5e9', borderRadius: [0, 4, 4, 0] } }],
      grid: { left: 130, right: 30, bottom: 30, top: 50 },
    }

    pieOpt.value = {
      title: { text: '状态分布', left: 'center', textStyle: { fontSize: 14, color: '#1f2937', fontWeight: 600 } },
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '68%'], center: ['50%', '45%'],
        data: [
          { value: s.pending,     name: '待维修', itemStyle: { color: '#f59e0b' } },
          { value: s.in_progress, name: '维修中', itemStyle: { color: '#0ea5e9' } },
          { value: s.completed,   name: '已完成', itemStyle: { color: '#22c55e' } },
        ],
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      }],
    }
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;" v-if="summary">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: card.bg, color: card.color }">
            <el-icon size="22"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 1：趋势 + 饼图 -->
    <el-row :gutter="16" style="margin-bottom: 16px;">
      <el-col :span="16">
        <el-card shadow="never">
          <v-chart v-if="trendOpt" :option="trendOpt" style="height: 280px;" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <v-chart v-if="pieOpt" :option="pieOpt" style="height: 280px;" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 2：点位排名 -->
    <el-card shadow="never">
      <v-chart v-if="locOpt" :option="locOpt" style="height: 320px;" autoresize />
    </el-card>
  </div>
</template>

<style scoped>
.stat-card { cursor: default; }
:deep(.stat-card .el-card__body) {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px;
  gap: 6px;
}
.stat-icon {
  width: 48px; height: 48px;
  border-radius: var(--radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}
.stat-value { font-size: 30px; font-weight: 700; line-height: 1; }
.stat-label { font-size: 13px; color: var(--color-text-secondary); }
</style>
