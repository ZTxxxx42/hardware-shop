<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Edit, Location, Plus } from '@element-plus/icons-vue'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import type { Address } from '@/types/shop'
import RequestState from '@/components/RequestState.vue'

const addresses = ref<Address[]>([])
const loading = ref(true)
const error = ref('')
const dialogOpen = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive({ receiver: '', phone: '', region: '', detail: '' })

const rules: FormRules = {
  receiver: [{ required: true, message: '请输入收货人姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' },
  ],
  region: [{ required: true, message: '请输入所在地区', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
}

async function loadAddresses() {
  loading.value = true
  error.value = ''
  try {
    addresses.value = await memberApi.addresses()
  } catch (requestError) {
    addresses.value = []
    error.value = getErrorMessage(requestError, '地址加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.receiver = ''
  form.phone = ''
  form.region = ''
  form.detail = ''
  dialogOpen.value = true
}

function openEdit(address: Address) {
  editingId.value = address.id
  form.receiver = address.receiver
  form.phone = address.phone
  form.region = address.region
  form.detail = address.detail
  dialogOpen.value = true
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  const payload = {
    receiver: form.receiver.trim(),
    phone: form.phone.trim(),
    region: form.region.trim(),
    detail: form.detail.trim(),
  }
  try {
    if (editingId.value) {
      await memberApi.updateAddress(editingId.value, payload)
      ElMessage.success('地址已更新')
    } else {
      await memberApi.createAddress(payload)
      ElMessage.success('地址已添加')
    }
    dialogOpen.value = false
    await loadAddresses()
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '保存地址失败，请稍后重试'))
  } finally {
    submitting.value = false
  }
}

async function removeAddress(address: Address) {
  try {
    await ElMessageBox.confirm(`确定删除“${address.receiver}”的收货地址吗？`, '删除地址', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await memberApi.removeAddress(address.id)
    ElMessage.success('地址已删除')
    await loadAddresses()
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '删除地址失败，请稍后重试'))
  }
}

onMounted(loadAddresses)
</script>

<template>
  <section class="address-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>地址管理</span></nav>
      <div class="page-heading">
        <div><span>DELIVERY ADDRESS</span><h1>地址管理</h1><p>维护收货人、联系电话与收货地址，下单时快速选择</p></div>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增地址</el-button>
      </div>
      <RequestState
        v-if="loading || error || addresses.length === 0"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在加载收货地址..."
        empty-text="暂无收货地址，请点击右上角新增"
        @retry="loadAddresses"
      />
      <div v-else class="address-grid">
        <article v-for="address in addresses" :key="address.id" class="address-card">
          <div class="address-icon"><el-icon :size="22"><Location /></el-icon></div>
          <div class="address-body">
            <div class="address-title"><strong>{{ address.receiver }}</strong><span>{{ address.phone }}</span></div>
            <p class="address-text">{{ address.region }} {{ address.detail }}</p>
          </div>
          <div class="address-actions">
            <el-button text type="primary" :icon="Edit" @click="openEdit(address)">编辑</el-button>
            <el-button text type="danger" @click="removeAddress(address)">删除</el-button>
          </div>
        </article>
      </div>
    </div>

    <el-dialog v-model="dialogOpen" :title="editingId ? '编辑地址' : '新增地址'" width="min(480px, 92%)" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="收货人" prop="receiver">
          <el-input v-model="form.receiver" placeholder="请输入收货人姓名" clearable />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="所在地区" prop="region">
          <el-input v-model="form.region" placeholder="例如：浙江省 杭州市" clearable />
        </el-form-item>
        <el-form-item label="详细地址" prop="detail">
          <el-input v-model="form.detail" type="textarea" :rows="3" placeholder="请输入街道、门牌号等详细地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.address-page { min-height: 620px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin: 32px 0 25px; }
.page-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.page-heading h1 { margin-top: 3px; font-size: 30px; }
.page-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.address-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.address-card { display: flex; align-items: flex-start; gap: 14px; padding: 20px 21px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); }
.address-icon { display: grid; width: 42px; height: 42px; flex: 0 0 auto; place-items: center; border-radius: 12px; color: var(--brand); background: var(--brand-light); }
.address-body { min-width: 0; flex: 1; }
.address-title { display: flex; align-items: center; gap: 10px; }
.address-title strong { color: #26384c; font-size: 15px; }
.address-title span { color: #8391a0; font-size: 12px; }
.address-text { margin-top: 5px; color: #657689; font-size: 13px; line-height: 1.7; }
.address-actions { display: flex; flex: 0 0 auto; }
@media (max-width: 767px) {
  .address-page { padding-top: 18px; }
  .page-heading { align-items: flex-start; margin: 25px 0 20px; }
  .page-heading h1 { font-size: 26px; }
  .page-heading p { font-size: 12px; }
  .page-heading > .el-button { padding-inline: 14px; }
  .address-grid { grid-template-columns: 1fr; gap: 12px; }
  .address-card { padding: 17px 16px; }
}
</style>
