import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financas_app.settings')
django.setup()

from financas_pessoais.models import Conta
from django.db.models import F

def atualizar_saldo_inicial():
    # Atualiza o saldo_inicial para ser igual ao saldo atual para contas existentes
    contas = Conta.objects.all()
    print(f"Encontradas {contas.count()} contas para atualizar.")
    
    for conta in contas:
        try:
            print(f"Atualizando conta: {conta.nome}")
            print(f"  Saldo atual: {conta.saldo}")
            print(f"  Saldo inicial antes: {conta.saldo_inicial}")
            
            # Atualiza o saldo_inicial para ser igual ao saldo atual
            conta.saldo_inicial = conta.saldo
            conta.save(update_fields=['saldo_inicial'])
            
            # Recarrega a conta do banco de dados para garantir que temos os valores atualizados
            conta.refresh_from_db()
            print(f"  Saldo inicial depois: {conta.saldo_inicial}")
        except Exception as e:
            print(f"Erro ao atualizar conta {conta.nome}: {str(e)}")
    
    print("Atualização concluída!")

if __name__ == "__main__":
    atualizar_saldo_inicial() 