<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'

onLaunch(() => {
  uni.$on('auth:unauthorized', () => {
    const userStore = useUserStore()
    userStore.logout()
    useCartStore().clear()
    const pages = getCurrentPages()
    const current = pages[pages.length - 1]
    if (current && current.route && !current.route.startsWith('pages/login')) {
      uni.navigateTo({ url: '/pages/login/index' })
    }
  })
})
</script>

<style>
page {
  --brand: #1a6fd6;
  --brand-dark: #0c56ad;
  --brand-deep: #102b49;
  --brand-ink: #172f49;
  --brand-light: #eaf3ff;
  --sky: #48a8ee;
  --ink: #172434;
  --muted: #718094;
  --line: #e6ecf2;
  --surface: #f5f8fb;
  --white: #ffffff;
  --price: #e45b32;
  background: #f5f8fb;
  color: #172434;
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
  font-size: 28rpx;
  line-height: 1.6;
}

view, text, image, input, textarea, button, navigator {
  box-sizing: border-box;
}

button {
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  border-radius: 0;
  line-height: 1.6;
  font-size: inherit;
  color: inherit;
}

button::after {
  border: none;
}

input, textarea {
  color: #172434;
}

.page-shell {
  max-width: 560px;
  margin: 0 auto;
  padding: 24rpx 24rpx 40rpx;
}

.page-pad {
  padding: 24rpx 24rpx 40rpx;
}

.eyebrow {
  color: var(--brand);
  font-family: Arial, sans-serif;
  font-size: 20rpx;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.page-title {
  margin: 12rpx 0 4rpx;
  font-size: 44rpx;
  font-weight: 750;
  line-height: 1.3;
  letter-spacing: 0.02em;
}

.page-subtitle {
  color: #7b8998;
  font-size: 24rpx;
}

.price {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-weight: 700;
}

.price-mark {
  font-size: 22rpx;
  margin-right: 4rpx;
}

.section-card {
  margin-top: 24rpx;
  padding: 28rpx;
  border: 1rpx solid #e7edf3;
  border-radius: 20rpx;
  background: #ffffff;
  box-shadow: 0 10rpx 30rpx rgb(33 69 103 / 6%);
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.section-heading__title {
  display: flex;
  align-items: center;
  gap: 14rpx;
  font-size: 32rpx;
  font-weight: 700;
}

.section-heading__title::before {
  content: "";
  width: 8rpx;
  height: 32rpx;
  border-radius: 6rpx;
  background: var(--brand);
}

.section-heading__more {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  color: #69798b;
  font-size: 24rpx;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  min-height: 80rpx;
  padding: 0 32rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 1;
}

.btn::after {
  border: none;
}

.btn-primary {
  color: #ffffff;
  background: linear-gradient(110deg, #0c56ad, #2188e7);
  box-shadow: 0 12rpx 26rpx rgb(0 91 190 / 22%);
}

.btn-primary:active {
  filter: brightness(1.06);
}

.btn-ghost {
  color: var(--brand);
  border: 1rpx solid #bfd6f3;
  background: #f3f9ff;
}

.btn-danger {
  color: #ef5350;
  border: 1rpx solid #ffd4d2;
  background: #fff5f4;
}

.btn[disabled] {
  color: #b7c2cd;
  background: #eef2f6;
  box-shadow: none;
}

.card {
  background: #ffffff;
  border: 1rpx solid #e7edf3;
  border-radius: 18rpx;
  box-shadow: 0 8rpx 26rpx rgb(33 69 103 / 5%);
}
</style>
