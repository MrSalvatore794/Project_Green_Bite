import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Require an authenticated Admin user for this route. */
    requiresAdmin?: boolean
  }
}