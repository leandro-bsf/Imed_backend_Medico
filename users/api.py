import bcrypt
import jwt
from datetime import datetime, timedelta
from ninja import NinjaAPI, Router
from pydantic import BaseModel
from .models import Usuario
from django.http import Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
router = Router()
api = NinjaAPI()

SECRET_KEY = "b&=kv*m2x0^d5z7$p4v+1w#f!@8s9+qc_2%3w-#n@4!e7c&j^y"  # Altere para uma chave secreta forte

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

class LoginSchema(BaseModel):
    email: str
    senha: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/register")
def register(request, data: RegisterSchema):
    if Usuario.objects.filter(email=data.email).exists():
        return {"error": "Email already registered"}
    if Usuario.objects.filter(documento=data.documento).exists():
        return {"error": "Documento already registered"}

    hashed_password = hash_password(data.senha)
    usuario = Usuario.objects.create(
        nome=data.nome,
        telefone=data.telefone,
        email=data.email,
        senha=hashed_password,
        dt_nascimento=data.dt_nascimento,
        genero=data.genero,
        id_especialidade=data.id_especialidade,
        documento=data.documento
    )
    return {"message": "User registered successfully", "user_id": usuario.id}

@router.post("/login", response=TokenSchema)
@csrf_exempt  # Adicione este decorador para desabilitar a verificação CSRF apenas se for necessário. Não é recomendado para endpoints de login.
def login(request, data: LoginSchema):
    csrf_token = get_token(request)  # Obtém o token CSRF
    try:
        usuario = Usuario.objects.get(email=data.email)
        if not verify_password(data.senha, usuario.senha):
            raise Http404("Invalid credentials")

        access_token = create_access_token(data={"user_id": usuario.id})
        return {"access_token": access_token, "token_type": "bearer", "csrf_token": csrf_token}
    except Usuario.DoesNotExist:
        raise Http404("Invalid credentials")
    
# Adicione o router à instância do NinjaAPI
api.add_router("/auth", router)
