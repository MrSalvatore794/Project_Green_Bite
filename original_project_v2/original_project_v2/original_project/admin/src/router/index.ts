import { createRouter, createWebHistory } from 'vue-router'
import AdminLayout from '../layouts/AdminLayout.vue'
import AdminLoginView from '../views/AdminLoginView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import AdminProductsView from '../views/AdminProductsView.vue'
import AdminOrdersView from '../views/AdminOrdersView.vue'
import AdminUsersView from '../views/AdminUsersView.vue'
import { useAdminAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/admin' },
    { path: '/admin/login', name: 'admin-login', component: AdminLoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAdmin: true },
      children: [
        { path: '', name: 'admin-dashboard', component: AdminDashboardView },
        { path: 'products', name: 'admin-products', component: AdminProductsView },
        { path: 'orders', name: 'admin-orders', component: AdminOrdersView },
        { path: 'users', name: 'admin-users', component: AdminUsersView },
      ],
    },
  ],
})

// Frontend route guard (UX only — the Flask API is the real security boundary).
router.beforeEach(async (to) => {
  if (!to.meta.requiresAdmin) return true

  const auth = useAdminAuthStore()
  if (!auth.state.token) {
    return { path: '/admin/login', query: { redirect: to.fullPath } }
  }

  // On a hard refresh the user object may still be loading; fetch it first.
  let user = auth.state.user
  if (!user) {
    try {
      await auth.loadCurrentUser()
      user = auth.state.user
    } catch {
      auth.logout()
      return { path: '/admin/login', query: { redirect: to.fullPath } }
    }
  }

  if (!user || user.role !== 'admin') {
    return { path: '/admin/login' }
  }

  return true
})

export default router