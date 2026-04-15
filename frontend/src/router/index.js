import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/empresas',
      name: 'empresas-list',
      component: () => import('../views/empresas/EmpresaListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/empresa/configuracoes',
      name: 'empresa-config',
      component: () => import('../views/empresas/EmpresaConfigView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/empresas/:id/configuracoes',
      name: 'empresa-cliente-config',
      component: () => import('../views/empresas/EmpresaConfigView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/intake',
      name: 'intake',
      component: () => import('../views/intake/IntakeView.vue'),
      meta: { requiresAuth: true, requiresBackoffice: true }
    },
    {
      path: '/area_cliente/:slug',
      name: 'area-cliente',
      component: () => import('../views/intake/ClientPortalView.vue'),
      meta: { requiresAuth: true, requiresCliente: true, clientPortal: true }
    },
    {
      path: '/cadastros/clientes',
      name: 'clientes-list',
      component: () => import('../views/cadastros/ClienteListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cadastros/fornecedores',
      name: 'fornecedores-list',
      component: () => import('../views/cadastros/FornecedorListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/cadastros/produtos',
      name: 'produtos-list',
      component: () => import('../views/cadastros/ProdutoListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/fiscal/notas',
      name: 'notas-fiscais-list',
      component: () => import('../views/fiscal/NotaFiscalListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/financeiro/contas-pagar',
      name: 'contas-pagar-list',
      component: () => import('../views/financeiro/ContaAPagarListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/financeiro/contas-receber',
      name: 'contas-receber-list',
      component: () => import('../views/financeiro/ContaAReceberListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/financeiro/fluxo-caixa',
      name: 'fluxo-caixa',
      component: () => import('../views/financeiro/FluxoCaixaView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/folha/funcionarios',
      name: 'funcionarios-list',
      component: () => import('../views/folha/FuncionarioListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/folha/funcionarios/:id',
      name: 'funcionario-detail',
      component: () => import('../views/folha/FuncionarioDetailView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/folha/folha-pagamento',
      name: 'folha-pagamento-list',
      component: () => import('../views/folha/FolhaPagamentoListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/contabil/lancamentos',
      name: 'lancamentos-contabeis-list',
      component: () => import('../views/contabil/LancamentoContabilListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/contabil/dre',
      name: 'dre-report',
      component: () => import('../views/contabil/DREView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/contabil/balanco',
      name: 'balanco-patrimonial-report',
      component: () => import('../views/contabil/BalancoPatrimonialView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/obrigacoes/calendario',
      name: 'obrigacoes-list',
      component: () => import('../views/obrigacoes/ObrigacaoFiscalListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/estoque/movimentacoes',
      name: 'estoque-movimentacoes',
      component: () => import('../views/estoque/EstoqueMovimentacaoView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/estoque/posicao',
      name: 'estoque-posicao',
      component: () => import('../views/estoque/EstoquePosicaoView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/obrigacoes/guias',
      name: 'obrigacoes-guias',
      component: () => import('../views/obrigacoes/ObrigacaoGuiaView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/relatorios',
      name: 'relatorios',
      component: () => import('../views/RelatorioView.vue'),
      meta: { requiresAuth: true }
    },
    // Rotas para as outras seções (Empresas, Clientes, etc.)
    // Serão adicionadas conforme o desenvolvimento avança
  ]
})

// Navigation Guard para autenticação e perfil
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (!isAuthenticated) {
    return next()
  }

  // Lê perfil do localStorage (salvo no login)
  let perfil = null
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    perfil = user.perfil_empresa || null
  } catch (_) {}

  const isCliente = perfil === 'CLIENTE'

  // CLIENTE tentando acessar /login ou qualquer rota sem clientPortal → portal
  if (isCliente && to.name === 'login') {
    return next('/area_cliente/portal')
  }

  // CLIENTE tentando rota de backoffice → portal
  if (isCliente && to.meta.requiresBackoffice) {
    return next('/area_cliente/portal')
  }

  // CLIENTE na raiz (dashboard) → portal
  if (isCliente && to.name === 'dashboard') {
    return next('/area_cliente/portal')
  }

  // Backoffice no /login → dashboard
  if (!isCliente && to.name === 'login') {
    return next('/')
  }

  // Backoffice tentando rota de cliente → intake
  if (!isCliente && perfil !== null && to.meta.requiresCliente) {
    return next('/intake')
  }

  next()
})

export default router
