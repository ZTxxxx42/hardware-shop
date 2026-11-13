<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

type LegalTab = 'privacy' | 'agreement'
interface LegalSection { title: string; paragraphs: string[]; bullets?: string[] }

const activeTab = ref<LegalTab>('privacy')
const updatedAt = '2026年11月13日'
const privacySections: LegalSection[] = [
  {
    title: '我们收集的信息',
    paragraphs: ['恒泰五金仅在提供采购服务所必需的范围内处理信息：'],
    bullets: [
      '账号信息：会员账号、手机号码、会员等级与联系人资料。',
      '微信登录信息：选择微信登录时，后端通过临时 code 获取 openid 以识别账号；session_key 不下发，也不写入前端存储。',
      '交易与配送信息：购物车、订单、收货人、联系电话、收货地址、订单备注及物流信息。',
      '安全日志：保障账号与交易安全所需的服务端请求和异常记录。',
    ],
  },
  {
    title: '信息如何使用',
    paragraphs: ['上述信息用于登录认证、展示会员价格、处理购物车与订单、安排配送、提供售后服务，以及防范异常请求。我们不会将个人信息用于与上述目的无关的自动化营销。'],
  },
  {
    title: '存储、共享与第三方服务',
    paragraphs: ['账号和订单数据保存在恒泰五金自建服务端。我们不出售个人信息，仅在完成服务所必需时向物流配送方或微信平台提供相应信息。微信支付尚未接入，实际启用前会另行核对支付处理规则与授权范围。'],
  },
  {
    title: '你的选择与权利',
    paragraphs: ['你可以在个人中心维护收货信息、查看订单，或提交账号注销申请。申请状态为 PENDING（待处理），不代表账号已被即时删除；处理时需核验身份，并可能依法保留必要的交易记录。'],
  },
  {
    title: '政策更新与联系',
    paragraphs: ['服务功能或信息处理规则变化时，我们会更新本政策并在此公布。对个人信息处理或注销申请有疑问时，请通过恒泰五金现有客服渠道联系我们。'],
  },
]
const agreementSections: LegalSection[] = [
  {
    title: '服务说明',
    paragraphs: ['恒泰五金提供商品浏览、会员价格、购物车、下单、订单查询和物流展示服务。商品库存、价格与可售状态以提交订单时服务端确认结果为准。'],
  },
  {
    title: '账号与交易规则',
    paragraphs: ['你应妥善保管账号与登录凭证，并提供真实、准确的收货信息。订单按待支付、已支付、已发货、已完成或已取消等状态流转；操作以页面按钮和服务端校验结果为准。'],
  },
  {
    title: '价格与支付',
    paragraphs: ['会员价格依据账号等级实时计算，购物车展示价格不视为最终锁价。当前微信支付处于接入框架阶段，未成功接入前不会产生真实扣款，也不以页面提示代替服务端支付结果。'],
  },
  {
    title: '配送、收货与售后',
    paragraphs: ['物流公司、物流单号与发货时间以订单详情为准。收到商品后请核对数量、型号与外观；发现异常请保留商品、包装和凭证，并通过现有客服渠道联系处理。'],
  },
  {
    title: '账号注销与服务边界',
    paragraphs: ['你可以提交账号注销申请。申请进入待处理状态后需按流程审核，不会在客户端即时物理删除账号。法律法规要求保留的交易、财务或安全记录不因提交申请而立即删除。'],
  },
]
const sections = computed(() => activeTab.value === 'privacy' ? privacySections : agreementSections)

onLoad((options) => {
  activeTab.value = options?.tab === 'agreement' ? 'agreement' : 'privacy'
})
</script>

<template>
  <view class="page-pad legal-page">
    <view class="legal-hero">
      <text class="eyebrow">HENGTAI / LEGAL</text>
      <view class="page-title">协议与隐私</view>
      <text class="page-subtitle">了解账号、订单与个人信息的处理规则</text>
    </view>
    <view class="legal-tabs" role="tablist">
      <button class="legal-tabs__item" :class="{ 'is-active': activeTab === 'privacy' }" role="tab" :aria-selected="activeTab === 'privacy'" @tap="activeTab = 'privacy'">隐私政策</button>
      <button class="legal-tabs__item" :class="{ 'is-active': activeTab === 'agreement' }" role="tab" :aria-selected="activeTab === 'agreement'" @tap="activeTab = 'agreement'">用户协议</button>
    </view>
    <view class="legal-document">
      <view class="legal-document__meta">
        <text>{{ activeTab === 'privacy' ? '恒泰五金隐私政策' : '恒泰五金用户协议' }}</text>
        <text>更新日期：{{ updatedAt }}</text>
      </view>
      <view v-for="(section, index) in sections" :key="section.title" class="legal-section">
        <view class="legal-section__heading">
          <text class="legal-section__index">{{ String(index + 1).padStart(2, '0') }}</text>
          <text class="legal-section__title">{{ section.title }}</text>
        </view>
        <text v-for="paragraph in section.paragraphs" :key="paragraph" class="legal-section__paragraph">{{ paragraph }}</text>
        <view v-if="section.bullets" class="legal-section__list">
          <view v-for="item in section.bullets" :key="item" class="legal-section__list-item">
            <text class="legal-section__bullet" />
            <text>{{ item }}</text>
          </view>
        </view>
      </view>
      <text class="legal-document__note">本页面为当前 MVP 功能规则说明；正式上线前仍需结合实际主体信息、平台隐私保护指引与审核要求复核。</text>
    </view>
  </view>
</template>

<style scoped>
.legal-page { padding-top: 36rpx; }
.legal-hero { padding: 8rpx 4rpx 28rpx; }
.legal-tabs {
  display: flex;
  padding: 6rpx;
  border: 1rpx solid var(--line);
  border-radius: var(--radius-md);
  background: var(--surface-deep);
}
.legal-tabs__item { min-height: 76rpx; flex: 1; border-radius: 14rpx; color: var(--muted); font-size: 26rpx; font-weight: 600; }
.legal-tabs__item.is-active { color: var(--white); background: var(--brand-deep); }
.legal-document { margin-top: 24rpx; padding: 32rpx 28rpx; border-top: 5rpx solid var(--brand); background: var(--white); }
.legal-document__meta { display: flex; flex-direction: column; gap: 8rpx; padding-bottom: 28rpx; border-bottom: 1rpx solid var(--line); color: var(--muted); font-size: 22rpx; }
.legal-document__meta > text:first-child { color: var(--ink); font-size: 32rpx; font-weight: 700; }
.legal-section { padding: 30rpx 0; border-bottom: 1rpx solid var(--line); }
.legal-section__heading { display: flex; align-items: baseline; gap: 16rpx; margin-bottom: 18rpx; }
.legal-section__index { color: var(--brand); font-family: Arial, sans-serif; font-size: 21rpx; font-weight: 700; }
.legal-section__title { font-size: 29rpx; font-weight: 700; }
.legal-section__paragraph { display: block; margin-top: 12rpx; color: var(--ink-soft); font-size: 25rpx; line-height: 1.95; }
.legal-section__list { margin-top: 16rpx; }
.legal-section__list-item { display: flex; align-items: flex-start; gap: 14rpx; margin-top: 14rpx; color: var(--ink-soft); font-size: 24rpx; line-height: 1.85; }
.legal-section__bullet { width: 8rpx; height: 8rpx; flex: 0 0 auto; margin-top: 20rpx; background: var(--brand); }
.legal-document__note { display: block; padding-top: 26rpx; color: var(--muted); font-size: 21rpx; line-height: 1.8; }
</style>
