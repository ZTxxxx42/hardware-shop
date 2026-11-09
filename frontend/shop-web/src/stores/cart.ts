import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { cartApi } from '@/api/cart'
import type { CartItem, CartSummary } from '@/types/shop'

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const productAmount = ref('0')
  const freightAmount = ref('0')
  const totalAmount = ref('0')
  const loading = ref(false)

  const totalQuantity = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))

  function applySummary(summary: CartSummary) {
    items.value = summary.items
    productAmount.value = summary.product_amount
    freightAmount.value = summary.freight_amount
    totalAmount.value = summary.total_amount
  }

  function clear() {
    items.value = []
    productAmount.value = '0'
    freightAmount.value = '0'
    totalAmount.value = '0'
  }

  async function load() {
    loading.value = true
    try {
      applySummary(await cartApi.summary())
    } finally {
      loading.value = false
    }
  }

  async function add(productId: number, quantity = 1) {
    applySummary(await cartApi.addItem(productId, quantity))
  }

  async function updateQuantity(itemId: number, quantity: number) {
    applySummary(await cartApi.updateItem(itemId, quantity))
  }

  async function remove(itemId: number) {
    applySummary(await cartApi.removeItem(itemId))
  }

  return { items, productAmount, freightAmount, totalAmount, totalQuantity, loading, load, add, updateQuantity, remove, clear }
})
