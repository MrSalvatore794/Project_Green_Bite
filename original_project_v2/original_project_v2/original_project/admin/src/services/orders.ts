import { api } from './api'

export interface AdminOrderItem {
  product_id: number
  product_name: string
  unit_price: number
  quantity: number
  subtotal: number
}

export interface AdminOrderSummary {
  id: number
  user_id: number
  customer_name: string
  phone: string
  total_amount: number
  pickup_date: string
  pickup_time: string
  payment_reference: string
  status: string
  payment_status: string
  canceled_at: string | null
  created_at: string
  items: AdminOrderItem[]
}

export interface AdminOrder extends AdminOrderSummary {
  payment_reference_type: string
}

interface OrdersResponse {
  orders: AdminOrderSummary[]
}

interface OrderResponse {
  order: AdminOrder
}

export function fetchOrders(): Promise<AdminOrderSummary[]> {
  return api.get<OrdersResponse>('/admin/orders').then((data) => data.orders)
}

export function fetchOrder(id: number): Promise<AdminOrder> {
  return api.get<OrderResponse>(`/admin/orders/${id}`).then((data) => data.order)
}

export function updateOrderStatus(id: number, status: string): Promise<AdminOrder> {
  return api
    .patch<OrderResponse>(`/admin/orders/${id}/status`, { status })
    .then((data) => data.order)
}

export function updatePaymentStatus(id: number, paymentStatus: string): Promise<AdminOrder> {
  return api
    .patch<OrderResponse>(`/admin/orders/${id}/payment-status`, {
      payment_status: paymentStatus,
    })
    .then((data) => data.order)
}