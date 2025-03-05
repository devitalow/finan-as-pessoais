from django.core.management.base import BaseCommand
from financas_pessoais.models import Conta

class Command(BaseCommand):
    help = 'Atualiza o saldo_inicial das contas existentes para ser igual ao saldo atual'

    def handle(self, *args, **options):
        contas = Conta.objects.all()
        self.stdout.write(self.style.SUCCESS(f"Encontradas {contas.count()} contas para atualizar."))
        
        for conta in contas:
            try:
                self.stdout.write(f"Atualizando conta: {conta.nome}")
                self.stdout.write(f"  Saldo atual: {conta.saldo}")
                self.stdout.write(f"  Saldo inicial antes: {conta.saldo_inicial}")
                
                # Atualiza o saldo_inicial para ser igual ao saldo atual
                conta.saldo_inicial = conta.saldo
                conta.save(update_fields=['saldo_inicial'])
                
                # Recarrega a conta do banco de dados para garantir que temos os valores atualizados
                conta.refresh_from_db()
                self.stdout.write(f"  Saldo inicial depois: {conta.saldo_inicial}")
                self.stdout.write(self.style.SUCCESS(f"  Conta {conta.nome} atualizada com sucesso!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao atualizar conta {conta.nome}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Atualização concluída!")) 