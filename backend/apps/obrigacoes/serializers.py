from rest_framework import serializers
from .models import ObrigacaoFiscal

class ObrigacaoFiscalSerializer(serializers.ModelSerializer):
    tipo_obrigacao_display = serializers.CharField(source='get_tipo_obrigacao_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)

    class Meta:
        model = ObrigacaoFiscal
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']
