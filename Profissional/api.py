import bcrypt
import jwt
from datetime import datetime, timedelta
from ninja import NinjaAPI, Router 
from .models import Profissional ,HorarioEspecialista , Avaliacao ,EnderecoEspecialista
from django.http import Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from ninja.security import django_auth 
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .schemas import RegisterSchema, TokenSchema, LoginSchema ,ProfissionalUpdateSchema, HorarioEspecialistaSchema,AvaliacaoSchema,EnderecoEspecialistaSchema
router = Router()
api = NinjaAPI()


SECRET_KEY = "b&=kv*m2x0^d5z7$p4v+1w#f!@8s9+qc_2%3w-#n@4!e7c&j^y"  # Altere para uma chave secreta forte




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
@csrf_exempt  # Adicione este decorador para desabilitar a verificação CSRF apenas se for necessário. Não é recomendado para endpoints de login.
def login(request, data: LoginSchema):
    csrf_token = get_token(request)  # Obtém o token CSRF
    try:
        usuario = Profissional.objects.get(email=data.email)
        if not verify_password(data.senha, usuario.senha):
            raise Http404("Invalid credentials")

        access_token = create_access_token(data={"user_id": usuario.id})
        return {"access_token": access_token, "token_type": "bearer", "csrf_token": csrf_token}
    except Profissional.DoesNotExist:
        raise Http404("Invalid credentials")
    
# Adicione o router à instância do NinjaAPI
api.add_router("/auth", router)




 
@api.put('/profissional/editar/{id}/', auth=django_auth)
def editar_profissional(request, id: int, payload: ProfissionalUpdateSchema):
    try:
        # Obtém o objeto Profissional pelo ID
        profissional = get_object_or_404(Profissional, id=id)
        
        # Atualiza os campos do objeto Profissional com os dados recebidos
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(profissional, attr, value)

        # Salva o objeto atualizado no banco de dados
        profissional.save()

        return {"message": "Dados do profissional atualizados com sucesso!"}
    
    except Exception as e:
        return {"error": str(e)}, 400
    

@router.post("/horarios/")
def criar_horario(request, payload: HorarioEspecialistaSchema):
    # Buscar o profissional pelo ID
    profissional = get_object_or_404(Profissional, id=payload.id_especialista)
    
    # Criar e salvar o novo horário
    novo_horario = HorarioEspecialista(
        horario=payload.horarios,
        id_profissional=profissional
    )
    novo_horario.save()
    
    return {"success": True, "message": "Horário criado com sucesso", "id_horario": novo_horario.id_horario}


@router.post("/avaliacoes")
def criar_avaliacao(request, data: AvaliacaoSchema):
    # Buscar o profissional (especialista) pelo ID
    profissional = get_object_or_404(Profissional, id=data.id_especialista)
    
    # Criar e salvar a nova avaliação
    nova_avaliacao = Avaliacao(
        estrela=data.estrela,
        comentario=data.comentario,
        especialista=profissional,
        paciente=data.id_paciente
    )
    nova_avaliacao.save()
    
    return {"message": "Avaliação criada com sucesso", "id_avaliacao": nova_avaliacao.id}


@router.post("/enderecos")
def criar_endereco(request, data: EnderecoEspecialistaSchema):
    # Buscar o profissional (especialista) pelo ID
    profissional = get_object_or_404(Profissional, id=data.id_especialista)
    
    # Criar e salvar o novo endereço
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