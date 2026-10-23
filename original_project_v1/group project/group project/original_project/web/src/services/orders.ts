import { api } from './api'

export interface OrderItem {
  product_id: number
  product_name: string
  unit_price: number
  quantity: number
  subtotal: number
}

export interface Order {
  id: number
  customer_name: string
  phone: string
  pickup_date: string
  pickup_time: string
  payment_reference_type: string
  payment_reference: string
  total_amount: number
  status: string
  payment_status: string
  items: OrderItem[]
}

export interface OrderSummary {
  id: number
  user_id: number
  total_amount: number
  pickup_date: string
  pickup_time: string
  status: string
  payment_status: string
  created_at: string
  items: OrderItem[]
}

export interface CreateOrderPayload {
  customer_name: string
  phone: string
  pickup_date: string
  pickup_time: string
  payment_reference_type: string
  payment_reference: string
}

interface OrderResponse {
  order: Order
}

export function createOrder(payload: CreateOrderPayload): Promise<Order> {
  return api.post<OrderResponse>('/orders', payload).then((data) => data.order)
}

export function fetchOrder(id: number): Promise<Order> {
  return api.get<OrderResponse>(`/orders/${id}`).then((data) => data.order)
}

interface OrdersResponse {
  orders: OrderSummary[]
}

export function fetchOrders(): Promise<OrderSummary[]> {
  return api.get<OrdersResponse>('/orders').then((data) => data.orders)
}
