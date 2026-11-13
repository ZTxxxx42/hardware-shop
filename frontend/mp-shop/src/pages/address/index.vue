<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { ensureLogin } from '@/utils/auth'
import type { Address } from '@/types/shop'
import RequestState from '@/components/RequestState.vue'
import LoginPrompt from '@/components/LoginPrompt.vue'

const addresses = ref<Address[]>([])
const loading = ref(true)
const error = ref('')
const needsLogin = ref(false)
const formOpen = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ receiver: '', phone: '', region: '', detail: '' })

function resetForm() {
  form.receiver = ''
  form.phone = ''
  form.region = ''
  form.detail = ''
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
  resetForm()
  formOpen.value = true
}

function openEdit(address: Address) {
  editingId.value = address.id
  form.receiver = address.receiver
  form.phone = address.phone
  form.region = address.region
  form.detail = address.detail
  formOpen.value = true
}

function closeForm() {
  if (submitting.value) return
  formOpen.value = false
}

async function submit() {
  const receiver = form.receiver.trim()
  const phone = form.phone.trim()
  const region = form.region.trim()
  const detail = form.detail.trim()

  if (!receiver) {
    uni.showToast({ title: '请输入收货人姓名', icon: 'none' })
    return
  }
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    uni.showToast({ title: '请输入有效的手机号', icon: 'none' })
    return
  }
  if (!region) {
    uni.showToast({ title: '请输入所在地区', icon: 'none' })
    return
  }
  if (!detail) {
    uni.showToast({ title: '请输入详细地址', icon: 'none' })
    return
  }

  submitting.value = true
  const payload = { receiver, phone, region, detail }
  try {
    if (editingId.value) {
      await memberApi.updateAddress(editingId.value, payload)
      uni.showToast({ title: '地址已更新', icon: 'success' })
    } else {
      await memberApi.createAddress(payload)
      uni.showToast({ title: '地址已添加', icon: 'success' })
    }
    formOpen.value = false
    await loadAddresses()
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '保存地址失败'), icon: 'none' })
  } finally {
    submitting.value = false
  }
}

async function removeAddress(address: Address) {
  const ok = await new Promise<boolean>((resolve) => {
    uni.showModal({
      title: '删除地址',
      content: `确定删除“${address.receiver}”的收货地址吗？`,
      confirmText: '删除',
      cancelText: '取消',
      success: (res) => resolve(res.confirm),
      fail: () => resolve(false),
    })
  })
  if (!ok) return
  try {
    await memberApi.removeAddress(address.id)
    uni.showToast({ title: '地址已删除', icon: 'success' })
    await loadAddresses()
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '删除地址失败'), icon: 'none' })
  }
}

onShow(() => {
  if (!ensureLogin()) {
    needsLogin.value = true
    loading.value = false
    error.value = ''
    return
  }
  needsLogin.value = false
  void loadAddresses()
})
</script>

<template>
  <view class="page-pad address-page">
    <view class="page-heading">
      <view class="page-heading__row">
        <view>
          <text class="eyebrow">DELIVERY ADDRESS</text>
          <view class="page-title">地址管理</view>
          <text class="page-subtitle">维护收货人、联系电话与收货地址</text>
        </view>
        <button v-if="!needsLogin" class="btn btn-primary page-heading__add" @tap="openCreate">新增地址</button>
      </view>
    </view>

    <LoginPrompt
      v-if="needsLogin"
      title="登录后管理收货地址"
      :redirect="'/pages/address/index'"
    />
    <RequestState
      v-else-if="loading || error || addresses.length === 0"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载收货地址..."
      empty-text="暂无收货地址，请点击右上角新增"
      @retry="loadAddresses"
    />
    <view v-else class="address-list">
      <view v-for="address in addresses" :key="address.id" class="address-card card">
        <view class="address-card__head">
          <view class="address-card__title">
            <text class="address-card__receiver">{{ address.receiver }}</text>
            <text class="address-card__phone">{{ address.phone }}</text>
          </view>
          <view class="address-card__actions">
            <text class="address-card__edit" @tap="openEdit(address)">编辑</text>
            <text class="address-card__delete" @tap="removeAddress(address)">删除</text>
          </view>
        </view>
        <text class="address-card__text">{{ address.region }} {{ address.detail }}</text>
      </view>
    </view>

    <view v-if="formOpen" class="mask" @tap="closeForm">
      <view class="sheet" @tap.stop>
        <view class="sheet__title">{{ editingId ? '编辑地址' : '新增地址' }}</view>
        <view class="form-field">
          <text class="form-field__label">收货人</text>
          <input v-model="form.receiver" class="form-field__input" type="text" placeholder="请输入收货人姓名" placeholder-class="form-field__placeholder" />
        </view>
        <view class="form-field">
          <text class="form-field__label">联系电话</text>
          <input v-model="form.phone" class="form-field__input" type="number" maxlength="11" placeholder="请输入手机号" placeholder-class="form-field__placeholder" />
        </view>
        <view class="form-field">
          <text class="form-field__label">所在地区</text>
          <input v-model="form.region" class="form-field__input" type="text" placeholder="例如：浙江省 杭州市" placeholder-class="form-field__placeholder" />
        </view>
        <view class="form-field">
          <text class="form-field__label">详细地址</text>
          <textarea v-model="form.detail" class="form-field__textarea" maxlength="120" placeholder="请输入街道、门牌号等详细地址" placeholder-class="form-field__placeholder" />
        </view>
        <view class="sheet__actions">
          <button class="btn btn-ghost sheet__btn" @tap="closeForm">取消</button>
          <button class="btn btn-primary sheet__btn" :disabled="submitting" @tap="submit">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.page-heading {
  padding: 10rpx 0 26rpx;
}

.page-heading__row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.page-heading__add {
  min-height: 68rpx;
  padding: 0 28rpx;
  font-size: 24rpx;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.address-card {
  padding: 26rpx 28rpx;
}

.address-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.address-card__title {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.address-card__receiver {
  color: #26384c;
  font-size: 29rpx;
  font-weight: 650;
}

.address-card__phone {
  color: #8391a0;
  font-size: 22rpx;
}

.address-card__actions {
  display: flex;
  align-items: center;
  gap: 26rpx;
}

.address-card__edit {
  color: var(--brand);
  font-size: 24rpx;
}

.address-card__delete {
  color: #ef5350;
  font-size: 24rpx;
}

.address-card__text {
  display: block;
  margin-top: 10rpx;
  color: #657689;
  font-size: 24rpx;
  line-height: 1.7;
}

.mask {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 50;
  display: flex;
  align-items: flex-end;
  background: rgb(16 43 73 / 45%);
}

.sheet {
  width: 100%;
  padding: 32rpx 28rpx calc(32rpx + env(safe-area-inset-bottom));
  border-radius: 28rpx 28rpx 0 0;
  background: #ffffff;
}

.sheet__title {
  margin-bottom: 24rpx;
  font-size: 32rpx;
  font-weight: 700;
}

.form-field {
  margin-bottom: 22rpx;
}

.form-field__label {
  display: block;
  margin-bottom: 10rpx;
  color: #46586b;
  font-size: 24rpx;
}

.form-field__input {
  height: 84rpx;
  padding: 0 24rpx;
  border: 1rpx solid #e0e7ef;
  border-radius: 14rpx;
  background: #f8fafc;
  font-size: 26rpx;
}

.form-field__textarea {
  width: 100%;
  min-height: 150rpx;
  padding: 20rpx 24rpx;
  border: 1rpx solid #e0e7ef;
  border-radius: 14rpx;
  background: #f8fafc;
  font-size: 26rpx;
}

.form-field__placeholder {
  color: #a0abb7;
}

.sheet__actions {
  display: flex;
  gap: 20rpx;
  margin-top: 10rpx;
}

.sheet__btn {
  min-height: 84rpx;
  flex: 1;
  border-radius: 14rpx;
}
</style>
