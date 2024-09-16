
from datetime import datetime, timedelta
from pydantic import BaseModel
from ninja import Schema
from typing import Optional




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




# Função de edição do profissional

# Define o schema para os dados de atualização do Profissional
class ProfissionalUpdateSchema(Schema):
    nome: Optional[str]
    telefone: Optional[str]
    email: Optional[str]
    senha: Optional[str]
    dt_nascimento: Optional[str]  # Pode usar date, mas no exemplo, é string
    genero: Optional[str]
    id_especialidade: Optional[int]
    documento: Optional[str]
    tempo_atuacao: Optional[int]
    fuso_horario: Optional[str]
    valor_consulta: Optional[float]
    chave_pix: Optional[str]



class HorarioEspecialistaSchema(Schema):
    horarios: str
    id_especialista: int  # Relaciona com o ID do Profissional


class AvaliacaoSchema(BaseModel):
    estrela: int
    comentario: str
    id_especialista: int
    id_paciente: int

class AtualizarAvaliacaoSchema(BaseModel):
    estrela: int
    comentario: str

    
class EnderecoEspecialistaSchema(BaseModel):
    id_especialista: int
    endereco: str
    cidade: str
    uf: str
    cep: str
    numero: str
    bairro: str
    complemento: Optional[str] = None