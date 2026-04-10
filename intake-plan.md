# Intake módulo – plano inicial

1. **Modelos e dados**
   - `Empresa` já tem certificado/ambientação; adicione `PortalCliente`, `DocumentoRecebido`, `ChecklistCompetencia`, `Pendencia` e `LoteExportacaoQuestor` para controlar uploads, segmentos e exportações.
   - Relacione documentos enviados a `Empresa`, `Funcionario`, `NotaFiscal`, `Contrato` e registre metadados como tipo de entrega, competência, anexo e hash.
   - Armazene status (novo/validado/reprovado) e logs de validação a partir de validações específicas (ex.: checar CPF/CNPJ, datas, obrigatoriedade de arquivos fiscais).

2. **APIs e validação**
   - Crie serializers no novo app (`apps/intake`) para upload e listagem. Reaproveite `rest_framework` + JWT já presentes.
   - Exponha endpoints `POST /api/intake/recebimentos/`, `GET /api/intake/pendencias/`, `POST /api/intake/confirmar/`.
   - Disponibilize tarefas Celery (ou management commands) que gerem bundles para o Questor (`exportar`), marcando os registros processados.

3. **Frontend**
   - Adicione rota em `frontend/src/router/` (ex.: `/intake`) com views para upload de documentos, acompanhamento do checklist e visão geral das pendências.
   - Use os stores existentes (autenticação, empresa) e serviços REST padronizados para chamadas.
   - Mostre status de validação, histórico de uploads e botões de exportação para Questor.

4. **Integração com Questor**
   - Defina um esquema de exportação (ZIP, CSV, API) descrevendo os campos esperados pelo contábil (folha, fiscal, financeiro).
   - Implemente rotina de geração e um endpoint protegido `POST /api/intake/exportar/questor/` que retorna link para download ou dispara webhook.

5. **Procedimentos**
   - Documente credenciais/templates necessários (certificados, env) e registre testes a rodar (`manage.py test apps.intake`).
   - Planeje seed data e comandos (ex.: `python manage.py seed_intake`) para facilitar demos.
