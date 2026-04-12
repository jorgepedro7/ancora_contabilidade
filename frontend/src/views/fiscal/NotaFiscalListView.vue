<template>
  <div class="p-4">
    <!-- Cabeçalho da página -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-display text-ancora-gold mb-1">Notas Fiscais</h1>
        <p class="text-sm text-gray-400">Emissão e gestão de NF-e da empresa ativa.</p>
      </div>
      <button @click="openCreateModal"
              class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors">
        + Nova NF-e
      </button>
    </div>

    <!-- Filtros -->
    <div class="mb-4 flex flex-wrap gap-3 items-center">
      <input type="text" v-model="searchQuery" @input="fetchNotasFiscais"
             placeholder="Número, chave ou destinatário..."
             class="flex-1 min-w-48 px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
      <select v-model="filterStatus" @change="fetchNotasFiscais"
              class="px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
        <option value="">Todos os status</option>
        <option value="RASCUNHO">Rascunho</option>
        <option value="AUTORIZADA">Autorizada</option>
        <option value="REJEITADA">Rejeitada</option>
        <option value="CANCELADA">Cancelada</option>
        <option value="PENDENTE">Pendente</option>
      </select>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-8">Carregando notas fiscais...</div>
    <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

    <div v-if="notasFiscais.length > 0" class="overflow-x-auto rounded-lg shadow-md">
      <table class="min-w-full bg-ancora-black/50 text-white">
        <thead>
          <tr class="bg-ancora-navy text-ancora-gold uppercase text-sm leading-normal">
            <th class="py-3 px-4 text-left">Número/Série</th>
            <th class="py-3 px-4 text-left">Tipo</th>
            <th class="py-3 px-4 text-left">Destinatário</th>
            <th class="py-3 px-4 text-left">Status</th>
            <th class="py-3 px-4 text-right">Valor Total</th>
            <th class="py-3 px-4 text-left">Emissão</th>
            <th class="py-3 px-4 text-center">Ações</th>
          </tr>
        </thead>
        <tbody class="text-gray-300 text-sm font-body">
          <tr v-for="nf in notasFiscais" :key="nf.id" class="border-b border-ancora-navy hover:bg-ancora-black/70">
            <td class="py-3 px-4 whitespace-nowrap">
              <div class="font-mono font-bold">{{ nf.numero }}/{{ nf.serie }}</div>
              <div v-if="nf.chave_acesso" class="text-[10px] text-gray-500 truncate max-w-[120px]">{{ nf.chave_acesso }}</div>
            </td>
            <td class="py-3 px-4">{{ nf.tipo_nf_display }}</td>
            <td class="py-3 px-4">
              <div>{{ nf.destinatario_nome }}</div>
              <div class="text-xs text-gray-500">{{ formatDoc(nf.destinatario_documento) }}</div>
            </td>
            <td class="py-3 px-4">
              <span :class="statusClass(nf.status)" class="px-2 py-0.5 rounded-full text-xs font-semibold text-white">
                {{ nf.status_display }}
              </span>
            </td>
            <td class="py-3 px-4 text-right font-mono">{{ formatCurrency(nf.valor_total_nf) }}</td>
            <td class="py-3 px-4 text-sm">{{ formatDate(nf.data_emissao) }}</td>
            <td class="py-3 px-4 text-center whitespace-nowrap">
              <button @click="openEditModal(nf)" class="text-ancora-gold hover:text-ancora-gold/80 font-bold mr-2">Abrir</button>
              <button v-if="nf.status === 'RASCUNHO' || nf.status === 'REJEITADA'"
                      @click="openAutorizarModal(nf)"
                      class="text-green-400 hover:text-green-300 font-bold mr-2">Autorizar</button>
              <button v-if="nf.status === 'AUTORIZADA'"
                      @click="openCancelarModal(nf)"
                      class="text-orange-400 hover:text-orange-300 font-bold mr-2">Cancelar</button>
              <button v-if="nf.status === 'AUTORIZADA'"
                      @click="downloadDanfe(nf.id)"
                      class="text-blue-400 hover:text-blue-300 font-bold mr-2">DANFE</button>
              <button v-if="nf.status === 'RASCUNHO'"
                      @click="openDeleteModal(nf)"
                      class="text-red-500 hover:text-red-400 font-bold">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!loading && !error" class="text-center text-gray-400 mt-8">
      Nenhuma nota fiscal encontrada.
    </div>

    <!-- ===================== MODAL PRINCIPAL (cabeçalho + itens) ===================== -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ancora-black/80 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-4xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/90 shadow-xl">

        <!-- Header do modal -->
        <div class="flex items-center justify-between p-6 border-b border-ancora-gold/20">
          <div>
            <h2 class="text-2xl font-display text-ancora-gold">
              {{ currentNF.id ? `NF ${currentNF.numero}/${currentNF.serie}` : 'Nova Nota Fiscal' }}
            </h2>
            <span v-if="currentNF.id" :class="statusClass(currentNF.status)" class="text-xs px-2 py-0.5 rounded-full font-semibold text-white mt-1 inline-block">
              {{ currentNF.status_display || currentNF.status }}
            </span>
          </div>
          <button @click="closeModal" class="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
        </div>

        <!-- Abas -->
        <div class="flex border-b border-ancora-gold/20">
          <button @click="activeTab = 'cabecalho'"
                  :class="activeTab === 'cabecalho' ? 'border-b-2 border-ancora-gold text-ancora-gold' : 'text-gray-400 hover:text-gray-200'"
                  class="px-6 py-3 text-sm font-semibold transition-colors">
            Cabeçalho
          </button>
          <button @click="activeTab = 'itens'" :disabled="!currentNF.id"
                  :class="[
                    activeTab === 'itens' ? 'border-b-2 border-ancora-gold text-ancora-gold' : 'text-gray-400 hover:text-gray-200',
                    !currentNF.id ? 'opacity-40 cursor-not-allowed' : ''
                  ]"
                  class="px-6 py-3 text-sm font-semibold transition-colors">
            Itens {{ currentNF.id ? `(${itens.length})` : '' }}
          </button>
        </div>

        <!-- Aba Cabeçalho -->
        <div v-show="activeTab === 'cabecalho'" class="p-6">
          <form @submit.prevent="saveNF" class="space-y-5">

            <!-- Tipo e finalidade -->
            <p class="text-xs uppercase tracking-wide text-gray-500">Identificação</p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">Tipo de NF *</label>
                <select v-model="nfForm.tipo_nf" required :disabled="isNFReadOnly"
                        class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60">
                  <option value="1">NF-e (Modelo 55)</option>
                  <option value="2">NFC-e (Modelo 65)</option>
                </select>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Finalidade *</label>
                <select v-model="nfForm.finalidade" required :disabled="isNFReadOnly"
                        class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60">
                  <option value="1">Normal</option>
                  <option value="2">Complementar</option>
                  <option value="3">Ajuste</option>
                  <option value="4">Devolução de Mercadoria</option>
                </select>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Modalidade de Frete</label>
                <select v-model="nfForm.modalidade_frete" :disabled="isNFReadOnly"
                        class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60">
                  <option value="0">Emitente</option>
                  <option value="1">Destinatário</option>
                  <option value="2">Terceiros</option>
                  <option value="3">Próprio (emitente)</option>
                  <option value="4">Próprio (destinatário)</option>
                  <option value="9">Sem frete</option>
                </select>
              </div>
            </div>

            <!-- Destinatário -->
            <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Destinatário</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block text-sm text-gray-300 mb-1">Nome / Razão Social *</label>
                <input type="text" v-model="nfForm.destinatario_nome" required :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">CPF / CNPJ *</label>
                <input type="text" v-model="nfForm.destinatario_documento" required :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Inscrição Estadual</label>
                <input type="text" v-model="nfForm.destinatario_ie" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">E-mail</label>
                <input type="email" v-model="nfForm.destinatario_email" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
            </div>

            <!-- Endereço -->
            <p class="text-xs uppercase tracking-wide text-gray-500 pt-2">Endereço do Destinatário</p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm text-gray-300 mb-1">CEP *</label>
                <div class="flex gap-2">
                  <input type="text" v-model="nfForm.destinatario_cep" maxlength="9" :disabled="isNFReadOnly"
                         placeholder="00000-000"
                         class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
                  <button v-if="!isNFReadOnly" type="button" @click="buscarCep" :disabled="cepLoading"
                          class="px-3 py-2 bg-ancora-navy border border-ancora-gold/40 rounded-md text-ancora-gold text-sm hover:bg-ancora-gold/10 whitespace-nowrap disabled:opacity-50">
                    {{ cepLoading ? '...' : 'Buscar' }}
                  </button>
                </div>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm text-gray-300 mb-1">Logradouro *</label>
                <input type="text" v-model="nfForm.destinatario_logradouro" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Número *</label>
                <input type="text" v-model="nfForm.destinatario_numero" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Complemento</label>
                <input type="text" v-model="nfForm.destinatario_complemento" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Bairro *</label>
                <input type="text" v-model="nfForm.destinatario_bairro" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">Município *</label>
                <input type="text" v-model="nfForm.destinatario_municipio" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
              <div>
                <label class="block text-sm text-gray-300 mb-1">UF *</label>
                <input type="text" v-model="nfForm.destinatario_uf" maxlength="2" :disabled="isNFReadOnly"
                       class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm disabled:opacity-60"/>
              </div>
            </div>

            <div v-if="!isNFReadOnly" class="flex justify-end gap-3 pt-2">
              <button type="button" @click="closeModal"
                      class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
              <button type="submit" :disabled="saving"
                      class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 transition-colors disabled:opacity-50">
                {{ saving ? 'Salvando...' : (currentNF.id ? 'Atualizar Cabeçalho' : 'Criar Rascunho e Adicionar Itens →') }}
              </button>
            </div>
          </form>
        </div>

        <!-- Aba Itens -->
        <div v-show="activeTab === 'itens'" class="p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-sm text-gray-400">
                Total: <span class="text-white font-bold">{{ formatCurrency(currentNF.valor_total_nf || 0) }}</span>
                · Produtos: <span class="text-white">{{ formatCurrency(currentNF.valor_produtos || 0) }}</span>
              </p>
            </div>
            <button v-if="!isNFReadOnly" @click="openItemForm(null)"
                    class="px-3 py-1.5 bg-ancora-gold text-ancora-black text-sm font-bold rounded hover:bg-ancora-gold/90">
              + Adicionar Item
            </button>
          </div>

          <div v-if="loadingItens" class="text-gray-400 text-sm">Carregando itens...</div>

          <div v-else-if="itens.length > 0" class="overflow-x-auto rounded-lg">
            <table class="min-w-full text-sm text-white">
              <thead>
                <tr class="bg-ancora-navy text-ancora-gold uppercase text-xs">
                  <th class="py-2 px-3 text-left">Descrição</th>
                  <th class="py-2 px-3 text-left">NCM</th>
                  <th class="py-2 px-3 text-left">CFOP</th>
                  <th class="py-2 px-3 text-right">Qtd</th>
                  <th class="py-2 px-3 text-right">Vl. Unit.</th>
                  <th class="py-2 px-3 text-right">Desconto</th>
                  <th class="py-2 px-3 text-right">Total</th>
                  <th v-if="!isNFReadOnly" class="py-2 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody class="text-gray-300">
                <tr v-for="item in itens" :key="item.id" class="border-b border-ancora-navy hover:bg-ancora-black/60">
                  <td class="py-2 px-3">{{ item.produto_descricao }}</td>
                  <td class="py-2 px-3 font-mono">{{ item.produto_ncm }}</td>
                  <td class="py-2 px-3 font-mono">{{ item.produto_cfop }}</td>
                  <td class="py-2 px-3 text-right">{{ item.quantidade }}</td>
                  <td class="py-2 px-3 text-right font-mono">{{ formatCurrency(item.valor_unitario) }}</td>
                  <td class="py-2 px-3 text-right font-mono">{{ formatCurrency(item.valor_desconto_item) }}</td>
                  <td class="py-2 px-3 text-right font-mono font-bold">{{ formatCurrency(item.valor_total) }}</td>
                  <td v-if="!isNFReadOnly" class="py-2 px-3 text-center whitespace-nowrap">
                    <button @click="openItemForm(item)" class="text-ancora-gold hover:text-ancora-gold/80 mr-2 text-xs font-bold">Editar</button>
                    <button @click="openDeleteItemModal(item)" class="text-red-500 hover:text-red-400 text-xs font-bold">Remover</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center text-gray-500 py-6 text-sm">
            Nenhum item adicionado. Clique em "+ Adicionar Item" para começar.
          </div>

          <div class="flex justify-end mt-4">
            <button @click="closeModal" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== MODAL: Formulário de Item ===================== -->
    <div v-if="itemModal.open" class="fixed inset-0 z-[60] flex items-center justify-center overflow-y-auto bg-ancora-black/80 p-4">
      <div class="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-lg border border-ancora-gold/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-ancora-gold mb-4">{{ itemModal.editingId ? 'Editar Item' : 'Adicionar Item' }}</h3>
        <form @submit.prevent="saveItem" class="space-y-4">

          <!-- Selecionar produto do catálogo -->
          <div>
            <label class="block text-sm text-gray-300 mb-1">Produto do Catálogo (opcional)</label>
            <select v-model="itemForm.produto" @change="preencherProduto"
                    class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm">
              <option :value="null">— Digitar manualmente —</option>
              <option v-for="p in produtos" :key="p.id" :value="p.id">{{ p.descricao }} ({{ p.codigo_interno || p.ncm }})</option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm text-gray-300 mb-1">Descrição *</label>
              <input type="text" v-model="itemForm.produto_descricao" required
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">NCM *</label>
              <input type="text" v-model="itemForm.produto_ncm" required maxlength="8"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CFOP *</label>
              <input type="text" v-model="itemForm.produto_cfop" required maxlength="4"
                     placeholder="5102"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">CEST</label>
              <input type="text" v-model="itemForm.produto_cest" maxlength="7"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">EAN / GTIN</label>
              <input type="text" v-model="itemForm.produto_ean" maxlength="14"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <!-- Quantidades e valores -->
          <p class="text-xs uppercase tracking-wide text-gray-500">Valores</p>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">Quantidade *</label>
              <input type="number" v-model="itemForm.quantidade" required step="0.0001" min="0.0001"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Valor Unitário (R$) *</label>
              <input type="number" v-model="itemForm.valor_unitario" required step="0.01" min="0"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">Desconto (R$)</label>
              <input type="number" v-model="itemForm.valor_desconto_item" step="0.01" min="0"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>
          <div class="text-right text-sm text-gray-400">
            Total do item: <span class="text-ancora-gold font-bold text-base">{{ formatCurrency(calcItemTotal) }}</span>
          </div>

          <!-- Impostos (simplificado) -->
          <p class="text-xs uppercase tracking-wide text-gray-500">Impostos (simplificado)</p>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm text-gray-300 mb-1">ICMS CST/CSOSN</label>
              <input type="text" v-model="itemForm.icms_cst_csosn" maxlength="3"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">ICMS Alíq. (%)</label>
              <input type="number" v-model="itemForm.icms_aliquota" step="0.01" min="0"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">PIS CST</label>
              <input type="text" v-model="itemForm.pis_cst" maxlength="2"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
            <div>
              <label class="block text-sm text-gray-300 mb-1">COFINS CST</label>
              <input type="text" v-model="itemForm.cofins_cst" maxlength="2"
                     class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white sm:text-sm"/>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="itemModal.open = false"
                    class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors">Cancelar</button>
            <button type="submit" :disabled="savingItem"
                    class="px-4 py-2 bg-ancora-gold text-ancora-black font-bold rounded-md hover:bg-ancora-gold/90 disabled:opacity-50">
              {{ savingItem ? 'Salvando...' : 'Salvar Item' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===================== MODAL: Autorizar ===================== -->
    <div v-if="autorizarModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-green-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-green-400 mb-2">Autorizar Nota Fiscal</h3>
        <p class="text-sm text-gray-300 mb-4">
          Enviar a NF <span class="font-bold text-white">{{ autorizarModal.numero }}/{{ autorizarModal.serie }}</span> para autorização na SEFAZ?
          Esta ação não pode ser desfeita facilmente.
        </p>
        <div class="flex justify-end gap-3">
          <button @click="autorizarModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarAutorizar" :disabled="saving"
                  class="px-4 py-2 bg-green-600 text-white font-bold rounded-md hover:bg-green-700 disabled:opacity-50">
            {{ saving ? 'Enviando...' : 'Sim, Autorizar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===================== MODAL: Cancelar ===================== -->
    <div v-if="cancelarModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-orange-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-orange-400 mb-2">Cancelar Nota Fiscal</h3>
        <p class="text-sm text-gray-300 mb-3">
          NF <span class="font-bold text-white">{{ cancelarModal.numero }}/{{ cancelarModal.serie }}</span>.
          Informe a justificativa (mínimo 15 caracteres):
        </p>
        <textarea v-model="cancelarModal.justificativa" rows="3"
                  class="block w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white text-sm mb-4"
                  placeholder="Justificativa do cancelamento..."></textarea>
        <div class="flex justify-end gap-3">
          <button @click="cancelarModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarCancelar" :disabled="saving || cancelarModal.justificativa.length < 15"
                  class="px-4 py-2 bg-orange-600 text-white font-bold rounded-md hover:bg-orange-700 disabled:opacity-50">
            {{ saving ? 'Cancelando...' : 'Confirmar Cancelamento' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===================== MODAL: Excluir NF ===================== -->
    <div v-if="deleteNFModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-red-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-red-400 mb-2">Excluir Rascunho</h3>
        <p class="text-sm text-gray-300 mb-4">
          Excluir o rascunho NF <span class="font-bold text-white">{{ deleteNFModal.numero }}/{{ deleteNFModal.serie }}</span>?
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deleteNFModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarDeleteNF" :disabled="saving"
                  class="px-4 py-2 bg-red-600 text-white font-bold rounded-md hover:bg-red-700 disabled:opacity-50">
            {{ saving ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ===================== MODAL: Excluir Item ===================== -->
    <div v-if="deleteItemModal.open" class="fixed inset-0 z-[60] flex items-center justify-center bg-ancora-black/80 p-4">
      <div class="w-full max-w-md rounded-lg border border-red-500/30 bg-ancora-black/95 p-6 shadow-xl">
        <h3 class="text-lg font-display text-red-400 mb-2">Remover Item</h3>
        <p class="text-sm text-gray-300 mb-4">
          Remover <span class="font-bold text-white">{{ deleteItemModal.descricao }}</span> da nota fiscal?
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deleteItemModal.open = false" class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700">Cancelar</button>
          <button @click="confirmarDeleteItem" :disabled="savingItem"
                  class="px-4 py-2 bg-red-600 text-white font-bold rounded-md hover:bg-red-700 disabled:opacity-50">
            {{ savingItem ? 'Removendo...' : 'Remover' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUiStore } from '@/stores/ui'
import FiscalService from '@/services/fiscal.service'
import EmpresasService from '@/services/empresas.service'
import CadastrosService from '@/services/cadastros.service'
import { extractApiErrorMessage } from '@/utils/api'

const uiStore = useUiStore()

// Lista principal
const notasFiscais = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const filterStatus = ref('')

// Modal principal
const isModalOpen = ref(false)
const activeTab = ref('cabecalho')
const saving = ref(false)
const cepLoading = ref(false)
const currentNF = ref({})

const emptyNFForm = () => ({
  tipo_nf: '1',
  finalidade: '1',
  modalidade_frete: '9',
  destinatario_nome: '',
  destinatario_documento: '',
  destinatario_ie: '',
  destinatario_email: '',
  destinatario_cep: '',
  destinatario_logradouro: '',
  destinatario_numero: '',
  destinatario_complemento: '',
  destinatario_bairro: '',
  destinatario_municipio: '',
  destinatario_uf: '',
})

const nfForm = reactive(emptyNFForm())

const isNFReadOnly = computed(() => {
  if (!currentNF.value.id) return false
  return !['RASCUNHO', 'REJEITADA'].includes(currentNF.value.status)
})

// Itens
const itens = ref([])
const loadingItens = ref(false)
const savingItem = ref(false)
const produtos = ref([])

const emptyItemForm = () => ({
  produto: null,
  produto_descricao: '',
  produto_ncm: '',
  produto_cest: '',
  produto_cfop: '',
  produto_ean: '',
  quantidade: 1,
  valor_unitario: 0,
  valor_desconto_item: 0,
  icms_cst_csosn: '',
  icms_aliquota: 0,
  pis_cst: '',
  cofins_cst: '',
})

const itemModal = reactive({ open: false, editingId: null })
const itemForm = reactive(emptyItemForm())

const calcItemTotal = computed(() => {
  const total = (Number(itemForm.quantidade) * Number(itemForm.valor_unitario)) - Number(itemForm.valor_desconto_item)
  return isNaN(total) ? 0 : total
})

// Modais de confirmação
const autorizarModal = reactive({ open: false, id: null, numero: '', serie: '' })
const cancelarModal = reactive({ open: false, id: null, numero: '', serie: '', justificativa: '' })
const deleteNFModal = reactive({ open: false, id: null, numero: '', serie: '' })
const deleteItemModal = reactive({ open: false, id: null, notaId: null, descricao: '' })

onMounted(() => {
  fetchNotasFiscais()
  loadProdutos()
})

async function fetchNotasFiscais() {
  loading.value = true
  error.value = null
  try {
    const params = { search: searchQuery.value }
    if (filterStatus.value) params.status = filterStatus.value
    const response = await FiscalService.getNotasFiscais(params)
    notasFiscais.value = response.results
  } catch (err) {
    error.value = 'Falha ao carregar notas fiscais.'
    uiStore.showNotification(error.value, 'error')
  } finally {
    loading.value = false
  }
}

async function loadProdutos() {
  try {
    const resp = await CadastrosService.getProdutos({ page_size: 200 })
    produtos.value = resp.results || []
  } catch { /* silencioso */ }
}

async function loadItens(nfId) {
  loadingItens.value = true
  try {
    const resp = await FiscalService.getItens(nfId)
    itens.value = resp.results || resp
  } catch {
    uiStore.showNotification('Erro ao carregar itens.', 'error')
  } finally {
    loadingItens.value = false
  }
}

function openCreateModal() {
  currentNF.value = {}
  Object.assign(nfForm, emptyNFForm())
  itens.value = []
  activeTab.value = 'cabecalho'
  isModalOpen.value = true
}

function openEditModal(nf) {
  currentNF.value = { ...nf }
  Object.assign(nfForm, emptyNFForm(), {
    tipo_nf: nf.tipo_nf,
    finalidade: nf.finalidade,
    modalidade_frete: nf.modalidade_frete,
    destinatario_nome: nf.destinatario_nome,
    destinatario_documento: nf.destinatario_documento,
    destinatario_ie: nf.destinatario_ie || '',
    destinatario_email: nf.destinatario_email || '',
    destinatario_cep: nf.destinatario_cep || '',
    destinatario_logradouro: nf.destinatario_logradouro || '',
    destinatario_numero: nf.destinatario_numero || '',
    destinatario_complemento: nf.destinatario_complemento || '',
    destinatario_bairro: nf.destinatario_bairro || '',
    destinatario_municipio: nf.destinatario_municipio || '',
    destinatario_uf: nf.destinatario_uf || '',
  })
  activeTab.value = 'cabecalho'
  isModalOpen.value = true
  loadItens(nf.id)
}

function closeModal() {
  isModalOpen.value = false
}

async function buscarCep() {
  const cep = (nfForm.destinatario_cep || '').replace(/\D/g, '')
  if (cep.length !== 8) { uiStore.showNotification('CEP inválido.', 'warning'); return }
  cepLoading.value = true
  try {
    const data = await EmpresasService.buscarCep(cep)
    nfForm.destinatario_logradouro = data.logradouro || nfForm.destinatario_logradouro
    nfForm.destinatario_bairro = data.bairro || nfForm.destinatario_bairro
    nfForm.destinatario_municipio = data.localidade || data.municipio || nfForm.destinatario_municipio
    nfForm.destinatario_uf = data.uf || nfForm.destinatario_uf
  } catch { uiStore.showNotification('CEP não encontrado.', 'warning') }
  finally { cepLoading.value = false }
}

async function saveNF() {
  saving.value = true
  try {
    const payload = {
      ...nfForm,
      destinatario_documento: (nfForm.destinatario_documento || '').replace(/\D/g, ''),
      destinatario_cep: (nfForm.destinatario_cep || '').replace(/\D/g, ''),
    }
    if (currentNF.value.id) {
      const updated = await FiscalService.updateNotaFiscal(currentNF.value.id, payload)
      currentNF.value = { ...currentNF.value, ...updated }
      uiStore.showNotification('Cabeçalho atualizado!', 'success')
    } else {
      const created = await FiscalService.createNotaFiscal(payload)
      currentNF.value = created
      uiStore.showNotification('Rascunho criado! Adicione os itens.', 'success')
      await loadItens(created.id)
      activeTab.value = 'itens'
    }
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar NF.'), 'error', 6000)
  } finally {
    saving.value = false
  }
}

// Itens
function openItemForm(item) {
  itemModal.editingId = item ? item.id : null
  Object.assign(itemForm, emptyItemForm())
  if (item) Object.assign(itemForm, item)
  itemModal.open = true
}

function preencherProduto() {
  const p = produtos.value.find(x => x.id === itemForm.produto)
  if (!p) return
  itemForm.produto_descricao = p.descricao
  itemForm.produto_ncm = p.ncm
  itemForm.produto_cest = p.cest || ''
  itemForm.produto_cfop = p.cfop_padrao || ''
  itemForm.produto_ean = p.ean || ''
  itemForm.valor_unitario = p.preco_venda || 0
}

async function saveItem() {
  savingItem.value = true
  try {
    const payload = { ...itemForm }
    if (!payload.produto) delete payload.produto
    if (itemModal.editingId) {
      await FiscalService.updateItem(currentNF.value.id, itemModal.editingId, payload)
      uiStore.showNotification('Item atualizado!', 'success')
    } else {
      await FiscalService.createItem(currentNF.value.id, payload)
      uiStore.showNotification('Item adicionado!', 'success')
    }
    itemModal.open = false
    await loadItens(currentNF.value.id)
    // Atualiza totais da NF na lista
    const nfAtualizada = await FiscalService.getNotaFiscal(currentNF.value.id)
    currentNF.value = nfAtualizada
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao salvar item.'), 'error', 6000)
  } finally {
    savingItem.value = false
  }
}

function openDeleteItemModal(item) {
  deleteItemModal.open = true
  deleteItemModal.id = item.id
  deleteItemModal.notaId = currentNF.value.id
  deleteItemModal.descricao = item.produto_descricao
}

async function confirmarDeleteItem() {
  savingItem.value = true
  try {
    await FiscalService.deleteItem(deleteItemModal.notaId, deleteItemModal.id)
    uiStore.showNotification('Item removido!', 'success')
    deleteItemModal.open = false
    await loadItens(currentNF.value.id)
    const nfAtualizada = await FiscalService.getNotaFiscal(currentNF.value.id)
    currentNF.value = nfAtualizada
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao remover item.'), 'error')
  } finally {
    savingItem.value = false
  }
}

// Autorizar
function openAutorizarModal(nf) {
  autorizarModal.open = true
  autorizarModal.id = nf.id
  autorizarModal.numero = nf.numero
  autorizarModal.serie = nf.serie
}

async function confirmarAutorizar() {
  saving.value = true
  try {
    await FiscalService.autorizarNotaFiscal(autorizarModal.id)
    uiStore.showNotification('NF enviada para autorização!', 'success')
    autorizarModal.open = false
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao autorizar NF.'), 'error', 8000)
  } finally {
    saving.value = false
  }
}

// Cancelar
function openCancelarModal(nf) {
  cancelarModal.open = true
  cancelarModal.id = nf.id
  cancelarModal.numero = nf.numero
  cancelarModal.serie = nf.serie
  cancelarModal.justificativa = ''
}

async function confirmarCancelar() {
  saving.value = true
  try {
    await FiscalService.cancelarNotaFiscal(cancelarModal.id, cancelarModal.justificativa)
    uiStore.showNotification('NF cancelada!', 'success')
    cancelarModal.open = false
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao cancelar NF.'), 'error', 8000)
  } finally {
    saving.value = false
  }
}

// Download DANFE
async function downloadDanfe(id) {
  try {
    uiStore.showNotification('Gerando DANFE...', 'info')
    const blob = await FiscalService.getDanfePdf(id)
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `danfe_${id}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    uiStore.showNotification('Erro ao gerar DANFE.', 'error')
  }
}

// Excluir NF (rascunho)
function openDeleteModal(nf) {
  deleteNFModal.open = true
  deleteNFModal.id = nf.id
  deleteNFModal.numero = nf.numero
  deleteNFModal.serie = nf.serie
}

async function confirmarDeleteNF() {
  saving.value = true
  try {
    await FiscalService.deleteNotaFiscal(deleteNFModal.id)
    uiStore.showNotification('Rascunho excluído!', 'success')
    deleteNFModal.open = false
    fetchNotasFiscais()
  } catch (err) {
    uiStore.showNotification(extractApiErrorMessage(err, 'Erro ao excluir NF.'), 'error')
  } finally {
    saving.value = false
  }
}

// Helpers
function statusClass(status) {
  switch (status) {
    case 'AUTORIZADA': return 'bg-green-600'
    case 'REJEITADA': return 'bg-red-600'
    case 'CANCELADA':
    case 'DENEGADA': return 'bg-gray-500'
    case 'PENDENTE':
    case 'PROCESSANDO': return 'bg-yellow-600'
    default: return 'bg-blue-600' // RASCUNHO
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0)
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('pt-BR')
}

function formatDoc(doc) {
  if (!doc) return ''
  if (doc.length === 11) return doc.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  return doc.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
}
</script>
