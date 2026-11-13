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
  --ink: #172434;
  --ink-soft: #3c4e61;
  --muted: #718094;
  --placeholder: #a0abb7;
  --line: #e6ecf2;
  --line-dark: #d4deea;
  --surface: #f5f8fb;
  --surface-deep: #eaf0f6;
  --white: #ffffff;
  --price: #e45b32;
  --success: #1d7a44;
  --success-light: #e4f4ea;
  --warning: #c98a2e;
  --warning-light: #fbf0dc;
  --danger: #c93a2a;
  --danger-light: #fbe9e5;
  --radius-sm: 12rpx;
  --radius-md: 20rpx;
  --radius-lg: 28rpx;
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
  padding: 24rpx 24rpx calc(40rpx + env(safe-area-inset-bottom));
}

.page-pad {
  padding: 24rpx 24rpx calc(40rpx + env(safe-area-inset-bottom));
}

.eyebrow {
  color: var(--brand-dark);
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
  color: var(--muted);
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
  border: 1rpx solid var(--line);
  border-radius: var(--radius-md);
  background: var(--white);
  box-shadow: 0 10rpx 30rpx rgb(27 62 96 / 5%);
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
  color: var(--muted);
  font-size: 24rpx;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  min-height: 80rpx;
  padding: 0 32rpx;
  border-radius: var(--radius-sm);
  font-size: 28rpx;
  font-weight: 600;
  line-height: 1;
}

.btn::after {
  border: none;
}

.btn-primary {
  color: #ffffff;
  background: var(--brand);
  box-shadow: 0 12rpx 26rpx rgb(12 86 173 / 22%);
}

.btn-primary:active {
  filter: brightness(1.06);
}

.btn-ghost {
  color: var(--brand-dark);
  border: 1rpx solid #bfd6f3;
  background: var(--brand-light);
}

.btn-danger {
  color: var(--danger);
  border: 1rpx solid #f3c4bb;
  background: var(--danger-light);
}

.btn[disabled] {
  color: #aab6c4;
  background: var(--surface-deep);
  box-shadow: none;
}

.card {
  background: var(--white);
  border: 1rpx solid var(--line);
  border-radius: var(--radius-md);
  box-shadow: 0 8rpx 26rpx rgb(27 62 96 / 4%);
}
</style>
