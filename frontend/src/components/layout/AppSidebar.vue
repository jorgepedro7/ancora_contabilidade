<script setup>
import { RouterLink } from 'vue-router'
import { useEmpresaStore } from '@/stores/empresa'

const empresaStore = useEmpresaStore()

const menuItems = [
  { name: 'Dashboard', icon: '📊', path: '/' },
  { name: 'Empresas', icon: '🏢', path: '/empresas', requiresEmpresa: false },
  { name: 'Cadastros', icon: '📝', children: [
    { name: 'Clientes', icon: '👥', path: '/cadastros/clientes' },
    { name: 'Fornecedores', icon: '🚚', path: '/cadastros/fornecedores' },
    { name: 'Produtos', icon: '📦', path: '/cadastros/produtos' },
  ], requiresEmpresa: true },
  { name: 'Fiscal', icon: '🧾', children: [
    { name: 'Notas Fiscais', icon: '📄', path: '/fiscal/notas' },
  ], requiresEmpresa: true },
  { name: 'Financeiro', icon: '💰', children: [
    { name: 'Contas a Pagar', icon: '💸', path: '/financeiro/contas-pagar' },
    { name: 'Contas a Receber', icon: '💵', path: '/financeiro/contas-receber' },
    { name: 'Fluxo de Caixa', icon: '📈', path: '/financeiro/fluxo-caixa' },
  ], requiresEmpresa: true },
  { name: 'Estoque', icon: '📦', children: [
    { name: 'Movimentações', icon: '🔄', path: '/estoque/movimentacoes' },
    { name: 'Posição Atual', icon: '📍', path: '/estoque/posicao' },
  ], requiresEmpresa: true },
  { name: 'Folha de Pagamento', icon: '👨‍👩‍👧‍👦', children: [
    { name: 'Funcionários', icon: '🧑‍💼', path: '/folha/funcionarios' },
    { name: 'Gerar Folha', icon: '📝', path: '/folha/folha-pagamento' },
  ], requiresEmpresa: true },
  { name: 'Contábil', icon: '📚', children: [
    { name: 'Lançamentos', icon: '✏️', path: '/contabil/lancamentos' },
    { name: 'DRE', icon: '📊', path: '/contabil/dre' },
    { name: 'Balanço', icon: '⚖️', path: '/contabil/balanco' },
  ], requiresEmpresa: true },
  { name: 'Obrigações', icon: '📆', children: [
    { name: 'Calendário Fiscal', icon: '🗓️', path: '/obrigacoes/calendario' },
    { name: 'Guias', icon: '🧾', path: '/obrigacoes/guias' },
  ], requiresEmpresa: true },
  { name: 'Relatórios', icon: '📈', path: '/relatorios', requiresEmpresa: true },
]

function isItemVisible(item) {
  if (item.requiresEmpresa && !empresaStore.activeEmpresa) {
    return false
  }
  return true
}
</script>

<template>
  <aside class="w-64 bg-ancora-black/90 p-4 border-r border-ancora-navy shadow-lg">
    <nav>
      <ul>
        <li v-for="item in menuItems" :key="item.name" class="mb-2">
          <template v-if="isItemVisible(item)">
            <RouterLink
              v-if="item.path"
              :to="item.path"
              class="flex items-center p-2 rounded-md text-gray-300 hover:bg-ancora-navy hover:text-ancora-gold transition-colors"
              active-class="bg-ancora-navy text-ancora-gold border-l-4 border-ancora-gold"
            >
              <span class="mr-3">{{ item.icon }}</span>
              <span>{{ item.name }}</span>
            </RouterLink>
            <details v-else class="group">
              <summary class="flex items-center p-2 rounded-md text-gray-300 hover:bg-ancora-navy hover:text-ancora-gold cursor-pointer transition-colors">
                <span class="mr-3">{{ item.icon }}</span>
                <span>{{ item.name }}</span>
              </summary>
              <ul class="ml-6 mt-1 border-l border-ancora-gold/30">
                <li v-for="subItem in item.children" :key="subItem.name">
                  <RouterLink
                    :to="subItem.path"
                    class="flex items-center p-2 rounded-md text-gray-300 hover:bg-ancora-navy hover:text-ancora-gold transition-colors"
                    active-class="bg-ancora-navy text-ancora-gold border-l-4 border-ancora-gold"
                  >
                    <span class="mr-3">{{ subItem.icon }}</span>
                    <span>{{ subItem.name }}</span>
                  </RouterLink>
                </li>
              </ul>
            </details>
          </template>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
/* Estilos específicos do sidebar aqui */
</style>
