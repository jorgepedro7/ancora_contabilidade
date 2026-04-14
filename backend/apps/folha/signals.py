from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FolhaPagamento

# Signals do módulo de Folha de Pagamento
# Atualmente sem signals ativos — lógica de cálculo é acionada explicitamente
# via action POST /api/folha/folha-pagamento/{id}/calcular/
