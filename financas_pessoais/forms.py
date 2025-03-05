from django import forms
from .models import Categoria, Conta, Transacao
from django.utils import timezone

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo', 'cor', 'descricao']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class CategoriaSelectWidget(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value and not isinstance(value, (str, int)):
            value = value.value
        if value:
            try:
                categoria = Categoria.objects.get(id=value)
                option['attrs']['data-tipo'] = categoria.tipo
            except (Categoria.DoesNotExist, ValueError):
                pass
        return option

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'valor', 'data', 'tipo', 'categoria', 'conta', 'conta_destino', 
                 'metodo_pagamento', 'is_financiamento', 'numero_parcelas', 'valor_parcela', 'data_primeira_parcela', 'juros']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'data_primeira_parcela': forms.DateInput(attrs={'type': 'date'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'onchange': 'handleTipoChange(this)'}),
            'metodo_pagamento': forms.Select(attrs={'class': 'form-control', 'onchange': 'handleMetodoPagamentoChange(this)'}),
            'is_financiamento': forms.CheckboxInput(attrs={'onchange': 'handleFinanciamentoChange(this)'}),
            'numero_parcelas': forms.NumberInput(attrs={'min': '1', 'class': 'form-control'}),
            'valor_parcela': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'juros': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categoria': CategoriaSelectWidget(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Define a data atual como valor inicial
        if not self.instance.pk:  # Apenas para novas transações
            self.initial['data'] = timezone.localtime(timezone.now()).date()
        
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
            self.fields['conta'].queryset = Conta.objects.filter(usuario=usuario)
            self.fields['conta_destino'].queryset = Conta.objects.filter(usuario=usuario)
        
        # Campos de financiamento inicialmente ocultos
        self.fields['numero_parcelas'].required = False
        self.fields['valor_parcela'].required = False
        self.fields['data_primeira_parcela'].required = False
        self.fields['juros'].required = False
        
        # Adiciona classes Bootstrap
        for field in self.fields:
            if not isinstance(self.fields[field].widget, forms.CheckboxInput):
                self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        conta_destino = cleaned_data.get('conta_destino')
        is_financiamento = cleaned_data.get('is_financiamento')
        metodo_pagamento = cleaned_data.get('metodo_pagamento')
        numero_parcelas = cleaned_data.get('numero_parcelas')
        data_primeira_parcela = cleaned_data.get('data_primeira_parcela')
        
        if tipo == 'T' and not conta_destino:
            raise forms.ValidationError('Para transferências, é necessário informar a conta de destino.')
        
        if is_financiamento:
            if not numero_parcelas or numero_parcelas < 1:
                raise forms.ValidationError('Para financiamentos, é necessário informar o número de parcelas.')
            if not data_primeira_parcela:
                raise forms.ValidationError('Para financiamentos, é necessário informar a data da primeira parcela.')
            if metodo_pagamento not in ['CC', 'FI']:
                raise forms.ValidationError('Para financiamentos, o método de pagamento deve ser Cartão de Crédito ou Financiamento.')
        
        return cleaned_data

class FiltroTransacaoForm(forms.Form):
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    data_fim = forms.DateField(
        label='Data Fim',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        label='Tipo',
        choices=[('', 'Todos'), ('R', 'Receita'), ('D', 'Despesa'), ('T', 'Transferência')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    categoria = forms.ModelChoiceField(
        label='Categoria',
        queryset=Categoria.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    conta = forms.ModelChoiceField(
        label='Conta',
        queryset=Conta.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
            self.fields['conta'].queryset = Conta.objects.filter(usuario=usuario) 