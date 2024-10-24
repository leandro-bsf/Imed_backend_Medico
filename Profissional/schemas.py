
from datetime import datetime
from pydantic import BaseModel
from ninja import Schema
from typing import Optional
from datetime import time




class LoginSchema(BaseModel):
    email: str
    senha: str

class TokenSchema(BaseModel):

    access_token: str
    token_type: str
    


# Atualizando o schema de registro para incluir os novos campos
class RegisterSchema(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    dt_nascimento: datetime  # Para armazenar a data de nascimento
    genero: str  # Pode ser 'M', 'F' ou 'O'
    id_especialidade: int  # ID da especialidade
    documento: str  # Documento único, como CPF
    cpf: str
    




# Função de edição do profissional

# Define o schema para os dados de atualização do Profissional
class ProfissionalSchema(Schema):
    
    nome: Optional[str]  # Campo opcional
    telefone:Optional[str]  # Campo opcional, com limite de tamanho
    email: Optional[str]   # Campo opcional, deve ser um email válido
    senha: Optional[str] 
    dt_nascimento: Optional[datetime]  # Campo opcional
    genero: Optional[str]  # Campo opcional
    id_especialidade: Optional[int]  # Campo opcional
    documento: Optional[str]   # Campo opcional
    cpf: Optional[str]   # Campo opcional
    tempo_atuacao: Optional[int]  # Campo opcional
    #foto: Optional[str]  # Para o caminho da foto, você pode adaptar se necessário
    fuso_horario: Optional[str] = 'UTC'  # Campo opcional, com valor padrão
    valor_consulta: Optional[float]  # Campo opcional
    chave_pix: Optional[str]  # Campo opcional
    modalidade_atendimento: Optional[str]  # Campo opcional

class SchemaCriahorario(Schema):

    dia_semana: str
    hora_inicio: str
    hora_fim: str

class HorarioEspecialistaSchema(Schema):
    id: int
    profissional: int  # 
    dia_semana: str
    hora_inicio: str
    hora_fim: str
  


class AvaliacaoSchema(Schema):
    estrela: int
    comentario: str
    paciente: int

class AtualizarAvaliacaoSchema(Schema):
    estrela: int
    comentario: str

    
class EnderecoEspecialistaSchema(BaseModel):
    endereco: str
    cidade: str
    uf: str
    cep: str
    numero: str
    bairro: str
    complemento: Optional[str] = None

class EnderecoEspecialistaSchemaList(BaseModel):
    id: int
    endereco: str
    cidade: str
    uf: str
    cep: str
    numero: str
    bairro: str
    complemento: Optional[str] = None

       