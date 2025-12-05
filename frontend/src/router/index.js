import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import RegistrationPage from '../pages/RegistrationPage.vue'
import AppSelectorPage from '../pages/AppSelectorPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import OrdersPage from '../pages/OrdersPage.vue'
import PortfoliosPage from '../pages/PortfoliosPage.vue'
import PositionsPage from '../pages/PositionsPage.vue'
import StrategyListPage from '../pages/StrategyListPage.vue'
import StrategyDetailPage from '../pages/StrategyDetailPage.vue'
import SettingsPage from '../pages/SettingsPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'Register',
    component: RegistrationPage
  },
  {
    path: '/apps',
    name: 'AppSelector',
    component: AppSelectorPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage
  },
  {
    path: '/orders',
    name: 'Orders',
    component: OrdersPage
  },
  {
    path: '/portfolios',
    name: 'Portfolios',
    component: PortfoliosPage
  },
  {
    path: '/positions',
    name: 'Positions',
    component: PositionsPage
  },
  {
    path: '/strategies',
    name: 'StrategyList',
    component: StrategyListPage
  },
  {
    path: '/strategies/:id',
    name: 'StrategyDetail',
    component: StrategyDetailPage
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

