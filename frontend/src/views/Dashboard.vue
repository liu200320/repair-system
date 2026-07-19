<script setup>
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStatsSummary, getStatsTrend, getStatsLocations } from '../api/stats'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, TitleComponent, LegendComponent])

const summary   = ref(null)
const trendOpt  = ref(null)
const locOpt    = ref(null)
const pieOpt    = ref(null)
const loading   = ref(true)

async function load() {
  loading.value = true
  try {
    const [s, t, l] = await Promise.all([getStatsSummary(), getStatsTrend(), getStatsLocations()])
    summary.value = s

    trendOpt.value = {
      title: { text: '近30天维修趋势', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: t.dates, axisLabel: { rotate: 45, fontSize: 10 } },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{ data: t.counts, type: 'line', smooth: true, areaStyle: { opacity: 0.15 }, itemStyle: { color: '#1a56db' } }],
      grid: { left: 40, right: 20, bottom: 60, top: 50 },
    }

    locOpt.value = {
      title: { text: '点位维修次数 TOP10', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'value', minInterval: 1 },
      yAxis: { type: 'category', data: l.names.slice().reverse(), axisLabel: { width: 120, overflow: 'truncate' } },
      series: [{ data: l.counts.slice().reverse(), type: 'bar', itemStyle: { color: '#0ea5e9' } }],
      grid: { left: 130, right: 30, bottom: 30, top: 50 },
    }

    pieOpt.value = {
      title: { text: '状态分布', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
        data: [
          { value: s.pending,     name: '待维修', itemStyle: { color: '#f59e0b' } },
          { value: s.in_progress, name: '维修中', itemStyle: { color: '#3b82f6' } },
          { value: s.completed,   name: '已完成', itemStyle: { color: '#22c55e' } },
        ],
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
    <!-- 数字卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px;" v-if="summary">
      <el-col :span="6" v-for="(item, key) in [
        { label:'总记录', value: summary.total,       color:'#1a56db', icon:'📋' },
        { label:'待维修', value: summary.pending,     color:'#f59e0b', icon:'🔴' },
        { label:'维修中', value: summary.in_progress, color:'#3b82f6', icon:'🔧' },
        { label:'已完成', value: summary.completed,   color:'#22c55e', icon:'✅' },
      ]" :key="key">
        <el-card shadow="hover" style="text-align:center; padding:8px 0;">
          <div style="font-size:28px;">{{ item.icon }}</div>
          <div style="font-size:32px; font-weight:700;" :style="{ color: item.color }">{{ item.value }}</div>
          <div style="color:#909399; font-size:14px;">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 1：趋势 + 饼图 -->
    <el-row :gutter="16" style="margin-bottom:16px;">
      <el-col :span="16">
        <el-card shadow="never">
          <v-chart v-if="trendOpt" :option="trendOpt" style="height:280px;" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <v-chart v-if="pieOpt" :option="pieOpt" style="height:280px;" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表行 2：点位排名 -->
    <el-card shadow="never">
      <v-chart v-if="locOpt" :option="locOpt" style="height:320px;" autoresize />
    </el-card>
  </div>
</template>
