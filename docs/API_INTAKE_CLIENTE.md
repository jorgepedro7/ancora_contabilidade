# API Contract - Intake Cliente

> **Status:** Fase 1 Complete
> **Audience:** Frontend Teams (Portal Cliente & Backoffice)

## Overview

Endpoints para portal cliente autenticado. Separação clara entre:
- Endpoints internos (`/api/intake/recebimentos/`, etc.): Backoffice apenas
- Endpoints cliente (`/api/intake/cliente/*`): Cliente autenticado

All requests require JWT token and `X-Empresa-Id` header.

## Endpoints

### GET /api/intake/cliente/portal/{slug}/

Retorna configuração do portal (tipos aceitos, extensões, tamanho máximo).

**Permission:** IsIntakeClientCompany

**Response (200):**
```json
{
  "slug": "portal-ancora",
  "nome": "Portal Âncora",
  "tipos_documento_permitidos": [
    {"value": "FINANCEIRO", "label": "Documentos Financeiros"},
    {"value": "GERAL", "label": "Documentos Gerais"},
    {"value": "FISCAL", "label": "Documentos Fiscais"},
    {"value": "FOLHA", "label": "Documentos de Folha"},
    {"value": "CONTRATUAL", "label": "Documentos Contratuais"}
  ],
  "extensoes_permitidas": [".pdf", ".xml", ".csv", ".zip", ".jpg", ".jpeg", ".png"],
  "tamanho_maximo_mb": 10
}
```

---

### GET /api/intake/cliente/recebimentos/

Lista documentos enviados pelo usuário autenticado.

**Permission:** IsIntakeClientCompany

**Query Parameters:**
- `page` (optional, int): Página
- `limit` (optional, int): Itens por página

**Response (200):**
```json
{
  "count": 2,
  "total_pages": 1,
  "current_page": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "titulo": "Nota Fiscal",
      "tipo_documento": "FISCAL",
      "competencia": "2026-04",
      "status": "NOVO",
      "arquivo_nome": "nf_001.pdf",
      "portal_cliente_slug": "portal-ancora",
      "criado_em": "2026-04-15T10:30:00Z",
      "validado_em": null,
      "observacoes": null,
      "referencia_cliente": "NF-001",
      "log_validacao": "Documento recebido, aguardando análise"
    }
  ]
}
```

---

### POST /api/intake/cliente/recebimentos/

Cliente envia novo documento.

**Permission:** IsIntakeClientCompany

**Request (multipart/form-data):**
```
titulo: "Nota Fiscal 2026"
tipo_documento: "FISCAL"
competencia: "2026-04"
arquivo: <file>
referencia_cliente: "NF-123" (optional)
observacoes: "..." (optional)
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "titulo": "Nota Fiscal 2026",
  "tipo_documento": "FISCAL",
  "competencia": "2026-04",
  "status": "NOVO",
  "arquivo_nome": "nota.pdf",
  "portal_cliente_slug": "portal-ancora",
  "criado_em": "2026-04-15T10:35:00Z",
  "validado_em": null,
  "observacoes": null,
  "referencia_cliente": "NF-123",
  "log_validacao": "Documento recebido, aguardando análise"
}
```

**Error (400):**
```json
{
  "arquivo": ["Extensão .exe não permitida..."]
}
```

---

## Status Values

- `NOVO`: Documento aceito, aguardando triagem
- `VALIDADO`: Documento aprovado
- `REPROVADO`: Documento rejeitado

## File Constraints

**Allowed Extensions (MVP):**
- .pdf, .xml, .csv, .zip, .jpg, .jpeg, .png

**Max Size:** 10 MB

**NOT Allowed:**
- .txt, .xls, .xlsx, executables, scripts

---

## Error Codes

- 200: OK
- 201: Created
- 400: Validation failed
- 403: Permission denied
- 404: Not found
- 500: Server error

---

## Example Flow

1. `GET /api/intake/cliente/portal/portal-ancora/` → Get config
2. `POST /api/intake/cliente/recebimentos/` → Upload document
3. `GET /api/intake/cliente/recebimentos/` → List my documents

---

## Data Model

- `enviado_por`: User ID who sent document
- `origem_upload`: "CLIENTE", "BACKOFFICE", "API"
- `validado_por`: User ID who validated (null until validated)
- `validado_em`: Validation timestamp
- `referencia_cliente`: Optional client reference (NF number, contract ID, etc)
