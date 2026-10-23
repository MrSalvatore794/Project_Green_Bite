import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Hide the bottom navigation on this route (e.g. entry screens). */
    hideNav?: boolean
    /** Constrain this route to the viewport height (no vertical scrolling). */
    noScroll?: boolean
  }
}
