// Função para formatar valores monetários
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Função para formatar datas
function formatarData(data) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(data));
}

// Adicionar classes do Bootstrap aos campos de formulário
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar classes aos campos de formulário
    const formFields = document.querySelectorAll('form input, form select, form textarea');
    formFields.forEach(field => {
        if (field.type !== 'checkbox' && field.type !== 'radio' && field.type !== 'submit' && field.type !== 'button') {
            field.classList.add('form-control');
        }
        if (field.type === 'checkbox' || field.type === 'radio') {
            field.classList.add('form-check-input');
        }
        if (field.type === 'submit' || field.type === 'button') {
            field.classList.add('btn', 'btn-primary');
        }
    });

    // Adicionar classes aos labels de checkbox e radio
    const checkLabels = document.querySelectorAll('form input[type="checkbox"] + label, form input[type="radio"] + label');
    checkLabels.forEach(label => {
        label.classList.add('form-check-label');
    });

    // Configurar mensagens de alerta para fechamento automático
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Inicializar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Função para alternar entre visões (pessoal/jurídica)
function alternarVisao() {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/usuarios/alternar-visao/';
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
}

// Função para confirmar exclusão
function confirmarExclusao(event, mensagem) {
    if (!confirm(mensagem || 'Tem certeza que deseja excluir este item?')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Função para filtrar tabelas
function filtrarTabela(inputId, tabelaId, indice) {
    const input = document.getElementById(inputId);
    const tabela = document.getElementById(tabelaId);
    const linhas = tabela.getElementsByTagName('tr');
    
    input.addEventListener('keyup', function() {
        const termo = input.value.toLowerCase();
        
        for (let i = 1; i < linhas.length; i++) {
            const celula = linhas[i].getElementsByTagName('td')[indice];
            if (celula) {
                const texto = celula.textContent || celula.innerText;
                if (texto.toLowerCase().indexOf(termo) > -1) {
                    linhas[i].style.display = '';
                } else {
                    linhas[i].style.display = 'none';
                }
            }
        }
    });
} 