from django.db import models

class Profissional(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)  # Armazena a senha em texto simples ou hash
    dt_nascimento = models.DateField()  # Data de nascimento do usuário
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])  # Gênero do usuário
    id_especialidade = models.IntegerField()  # ID da especialidade do usuário (se aplicável)
    documento = models.CharField(max_length=20, unique=True)  # Documento único (CPF, RG, etc.)
    cpf = models.CharField(max_length=14, unique=True)
    # Novos campos adicionados
    tempo_atuacao = models.PositiveIntegerField(null=True)  # Tempo de atuação em anos
    foto = models.ImageField(upload_to='fotos_profissionais/', null=True, blank=True)  # Campo para upload de imagem
    fuso_horario = models.CharField(max_length=50, default='UTC')  # Valor padrão definido
    valor_consulta = models.DecimalField(max_digits=10, decimal_places=2 ,null=True)  # Valor da consulta
    chave_pix = models.CharField(max_length=100, blank=True, null=True)  # Chave PIX do profissional
    modalidade_atendimento = models.CharField(max_length=100 , choices=[('online ', 'Online'),('presencial','Presencial'), ('ambos','Ambos')], default= 'online') 
    def __str__(self):
        return self.nome
    class Meta:
        db_table = 'Profissional' 

class HorarioEspecialista(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)  # Relaciona o horário com o profissional
    dia_semana = models.CharField(max_length=10, choices=[
        ('segunda', 'Segunda'), ('terca', 'Terça'), ('quarta', 'Quarta'),
        ('quinta', 'Quinta'), ('sexta', 'Sexta'), ('sabado', 'Sábado'),
        ('domingo', 'Domingo')
    ] , default='segunda')
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f"{self.id_profissional.nome} - {self.id_horario}"

    class Meta:
        db_table = 'HorarioEspecialista'

class HorarioDisponivel(models.Model):
    medico = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    horario = models.ForeignKey(HorarioEspecialista, on_delete=models.CASCADE)
    data = models.DateField()  # Data específica (ex: 23 SET)
    dispnivel = models.BooleanField(default=True)  # Disponível ou não para agendamento


class Avaliacao(models.Model):
    estrela = models.IntegerField()  # Nota de 1 a 5
    comentario = models.TextField()  # Comentário do paciente
    especialista = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='avaliacoes')  # Relaciona com o especialista
    paciente = models.IntegerField()  # ID do paciente

    def __str__(self):
        return f"Avaliação {self.estrela} estrelas para o especialista {self.especialista.nome}"

    class Meta:
        db_table = 'avaliacoes'


class EnderecoEspecialista(models.Model):
    id_especialista = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='enderecos')  # Relaciona com o especialista
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)  # Unidade Federativa (ePx: SP, RJ)
    cep = models.CharField(max_length=10)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    complemento = models.CharField(max_length=255, blank=True, null=True)  # Campo opcional

    def __str__(self):
        return f"Endereço de {self.especialista.nome} - {self.endereco}, {self.numero}"

    class Meta:
        db_table = 'endereco_especialista'