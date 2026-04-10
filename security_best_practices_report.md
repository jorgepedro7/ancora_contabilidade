# Relatório de Segurança

## Resumo executivo

Foi realizada uma revisão estática da aplicação com foco no OWASP Top 10, cobrindo backend Django/DRF e frontend Vue/Vite. Os dois achados mais graves são:

1. Controle de acesso sensível aplicado apenas na interface, sem enforcement equivalente no backend.
2. Segredos fiscais armazenados e serializados em texto puro pela API.

Também há falhas relevantes de configuração segura em produção e aceitação de uploads sem validação robusta.

Escopo desta revisão:
- análise estática do repositório
- validação complementar com `python manage.py check --deploy`

Fora do escopo:
- pentest dinâmico autenticado
- revisão de infraestrutura, proxy reverso, CDN, WAF e storage real de produção

## Críticas

### SEC-001
- Regra OWASP: A01 Broken Access Control
- Severidade: Crítica
- Localização:
  - `backend/apps/core/models.py:74`
  - `backend/apps/core/permissions.py:10`
  - `backend/apps/empresas/views.py:17`
  - `backend/apps/cadastros/views.py:8`
  - `backend/apps/financeiro/views.py:12`
  - `backend/apps/intake/views.py:22`
  - `frontend/src/components/layout/AppSidebar.vue:12`
- Evidência:
  - O backend define perfis incluindo `CLIENTE` em `PerfilPermissao`, mas a permissão efetiva usada nos módulos operacionais é apenas `IsActiveCompany`.
  - `IsActiveCompany.has_permission()` apenas verifica autenticação + existência de empresa ativa, sem checar perfil ou permissão granular.
  - As rotas de backoffice em `cadastros`, `financeiro`, `intake` e `empresas` usam `IsActiveCompany` ou apenas `IsAuthenticated`.
  - A restrição de “cliente não vê backoffice” está apenas no frontend via `requiresBackoffice`.
- Impacto:
  - Um usuário com perfil `CLIENTE` pode chamar diretamente a API e acessar ou alterar dados de backoffice da própria empresa, incluindo financeiro, cadastros, intake, e possivelmente configurações fiscais.
- Correção sugerida:
  - Implementar autorização server-side por perfil e por ação.
  - Criar permissões explícitas como `IsBackofficeUser`, `CanManageFinanceiro`, `CanViewFolha`, `CanManageEmpresas`.
  - Aplicar essas permissões em cada `ViewSet` e em actions específicas.
  - Tratar o perfil `CLIENTE` com allowlist estrita de endpoints.
  - Adicionar testes automatizados garantindo `403 Forbidden` para usuários `CLIENTE` nos módulos internos.
- Mitigação imediata:
  - Bloquear temporariamente no backend os endpoints de backoffice para perfis `CLIENTE` antes de granularizar.
- Nota:
  - Este é um bypass de autorização clássico porque o controle está no menu, não na API.

### SEC-002
- Regra OWASP: A02 Cryptographic Failures / Sensitive Data Exposure
- Severidade: Crítica
- Localização:
  - `backend/apps/empresas/models.py:47`
  - `backend/apps/empresas/models.py:48`
  - `backend/apps/empresas/models.py:99`
  - `backend/apps/empresas/models.py:100`
  - `backend/apps/empresas/serializers.py:5`
  - `backend/apps/empresas/serializers.py:19`
- Evidência:
  - `Empresa.certificado_senha` é armazenado em `CharField`.
  - `ConfiguracaoFiscalEmpresa.csc_token_nfce` também é armazenado em `CharField`.
  - O serializer aninhado `ConfiguracaoFiscalEmpresaSerializer` usa `fields = '__all__'`.
  - `EmpresaSerializer` inclui explicitamente `certificado_senha` no payload de leitura/escrita.
- Impacto:
  - Qualquer usuário autenticado com acesso ao endpoint da empresa pode recuperar segredos fiscais em texto puro, comprometendo emissão de notas, identidade fiscal e integrações com SEFAZ/NFC-e.
- Correção sugerida:
  - Remover imediatamente `certificado_senha` e `csc_token_nfce` das respostas da API.
  - Separar serializers de leitura e escrita para evitar exposição acidental.
  - Armazenar esses segredos cifrados em repouso com chave fora do banco, preferencialmente em secret manager/KMS ou campo criptografado robusto.
  - Considerar armazenar apenas referência ao segredo e não o segredo em si.
  - Rotacionar o certificado/senha e CSC caso o ambiente já tenha sido usado por terceiros.
- Mitigação imediata:
  - Tornar os campos `write_only=True` ainda hoje, enquanto a solução de criptografia é implementada.
- Nota:
  - Os nomes dos campos dizem “Criptografada”, mas o armazenamento atual não mostra qualquer criptografia no modelo nem no serializer.

## Altas

### SEC-003
- Regra OWASP: A05 Security Misconfiguration
- Severidade: Alta
- Localização:
  - `backend/config/settings.py:26`
  - `backend/config/settings.py:29`
  - `backend/config/settings.py:177`
  - `backend/config/settings.py:203`
  - `backend/config/settings.py:204`
- Evidência:
  - `SECRET_KEY` possui fallback inseguro hardcoded.
  - `DEBUG` fica `True` por padrão.
  - O JWT é assinado com `SIGNING_KEY = SECRET_KEY`.
  - `CORS_ALLOW_ALL_ORIGINS = True`.
  - `CORS_ALLOW_CREDENTIALS = True`.
  - O comando `python manage.py check --deploy` retornou warnings `security.W009`, `security.W018`, `security.W012`, `security.W016`, `security.W004` e `security.W008`.
- Impacto:
  - Um deploy mal configurado pode expor páginas de debug, usar chave previsível para assinatura de tokens e operar sem baseline mínima de HTTPS/cookies seguras.
- Correção sugerida:
  - Falhar o boot em produção se `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` e origins confiáveis não estiverem definidos.
  - Separar `settings` de desenvolvimento e produção.
  - Restringir CORS a domínios confiáveis.
  - Configurar `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` e política de headers adequada no ambiente produtivo.
- Mitigação imediata:
  - Trocar a configuração padrão para segura por omissão e habilitar relaxamentos apenas em desenvolvimento.
- Nota:
  - Parte do risco depende de como o projeto é implantado, mas o código hoje favorece erro operacional perigoso.

### SEC-004
- Regra OWASP: A05 Security Misconfiguration / A08 Software and Data Integrity Failures
- Severidade: Alta
- Localização:
  - `backend/apps/intake/models.py:79`
  - `backend/apps/intake/serializers.py:46`
  - `backend/apps/intake/serializers.py:67`
  - `backend/config/urls.py:28`
- Evidência:
  - `DocumentoRecebido.arquivo` aceita qualquer arquivo.
  - O serializer não valida extensão, MIME type, tamanho, conteúdo ativo ou quotas.
  - Em modo debug, a aplicação expõe `MEDIA_URL` diretamente por Django.
- Impacto:
  - A aplicação pode receber arquivos arbitrários, incluindo HTML/SVG/polyglots ou cargas maliciosas. Se esses arquivos forem servidos inline no mesmo domínio por proxy/storage, o risco inclui XSS armazenado, malware hosting e abuso de armazenamento.
- Correção sugerida:
  - Validar extensão, MIME type real e tamanho máximo por tipo de upload.
  - Rejeitar formatos ativos desnecessários como HTML/SVG/JS.
  - Submeter uploads a antivírus ou scanning assíncrono.
  - Servir mídia por domínio/host separado, com `Content-Disposition: attachment` para arquivos não renderizáveis com segurança.
  - Definir quotas e limites por usuário/empresa.
- Mitigação imediata:
  - Começar com allowlist rígida de extensões e limite de tamanho no serializer.
- Nota:
  - O impacto máximo depende de como a mídia é servida fora do ambiente de desenvolvimento; isso deve ser verificado na infraestrutura.

## Observações adicionais

- Não encontrei evidência direta de SQL injection ou uso explícito de `raw()`/`cursor()` com interpolação insegura no escopo analisado.
- Não encontrei uso de `v-html`/`innerHTML` no frontend analisado.
- O uso de tokens JWT em `localStorage` aumenta o impacto de qualquer XSS futuro; não classifiquei isso como crítico isoladamente, mas vale reavaliar ao desenhar o portal externo do cliente.

## Próximos passos recomendados

1. Corrigir imediatamente `SEC-001` e `SEC-002`.
2. Endurecer configuração de produção e pipeline de deploy para bloquear `SEC-003`.
3. Introduzir política centralizada de uploads para resolver `SEC-004`.
4. Adicionar testes de segurança automatizados para perfis `CLIENTE` e para serialização de segredos.
