import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface CartLine {
  productId: number
  quantity: number
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartLine[]>([])
  const totalQuantity = computed(() => items.value.reduce((sum, item) => sum + item.quantity, 0))

  function addItem(productId: number, quantity = 1) {
    const line = items.value.find((item) => item.productId === productId)
    if (line) line.quantity += quantity
    else items.value.push({ productId, quantity })
  }

  function clear() {
    items.value = []
  }

  return { items, totalQuantity, addItem, clear }
})
