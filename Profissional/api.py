import bcrypt
import jwt
from datetime import datetime, timedelta
from ninja import NinjaAPI, Router 
from .models import Profissional, HorarioEspecialista, Avaliacao, EnderecoEspecialista
from django.http import Http404
from ninja.security import HttpBearer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .schemas import RegisterSchema, TokenSchema, LoginSchema, ProfissionalUpdateSchema, HorarioEspecialistaSchema, AvaliacaoSchema, EnderecoEspecialistaSchema,AtualizarAvaliacaoSchema

router = Router()
api = NinjaAPI()

SECRET_KEY = "b&=kv*m2x0^d5z7$p4v+1w#f!@8s9+qc_2%3w-#n@4!e7c&j^y"  # Altere para uma chave secreta forte

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload  # Retorna o payload se o token for válido
        except jwt.ExpiredSignatureError:
            return None  # Token expirado
        except jwt.InvalidTokenError:
            return None  # Token inválido

# Instancia a classe de autenticação
jwt_auth = JWTAuth()

def get_jwt_from_request(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

def get_user_id_from_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

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
    if Profissional.objects.filter(email=data.email).exists():
        return {"error": "Email already registered"}
    if Profissional.objects.filter(documento=data.documento).exists():
        return {"error": "Documento already registered"}

    hashed_password = hash_password(data.senha)
    profissional = Profissional.objects.create(
        nome=data.nome,
        telefone=data.telefone,
        email=data.email,
        senha=hashed_password,
        dt_nascimento=data.dt_nascimento,
        genero=data.genero,
        id_especialidade=data.id_especialidade,
        documento=data.documento
    )
    return {"message": "User registered successfully", "user_id": profissional.id}

@router.post("/login", response=TokenSchema)
def login(request, data: LoginSchema):
    try:
        usuario = Profissional.objects.get(email=data.email)
        if not verify_password(data.senha, usuario.senha):
            raise Http404("Invalid credentials")

        access_token = create_access_token(data={"user_id": usuario.id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Profissional.DoesNotExist:
        raise Http404("Invalid credentials")

# Adiciona o router à instância do NinjaAPI
api.add_router("/auth", router)

@api.put('/profissional/editar/{id}/')
def editar_profissional(request, id: int, payload: ProfissionalUpdateSchema):
    try:
        # Obtém o objeto Profissional pelo ID
        profissional = get_object_or_404(Profissional, id=id)
        
        # Atualiza os campos do objeto Profissional com os dados recebidos
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(profissional, attr, value)

        # Salva o objeto atualizado no banco de dados
        profissional.save()

        # Retorna a resposta como um dicionário
        return {"message": "Dados do profissional atualizados com sucesso!"}
    
    except Exception as e:
        # Retorna a mensagem de erro como um dicionário com código de status 400
        return {"error": str(e)}, 400

@router.post("/horarios/", auth=jwt_auth)
def criar_horario(request, payload: HorarioEspecialistaSchema):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    novo_horario = HorarioEspecialista(
        horario=payload.horarios,
        id_profissional=profissional
    )
    novo_horario.save()
    return {"success": True, "message": "Horário criado com sucesso", "id_horario": novo_horario.id_horario}

@router.put("/horarios/{horario_id}/", auth=jwt_auth)
def editar_horario(request, horario_id: int, payload: HorarioEspecialistaSchema):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    horario = get_object_or_404(HorarioEspecialista, id=horario_id, id_profissional=profissional.id)

    horario.horario = payload.horarios
    horario.save()

    return {"success": True, "message": "Horário atualizado com sucesso"}

@router.delete("/horarios/{horario_id}/", auth=jwt_auth)
def excluir_horario(request, horario_id: int):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    horario = get_object_or_404(HorarioEspecialista, id=horario_id, id_profissional=profissional.id)

    horario.delete()

    return {"success": True, "message": "Horário excluído com sucesso"}


@router.post("/avaliacoes", auth=jwt_auth)
def criar_avaliacao(request, data: AvaliacaoSchema):
    profissional = get_object_or_404(Profissional, id=data.id_especialista)
    nova_avaliacao = Avaliacao(
        estrela=data.estrela,
        comentario=data.comentario,
        especialista=profissional,
        paciente=data.id_paciente
    )
    nova_avaliacao.save()
    return {"message": "Avaliação criada com sucesso", "id_avaliacao": nova_avaliacao.id}

@router.put("/avaliacoes/{avaliacao_id}", auth=jwt_auth)
def editar_avaliacao(request, avaliacao_id: int, data: AtualizarAvaliacaoSchema):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, especialista=profissional)

    avaliacao.estrela = data.estrela
    avaliacao.comentario = data.comentario
    avaliacao.save()

    return {"message": "Avaliação atualizada com sucesso"}

@router.delete("/avaliacoes/{avaliacao_id}", auth=jwt_auth)
def excluir_avaliacao(request, avaliacao_id: int):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, especialista=profissional)

    avaliacao.delete()

    return {"message": "Avaliação excluída com sucesso"}



@router.post("/enderecos", auth=jwt_auth)
def criar_endereco(request, data: EnderecoEspecialistaSchema):
    profissional = get_object_or_404(Profissional, id=data.id_especialista)
    novo_endereco = EnderecoEspecialista(
        id_especialista=profissional,
        endereco=data.endereco,
        cidade=data.cidade,
        uf=data.uf,
        cep=data.cep,
        numero=data.numero,
        bairro=data.bairro,
        complemento=data.complemento
    )
    novo_endereco.save()
    return {"message": "Endereço adicionado com sucesso", "id_endereco": novo_endereco.id}


@router.put("/enderecos/{endereco_id}", auth=jwt_auth)
def editar_endereco(request, endereco_id: int, data: EnderecoEspecialistaSchema):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    endereco = get_object_or_404(EnderecoEspecialista, id=endereco_id, id_especialista=profissional.id)

    endereco.endereco = data.endereco
    endereco.cidade = data.cidade
    endereco.uf = data.uf
    endereco.cep = data.cep
    endereco.numero = data.numero
    endereco.bairro = data.bairro
    endereco.complemento = data.complemento
    endereco.save()

    return {"message": "Endereço atualizado com sucesso"}

@router.delete("/enderecos/{endereco_id}", auth=jwt_auth)
def excluir_endereco(request, endereco_id: int):
    user_id = request.auth.get("user_id")
    profissional = get_object_or_404(Profissional, id=user_id)
    endereco = get_object_or_404(EnderecoEspecialista, id=endereco_id, id_especialista=profissional.id)

    endereco.delete()

    return {"message": "Endereço excluído com sucesso"}

