from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)  # Armazena a senha em texto simples ou hash
    dt_nascimento = models.DateField()  # Data de nascimento do usuário
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])  # Gênero do usuário
    id_especialidade = models.IntegerField()  # ID da especialidade do usuário (se aplicável)
    documento = models.CharField(max_length=20, unique=True)  # Documento único (CPF, RG, etc.)

    def __str__(self):
        return self.nome
