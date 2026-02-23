from rest_framework import serializers
from .models import LancamentoContabil, PartidaLancamento
from backend.apps.financeiro.serializers import PlanoContasSerializer

class PartidaLancamentoSerializer(serializers.ModelSerializer):
    conta_contabil_detail = PlanoContasSerializer(source='conta_contabil', read_only=True)

    class Meta:
        model = PartidaLancamento
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'lancamento', 'criado_em', 'atualizado_em']

class LancamentoContabilSerializer(serializers.ModelSerializer):
    partidas = PartidaLancamentoSerializer(many=True, required=False) # Permite criar ou atualizar partidas aninhadas

    class Meta:
        model = LancamentoContabil
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

    def create(self, validated_data):
        partidas_data = validated_data.pop('partidas', [])
        validated_data['empresa'] = self.context['request'].user.empresa_ativa
        lancamento = LancamentoContabil.objects.create(**validated_data)
        lancamento.salvar_lancamento_com_partidas(partidas_data)
        return lancamento

    def update(self, instance, validated_data):
        partidas_data = validated_data.pop('partidas', None)
        instance = super().update(instance, validated_data)

        if partidas_data is not None:
            # Lógica para atualizar partidas existentes ou criar novas
            # Isso pode ser complexo, dependendo da necessidade de remoção de partidas antigas etc.
            # Por simplicidade, vamos deletar as antigas e recriar
            instance.partidas.all().delete()
            instance.salvar_lancamento_com_partidas(partidas_data)
        
        return instance
