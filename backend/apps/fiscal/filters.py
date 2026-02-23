import django_filters
from .models import NotaFiscal

class NotaFiscalFilter(django_filters.FilterSet):
    data_emissao_after = django_filters.DateFilter(field_name='data_emissao', lookup_expr='gte')
    data_emissao_before = django_filters.DateFilter(field_name='data_emissao', lookup_expr='lte')

    class Meta:
        model = NotaFiscal
        fields = ['status', 'tipo_nf', 'finalidade', 'data_emissao_after', 'data_emissao_before']
