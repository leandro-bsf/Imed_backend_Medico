import bcrypt
import jwt
from datetime import datetime, timedelta
from ninja import NinjaAPI, Router 
from rest_framework.exceptions import AuthenticationFailed
from .models import Profissional, HorarioEspecialista, Avaliacao, EnderecoEspecialista
from django.http import Http404
from ninja.security import HttpBearer
from corsheaders.middleware import CorsMiddleware
from django.shortcuts import get_object_or_404
import base64
from ninja.errors import HttpError
from .schemas import RegisterSchema, TokenSchema, LoginSchema,SchemaCriahorario, ProfissionalSchema, HorarioEspecialistaSchema, AvaliacaoSchema, EnderecoEspecialistaSchema,AtualizarAvaliacaoSchema
from typing import List  # Import List
router = Router()
api = NinjaAPI()


SECRET_KEY = "b&=kv*m2x0^d5z7$p4v+1w#f!@8s9+qc_2%3w-#n@4!e7c&j^y"  # Altere para uma chave secreta forte

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Decodifica o token e valida
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"Token decodificado: {payload}")  # Para debug
            
            # Aqui você pode retornar o ID do usuário, se ele estiver no payload
            return payload.get("user_id")  # Retorna o ID do usuário, ajuste conforme necessário

        except jwt.ExpiredSignatureError:
            print("Token expirado")
            return None  # Token expirado
        except jwt.InvalidTokenError:
            print("Token inválido")
            return None  # Token inválido
# Instancia a classe de autenticação
jwt_auth = JWTAuth()

def get_jwt_from_request(request):
 
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    else:
        # Log para indicar que o token não foi encontrado ou está incorreto
        print("Token não encontrado ou formato incorreto no cabeçalho Authorization")
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
        documento=data.documento,
        cpf = data.cpf
    )
    return {"message": "User registered successfully", "user_id": profissional.id}

@router.post("/login", response=TokenSchema)
def login(request, data: LoginSchema):
    try:
        usuario = Profissional.objects.get(email=data.email)
        if not verify_password(data.senha, usuario.senha):
            raise Http404("Invalid credentials")

        access_token = create_access_token(data={"user_id": usuario.id})

        # Retorna o access token, o tipo de token e o ID do usuário
       
        return {"access_token": access_token, "token_type": "bearer"}
    
    
    except Profissional.DoesNotExist:
        raise Http404("Invalid credentials")

# Adiciona o router à instância do NinjaAPI
api.add_router("/auth", router)



@api.put('/profissional/editar/', auth=jwt_auth)
def editar_profissional(request, payload: ProfissionalSchema):
    try:
        # Passo 1: Pegar o token JWT do cabeçalho
        token = get_jwt_from_request(request)
        
        if not token:
            return {"detail": "Token not provided or invalid."}, 401
        
        # Passo 2: Decodificar o token e pegar o user_id
        user_id = get_user_id_from_token(token)
        if not user_id:
            return {"detail": "Invalid or expired token."}, 401
        
        # Passo 3: Consultar os dados do profissional no banco de dados pelo user_id
        profissional = get_object_or_404(Profissional, id=user_id)

        profissional.nome =payload.nome
        profissional.telefone = payload.telefone
        profissional.email = payload.email
        profissional.dt_nascimento = payload.dt_nascimento
        profissional.genero =  payload.genero
        profissional.id_especialidade = payload.id_especialidade
        profissional.documento = payload.documento
        profissional.cpf = payload.cpf
        profissional.tempo_atuacao = payload.tempo_atuacao
       # profissional.foto = payload.foto
        profissional.fuso_horario = payload.fuso_horario
        profissional.valor_consulta = payload.valor_consulta
        profissional.chave_pix = payload.chave_pix
        profissional.modalidade_atendimento = payload.modalidade_atendimento
        # Salva o objeto atualizado no banco de dados
        profissional.save()

        # Retorna a resposta como um dicionário
        return {"message": "Dados do profissional atualizados com sucesso!"}

    except Exception as e:
        # Retorna a mensagem de erro como um dicionário com código de status 400
        return {"error": str(e)}, 400


 ##obter dados o profissional logado
@router.get("/profissional", auth=jwt_auth)
def get_professional_data(request):
    # Passo 1: Pegar o token JWT do cabeçalho
    token = get_jwt_from_request(request)
    
    if not token:
        return {"detail": "Token not provided or invalid."}, 401
    
    # Passo 2: Decodificar o token e pegar o user_id
    user_id = get_user_id_from_token(token)
    
    if not user_id:
        return {"detail": "Invalid or expired token."}, 401
    
    # Passo 3: Consultar os dados do profissional no banco de dados
    try:
        profissional = get_object_or_404(Profissional, id=user_id)
        foto_base64 = None
        
        if profissional.foto:
            try:
                # Certifique-se de que o arquivo da foto realmente existe
                with profissional.foto.open("rb") as foto_file:
                    foto_bytes = foto_file.read()
                    foto_base64 = base64.b64encode(foto_bytes).decode('utf-8')
            except FileNotFoundError:
                return {"detail": "Foto não encontrada."}, 404
            except Exception as e:
                return {"detail": f"Erro ao abrir a foto: {str(e)}"}, 500
        
        # Retorna os dados do profissional
        return {
            "nome": profissional.nome,
            "email": profissional.email,
            "dt_nascimento": profissional.dt_nascimento,
            "genero": profissional.genero,
            "id_especialidade": profissional.id_especialidade,
            "documento": profissional.documento,
            "cpf": profissional.cpf,
            "telefone": profissional.telefone,
            "fuso_horario": profissional.fuso_horario,
            "valor_consulta": profissional.valor_consulta,
            "chave_pix": profissional.chave_pix,
            "tempo_atuacao": profissional.tempo_atuacao,
            "modalidade_atendimento": profissional.modalidade_atendimento,
          ##  "foto": foto_base64,
        }
    
    except Profissional.DoesNotExist:
        return {"detail": "Profissional não encontrado."}, 404

## adiciona horario
@router.post("/horarios/", auth=jwt_auth)
def criar_horario(request, payload: SchemaCriahorario):
    user_id = request.auth

    profissional = get_object_or_404(Profissional,id=user_id)
    print(" dedeed", profissional)
    # Cria um novo horário com os dados recebidos
    novo_horario = HorarioEspecialista(
        profissional=profissional,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim
    )
    novo_horario.save()
    return {"success": True, "message": "Horário criado com sucesso", "id_horario": novo_horario.id}

 ##edita  horario 
@router.put("/horarios/{horario_id}/", auth=jwt_auth)
def editar_horario(request, horario_id: int, payload: SchemaCriahorario):
    
    user_id = request.auth
    profissional = get_object_or_404(Profissional,id=user_id)
    horario = get_object_or_404(HorarioEspecialista, id=horario_id, profissional=profissional)

    # Atualiza os campos do horário com os dados recebidos

    horario.dia_semana = payload.dia_semana
    horario.hora_inicio = payload.hora_inicio
    horario.hora_fim = payload.hora_fim
    horario.save()

    return {"success": True, "message": "Horário atualizado com sucesso"}

##deleta horario 

@router.delete("/horarios/{horario_id}/", auth=jwt_auth)
def excluir_horario(request, horario_id: int):
    user_id = request.auth
    # Obtém o profissional autenticado
    profissional = get_object_or_404(Profissional, id=user_id)
    
    # Busca o horário com o ID fornecido e que pertence ao profissional autenticado
    horario = get_object_or_404(HorarioEspecialista, id=horario_id, profissional=profissional)

    # Exclui o horário
    horario.delete()

    return {"success": True, "message": "Horário excluído com sucesso"}


@router.get("/horarios/", response=List[HorarioEspecialistaSchema], auth=jwt_auth)
def obter_horarios_profissional(request):
    user_id = request.auth  # Aqui você deve receber o user_id corretamente autenticado
    
    
    if not user_id:
        return {"detail": "Unauthorized"}  # Retorna erro se não estiver autenticado

    try:
        profissional = Profissional.objects.get(id=user_id)
        # Filtra os horários pelo profissional
        horarios_especialista = HorarioEspecialista.objects.filter(profissional=profissional)

        # Serializando manualmente para evitar erros de validação
        resultado = [
            {
                "id": horario.id,
                "profissional": profissional.id,  # Retornando o ID do profissional, não o objeto
                "dia_semana": horario.dia_semana,
                "hora_inicio": horario.hora_inicio.strftime('%H:%M'),  # Convertendo para string
                "hora_fim": horario.hora_fim.strftime('%H:%M')  # Convertendo para string
            }
            for horario in horarios_especialista
        ]

        return resultado
    except Profissional.DoesNotExist:
        return {"error": "Profissional não encontrado"}
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        raise HttpError(500, "Erro interno no servidor")
    

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

##retorna avaliações do profissional logado

@router.get("/avaliacoes/", response=List[AvaliacaoSchema], auth=jwt_auth)
def obter_avaliacoes_profissional(request):
    user_id = request.auth
    
    # Obtém o profissional autenticado
    profissional = get_object_or_404(Profissional, id=user_id)
    
    # Busca todas as avaliações relacionadas ao profissional logado (campo é 'especialista' ao invés de 'profissional')
    avaliacoes = Avaliacao.objects.filter(especialista=profissional).values('estrela', 'comentario', 'paciente')
    
    # Retorna a lista de avaliações
    return list(avaliacoes)

### retorna avaliacao do profissional atraves do login 

@router.get("/avaliacoes/{id_profissional}", response=List[AvaliacaoSchema])
def obter_avaliacoes_por_profissional(request, id_profissional: int):
    # Obtém o profissional com base no ID passado na URL
    profissional = get_object_or_404(Profissional, id=id_profissional)
    
    # Busca todas as avaliações relacionadas ao profissional especificado
    avaliacoes = Avaliacao.objects.filter(especialista=profissional)
    
    # Retorna a lista de avaliações
    return avaliacoes


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

###retorna  enderecos do profissional logado
@router.get("/endereco", response=EnderecoEspecialistaSchema)
def obter_endereco_profissional(request):
    # Obtém o profissional logado via JWT
    profissional = get_object_or_404(Profissional, id=request.auth['user_id'])
    
    # Busca o endereço do profissional
    endereco = get_object_or_404(EnderecoEspecialista, id_especialista=profissional)
    
    # Retorna o endereço encontrado
    return endereco