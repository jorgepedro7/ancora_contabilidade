from rest_framework import viewsets, status, filters
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from backend.apps.core.utils import obter_empresa_ativa_ou_erro
from .models import NotaFiscal, ItemNotaFiscal, EventoNotaFiscal
from .serializers import NotaFiscalSerializer, ItemNotaFiscalSerializer, EventoNotaFiscalSerializer
from .services import NFeService
from backend.apps.core.utils import gerar_chave_acesso_nfe
from .filters import NotaFiscalFilter # New import

class NotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = NotaFiscal.objects.all()
    serializer_class = NotaFiscalSerializer
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NotaFiscalFilter # New line
    filterset_fields = ['status', 'tipo_nf', 'finalidade']
    search_fields = ['numero', 'chave_acesso', 'destinatario_nome', 'destinatario_documento']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        # Gerar a chave de acesso e o número/série antes de salvar, se for a primeira criação
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        config_fiscal = empresa.configuracao_fiscal

        # Criar a nota fiscal como rascunho
        nota_fiscal = serializer.save(empresa=empresa, status='RASCUNHO')
        
        # Gerar chave de acesso (se já não tiver uma, o que pode acontecer em rascunhos)
        if not nota_fiscal.chave_acesso:
            chave = gerar_chave_acesso_nfe(
                cUF=nota_fiscal.empresa.uf,
                AAMM=nota_fiscal.data_emissao.strftime('%y%m'),
                CNPJ=nota_fiscal.empresa.cnpj,
                mod=nota_fiscal.modelo,
                serie=nota_fiscal.serie,
                nNF=str(nota_fiscal.numero).zfill(9),
                tpEmis='1', # Sempre normal para este exemplo
                cNF=str(nota_fiscal.numero).zfill(8) # Código numérico da NF-e (8 dígitos)
            )
            nota_fiscal.chave_acesso = chave
            nota_fiscal.save(update_fields=['chave_acesso'])
        
        # O campo numero e serie já deveriam ter sido populados pelo save() do model
        # nota_fiscal.numero = config_fiscal.proximo_numero_nfe() # Exemplo
        # nota_fiscal.serie = config_fiscal.serie_nfe # Exemplo
        # nota_fiscal.save()


    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=['post'])
    def autorizar(self, request, pk=None):
        nota_fiscal = self.get_object()
        if nota_fiscal.status not in ['RASCUNHO', 'REJEITADA']:
            return Response({'error': 'A nota fiscal não pode ser autorizada neste status.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 1. Gerar XML
            xml_nfe = NFeService.gerar_xml(nota_fiscal)
            
            # 2. Assinar XML
            xml_assinado = NFeService.assinar_xml(xml_nfe, nota_fiscal.empresa)
            
            # 3. Enviar para SEFAZ
            retorno_sefaz = NFeService.enviar_sefaz(xml_assinado, nota_fiscal.empresa.uf, nota_fiscal.empresa.configuracao_fiscal.ambiente_sefaz)
            
            # 4. Processar retorno
            NFeService.processar_retorno(nota_fiscal, retorno_sefaz)

            return Response(NotaFiscalSerializer(nota_fiscal).data, status=status.HTTP_200_OK)
        except Exception as e:
            # Em caso de erro, mudar status para REJEITADA ou similar e registrar log
            nota_fiscal.status = 'REJEITADA'
            nota_fiscal.mensagem_retorno = str(e)
            nota_fiscal.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        nota_fiscal = self.get_object()
        justificativa = request.data.get('justificativa')
        if not justificativa:
            return Response({'error': 'Justificativa é obrigatória para o cancelamento.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            NFeService.cancelar_nota(nota_fiscal, justificativa)
            return Response(NotaFiscalSerializer(nota_fiscal).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def danfe(self, request, pk=None):
        nota_fiscal = self.get_object()
        try:
            pdf_danfe_bytes = NFeService.gerar_danfe(nota_fiscal)
            response = HttpResponse(pdf_danfe_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="danfe_{nota_fiscal.numero}.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def email(self, request, pk=None):
        nota_fiscal = self.get_object()
        target_email = request.data.get('email', nota_fiscal.destinatario_email)
        if not target_email:
            return Response({'error': 'E-mail do destinatário não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Em um sistema real, aqui você enfileiraria uma tarefa Celery para enviar o e-mail
        # Ex: enviar_email_nfe.delay(nota_fiscal.id, target_email)
        # Por simplicidade, apenas retornamos sucesso
        return Response({'status': 'E-mail enfileirado para envio.'}, status=status.HTTP_200_OK)

class ItemNotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = ItemNotaFiscal.objects.all()
    serializer_class = ItemNotaFiscalSerializer
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['nota_fiscal']
    search_fields = ['produto_descricao']

    def get_queryset(self):
        # Garante que o usuário só veja itens de notas fiscais da empresa ativa
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(nota_fiscal__empresa=self.request.user.empresa_ativa)
        return self.queryset.none()

    def perform_create(self, serializer):
        # Ao criar um item, associar à nota fiscal que vem da URL ou corpo da requisição
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        nota_fiscal_id = self.kwargs.get('nota_fiscal_pk') or self.request.data.get('nota_fiscal')
        if not nota_fiscal_id:
            raise serializers.ValidationError({"nota_fiscal": "ID da Nota Fiscal é obrigatório."})
        
        try:
            nota_fiscal = NotaFiscal.objects.get(id=nota_fiscal_id, empresa=empresa)
        except NotaFiscal.DoesNotExist:
            raise serializers.ValidationError({"nota_fiscal": "Nota Fiscal não encontrada ou não pertence à empresa ativa."})
        
        # Preencher dados do produto se um FK de produto for fornecido
        produto_id = self.request.data.get('produto')
        if produto_id:
            try:
                produto = Produto.objects.get(id=produto_id, empresa=empresa)
                serializer.validated_data['produto_descricao'] = produto.descricao
                serializer.validated_data['produto_ncm'] = produto.ncm
                serializer.validated_data['produto_cest'] = produto.cest
                serializer.validated_data['produto_cfop'] = produto.cfop_padrao
                serializer.validated_data['produto_ean'] = produto.ean
            except Produto.DoesNotExist:
                raise serializers.ValidationError({"produto": "Produto não encontrado ou não pertence à empresa ativa."})
        
        serializer.save(nota_fiscal=nota_fiscal)

class EventoNotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = EventoNotaFiscal.objects.all()
    serializer_class = EventoNotaFiscalSerializer
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nota_fiscal', 'tipo_evento']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa)
        return self.queryset.none()

    def perform_create(self, serializer):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        nota_fiscal_id = self.kwargs.get('nota_fiscal_pk') or self.request.data.get('nota_fiscal')
        if not nota_fiscal_id:
            raise serializers.ValidationError({"nota_fiscal": "ID da Nota Fiscal é obrigatório."})
        
        try:
            nota_fiscal = NotaFiscal.objects.get(id=nota_fiscal_id, empresa=empresa)
        except NotaFiscal.DoesNotExist:
            raise serializers.ValidationError({"nota_fiscal": "Nota Fiscal não encontrada ou não pertence à empresa ativa."})
        
        serializer.save(empresa=empresa, nota_fiscal=nota_fiscal)
