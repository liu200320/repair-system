import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getRepairs, getRepair, createRepair, updateRepair, deleteRepair } from '../api/repair'

export const useRepairStore = defineStore('repair', () => {
  const list = ref([])
  const total = ref(0)
  const current = ref(null)
  const loading = ref(false)

  async function fetchList(params = {}) {
    loading.value = true
    try {
      const res = await getRepairs(params)
      list.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      current.value = await getRepair(id)
    } finally {
      loading.value = false
    }
  }

  async function create(data) {
    return await createRepair(data)
  }

  async function update(id, data) {
    return await updateRepair(id, data)
  }

  async function remove(id) {
    await deleteRepair(id)
  }

  return { list, total, current, loading, fetchList, fetchOne, create, update, remove }
})
