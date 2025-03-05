document.addEventListener('DOMContentLoaded', function() {
    // Inicializa o estado dos campos de financiamento
    handleFinanciamentoChange(document.querySelector('[name="is_financiamento"]'));
    handleTipoChange(document.querySelector('[name="tipo"]'));
    handleMetodoPagamentoChange(document.querySelector('[name="metodo_pagamento"]'));
    
    // Atualiza as categorias quando o tipo muda
    const tipoSelect = document.querySelector('[name="tipo"]');
    if (tipoSelect) {
        atualizarCategorias(tipoSelect.value);
        tipoSelect.addEventListener('change', function() {
            atualizarCategorias(this.value);
        });
    }
});

function handleFinanciamentoChange(checkbox) {
    if (!checkbox) return;
    
    const isFinanciamento = checkbox.checked;
    const camposFinanciamento = document.getElementById('campos-financiamento');
    
    if (camposFinanciamento) {
        camposFinanciamento.style.display = isFinanciamento ? 'block' : 'none';
        
        // Atualiza o estado required dos campos
        const camposObrigatorios = [
            'numero_parcelas',
            'data_primeira_parcela'
        ];
        
        camposObrigatorios.forEach(fieldName => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.required = isFinanciamento;
            }
        });
        
        // Atualiza o campo de valor da parcela
        if (isFinanciamento) {
            calcularValorParcela();
        }
    }
}

function handleTipoChange(select) {
    if (!select) return;
    
    const contaDestinoGroup = document.querySelector('[name="conta_destino"]').closest('.form-group');
    const isTransferencia = select.value === 'T';
    
    contaDestinoGroup.style.display = isTransferencia ? 'block' : 'none';
    document.querySelector('[name="conta_destino"]').required = isTransferencia;
    
    // Desabilita financiamento para transferências
    const financiamentoCheck = document.querySelector('[name="is_financiamento"]');
    if (financiamentoCheck) {
        financiamentoCheck.disabled = isTransferencia;
        if (isTransferencia) {
            financiamentoCheck.checked = false;
            handleFinanciamentoChange(financiamentoCheck);
        }
    }

    // Atualiza as categorias visíveis
    atualizarCategorias(select.value);
}

function handleMetodoPagamentoChange(select) {
    if (!select) return;
    
    const financiamentoCheck = document.querySelector('[name="is_financiamento"]');
    if (financiamentoCheck) {
        const metodosFinanciamento = ['CC', 'FI'];
        const podeFinanciar = metodosFinanciamento.includes(select.value);
        
        financiamentoCheck.disabled = !podeFinanciar;
        if (!podeFinanciar) {
            financiamentoCheck.checked = false;
            handleFinanciamentoChange(financiamentoCheck);
        }
    }
}

function calcularValorParcela() {
    const valor = parseFloat(document.querySelector('[name="valor"]').value) || 0;
    const numeroParcelas = parseInt(document.querySelector('[name="numero_parcelas"]').value) || 1;
    const juros = parseFloat(document.querySelector('[name="juros"]').value) || 0;
    const valorParcelaField = document.querySelector('[name="valor_parcela"]');
    
    if (valor && numeroParcelas) {
        let valorParcela;
        if (juros) {
            // Cálculo com juros compostos
            const taxa = juros / 100;
            valorParcela = (valor * (taxa * Math.pow(1 + taxa, numeroParcelas))) / (Math.pow(1 + taxa, numeroParcelas) - 1);
        } else {
            // Cálculo sem juros
            valorParcela = valor / numeroParcelas;
        }
        valorParcelaField.value = valorParcela.toFixed(2);
    } else {
        valorParcelaField.value = '';
    }
}

// Adiciona listeners para recalcular o valor da parcela quando os campos relevantes mudarem
document.querySelectorAll('[name="valor"], [name="numero_parcelas"], [name="juros"]').forEach(field => {
    field.addEventListener('change', calcularValorParcela);
    field.addEventListener('keyup', calcularValorParcela);
});

function atualizarCategorias(tipo) {
    const categoriaSelect = document.querySelector('[name="categoria"]');
    if (!categoriaSelect) return;

    // Se for transferência, esconde o campo de categoria
    const categoriaGroup = categoriaSelect.closest('.form-group');
    if (categoriaGroup) {
        if (tipo === 'T') {
            categoriaGroup.style.display = 'none';
            categoriaSelect.value = '';
            categoriaSelect.required = false;
            return;
        } else {
            categoriaGroup.style.display = 'block';
            categoriaSelect.required = true;
        }
    }

    // Filtra as opções de categoria
    Array.from(categoriaSelect.options).forEach(option => {
        if (option.value === '') return; // Mantém a opção vazia (placeholder) sempre visível
        
        const tipoCategoria = option.getAttribute('data-tipo');
        const shouldShow = tipoCategoria === tipo;
        
        option.style.display = shouldShow ? '' : 'none';
        option.disabled = !shouldShow;
    });

    // Se a opção selecionada não está mais disponível, limpa a seleção
    if (categoriaSelect.selectedOptions[0]?.disabled) {
        categoriaSelect.value = '';
    }
} 