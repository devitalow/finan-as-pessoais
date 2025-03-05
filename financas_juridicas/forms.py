from django import forms
from .models import Empresa, CategoriaJuridica, ContaJuridica, TransacaoJuridica, Imposto

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'razao_social', 'endereco', 'telefone', 'email', 'data_fundacao']
        widgets = {
            'data_fundacao': forms.DateInput(attrs={'type': 'date'}),
            'endereco': forms.Textarea(attrs={'rows': 3}),
        }

class CategoriaJuridicaForm(forms.ModelForm):
    class Meta:
        model = CategoriaJuridica
        fields = ['nome', 'tipo', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class ContaJuridicaForm(forms.ModelForm):
    class Meta:
        model = ContaJuridica
        fields = ['nome', 'tipo', 'banco', 'agencia', 'numero', 'saldo']
        widgets = {
            'saldo': forms.NumberInput(attrs={'step': '0.01'}),
        }

class TransacaoJuridicaForm(forms.ModelForm):
    class Meta:
        model = TransacaoJuridica
        fields = ['descricao', 'valor', 'data', 'tipo', 'metodo_pagamento', 'categoria', 
                 'conta', 'conta_destino', 'numero_nota', 'observacao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        empresa = kwargs.pop('empresa', None)
        super(TransacaoJuridicaForm, self).__init__(*args, **kwargs)
        
        if user and empresa:
            self.fields['categoria'].queryset = CategoriaJuridica.objects.filter(usuario=user, empresa=empresa)
            self.fields['conta'].queryset = ContaJuridica.objects.filter(usuario=user, empresa=empresa)
            self.fields['conta_destino'].queryset = ContaJuridica.objects.filter(usuario=user, empresa=empresa)
            
            # Tornar conta_destino obrigatória apenas para transferências
            self.fields['conta_destino'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        conta_destino = cleaned_data.get('conta_destino')
        conta = cleaned_data.get('conta')
        
        # Validar conta_destino para transferências
        if tipo == 'T' and not conta_destino:
            self.add_error('conta_destino', 'Para transferências, a conta de destino é obrigatória.')
        
        # Validar que conta e conta_destino são diferentes
        if tipo == 'T' and conta and conta_destino and conta == conta_destino:
            self.add_error('conta_destino', 'A conta de destino deve ser diferente da conta de origem.')
        
        return cleaned_data

class ImpostoForm(forms.ModelForm):
    class Meta:
        model = Imposto
        fields = ['nome', 'valor', 'data_vencimento', 'data_pagamento', 'status', 'periodo_referencia', 'observacao']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
            'periodo_referencia': forms.TextInput(attrs={'placeholder': 'MM/AAAA'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        } 