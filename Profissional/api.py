import bcrypt
import jwt
from django.utils import timezone
from django.db.models import Q

from datetime import datetime, timedelta ,date
from ninja import NinjaAPI, Router 
from rest_framework.exceptions import AuthenticationFailed
from .models import Profissional,Consulta ,Despesa, Paciente, HorarioEspecialista, Avaliacao,Agendamento, EnderecoEspecialista
from django.http import Http404
from ninja.security import HttpBearer
from corsheaders.middleware import CorsMiddleware
from django.shortcuts import get_object_or_404
import base64
from django.http import JsonResponse
from ninja.errors import HttpError
from .schemas import RegisterSchema,DespesaCreateSchema,DespesaUpdateSchema , AgendamentoCreateSchema,ConsultaCreateSchema,ConsultaUpdateSchema, AtualizarAgendamentoSchema ,PacienteSchema,PacienteUpdateSchema ,PacienteOutSchemaList , TokenSchema,EnderecoEspecialistaSchemaList, LoginSchema,SchemaCriahorario, ProfissionalSchema, HorarioEspecialistaSchema, AvaliacaoSchema, EnderecoEspecialistaSchema,AtualizarAvaliacaoSchema
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

    profissional = get_object_or_404(Profissional, id=user_id)

    # Verifica se já existe um horário para o mesmo dia da semana
    horario_existente = HorarioEspecialista.objects.filter(
        profissional=profissional,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim
    ).exists()

    if horario_existente:
        return {"success": False, "message": "Já existe um horário igual para este dia."}

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
    profissional = get_object_or_404(Profissional, id=user_id)
    horario = get_object_or_404(HorarioEspecialista, id=horario_id, profissional=profissional)

    # Verifica se já existe um horário igual para o mesmo dia da semana
    horario_existente = HorarioEspecialista.objects.filter(
        profissional=profissional,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim
    ).exclude(id=horario.id).exists()

    if horario_existente:
        return {"success": False, "message": "Já existe um horário igual para este dia."}

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
def criar_avaliacao(request,  payload: AvaliacaoSchema):
    user_id = request.auth

    profissional = get_object_or_404(Profissional, id=user_id)

    nova_avaliacao = Avaliacao(
        estrela=payload.estrela,
        comentario=payload.comentario,
        especialista=profissional,
        paciente=payload.paciente
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
    # Se `request.auth` é o `id_especialista` diretamente, use-o como tal
    id_especialista = request.auth  # Aqui o id_especialista é diretamente o valor inteiro
    
    # Busca o profissional pelo ID extraído do token
    profissional = get_object_or_404(Profissional, id=id_especialista)
    
    # Cria um novo endereço com base nos dados recebidos e no profissional
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
    
    # Retorna uma resposta de sucesso com o ID do endereço criado
    return {"message": "Endereço adicionado com sucesso", "id_endereco": novo_endereco.id}


@router.put("/enderecos/{endereco_id}", auth=jwt_auth)
def editar_endereco(request, endereco_id: int, data: EnderecoEspecialistaSchema):
    user_id = request.auth
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
    user_id = request.auth
    profissional = get_object_or_404(Profissional, id=user_id)
    endereco = get_object_or_404(EnderecoEspecialista, id=endereco_id, id_especialista=profissional.id)

    endereco.delete()

    return {"message": "Endereço excluído com sucesso"}

###retorna  enderecos do profissional logado
@router.get("/endereco/", response=List[EnderecoEspecialistaSchemaList], auth=jwt_auth)
def obter_endereco_profissional(request):
    user_id = request.auth  # Aqui você deve receber o user_id corretamente autenticado
    
    if not user_id:
        return {"detail": "Unauthorized"}  # Retorna erro se não estiver autenticado

    try:
        # Busca o profissional pelo ID extraído do token
        profissional = Profissional.objects.get(id=user_id)
        
        # Filtra os endereços pelo profissional
        enderecos_especialista = EnderecoEspecialista.objects.filter(id_especialista=profissional)

        # Serializando manualmente para evitar erros de validação
        resultado = [
            {
                "id": endereco.id,
                "id_especialista": profissional.id,  # Retornando o ID do profissional, não o objeto
                "endereco": endereco.endereco,
                "cidade": endereco.cidade,
                "uf": endereco.uf,
                "cep": endereco.cep,
                "numero": endereco.numero,
                "bairro": endereco.bairro,
                "complemento": endereco.complemento,
            }
            for endereco in enderecos_especialista
        ]

        if not resultado:
            return {"detail": "Nenhum endereço encontrado para o profissional."}

        return resultado

    except Profissional.DoesNotExist:
        return {"error": "Profissional não encontrado"}
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        raise HttpError(500, "Erro interno no servidor")
    
@router.post("/paciente/" , auth=jwt_auth)
def adicionar_paciente(request, paciente: PacienteSchema):
    # Obtendo o id do profissional do request.auth (autenticação do usuário)
    user_id = request.auth

    # Buscando o profissional no banco de dados (assumindo que o user_id é o id do Profissional)
    profissional = get_object_or_404(Profissional, id=user_id)
    
    # Criando o novo paciente
    novo_paciente = Paciente.objects.create(
        nome=paciente.nome,
        email=paciente.email,
        celular=paciente.celular,
        genero=paciente.genero,
        dt_nascimento=paciente.dt_nascimento,
        foto=paciente.foto,
        cpf=paciente.cpf,
        fuso_horario=paciente.fuso_horario,
        id_profissional=profissional  # Ligando ao profissional autenticado
    )

    return {"msg": "Paciente criado com sucesso", "paciente_id": novo_paciente.id}

@router.get("/paciente/{paciente_id}/", auth=jwt_auth)
def obter_paciente_por_id(request, paciente_id: int):
    # Obtendo o id do profissional do request.auth (autenticação do usuário)
    user_id = request.auth

    # Buscando o profissional no banco de dados (assumindo que o user_id é o id do Profissional)
    profissional = get_object_or_404(Profissional, id=user_id)

    # Buscando o paciente pelo ID e garantindo que pertença ao profissional autenticado
    paciente = get_object_or_404(Paciente, id=paciente_id, id_profissional=profissional)

    # Retornando os dados do paciente
    return {
        "id": paciente.id,
        "nome": paciente.nome,
        "email": paciente.email,
        "celular": paciente.celular,
        "genero": paciente.genero,
        "dt_nascimento": paciente.dt_nascimento,
        "foto": paciente.foto.url if paciente.foto else None,
        "cpf": paciente.cpf,
        "fuso_horario": paciente.fuso_horario,
        "profissional_id": profissional.id,
    }


# Endpoint para listar os pacientes do médico logado
@router.get("/pacientes/", auth=jwt_auth)
def listar_pacientes(request):
    user_id = request.auth
    profissional = get_object_or_404(Profissional, id=user_id)
    pacientes = Paciente.objects.filter(id_profissional=profissional)
    return [PacienteOutSchemaList.from_orm(paciente) for paciente in pacientes]

# Endpoint para deletar um paciente do médico logado
@router.delete("/paciente/{paciente_id}/" , auth=jwt_auth)
def deletar_paciente(request, paciente_id: int):
    # Obtendo o id do profissional do request.auth (autenticação do usuário)
    user_id = request.auth

    # Buscando o profissional autenticado no banco de dados
    profissional = get_object_or_404(Profissional, id=user_id)

    # Buscando o paciente que pertence ao profissional autenticado
    paciente = get_object_or_404(Paciente, id=paciente_id, id_profissional=profissional)

    # Deletando o paciente
    paciente.delete()
    return {"msg": "Paciente Excluido com sucesso", "paciente_id": paciente_id}

# Endpoint para atualizar os dados do paciente do médico logado
@router.put("/paciente/{paciente_id}/" ,  auth=jwt_auth)
def atualizar_paciente(request, paciente_id: int, dados: PacienteUpdateSchema):
    # Obtendo o id do profissional do request.auth (autenticação do usuário)
    user_id = request.auth

    # Buscando o profissional autenticado no banco de dados
    profissional = get_object_or_404(Profissional, id=user_id)

    # Buscando o paciente que pertence ao profissional autenticado
    paciente = get_object_or_404(Paciente, id=paciente_id, id_profissional=profissional)

    # Atualizando os campos do paciente com os novos dados, se fornecidos
    for attr, value in dados.dict(exclude_unset=True).items():
        setattr(paciente, attr, value)
    
    # Salvando as mudanças no banco de dados
    paciente.save()

    return {"msg": "Paciente atualizado com sucesso", "paciente_id": paciente_id}

# Mapeamento dos dias da semana
DIA_SEMANA_MAPA = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo'
}



@router.get("/agendamentos/disponiveis/", auth=jwt_auth)
def listar_agendamentos_disponiveis(request):
    """
    Lista todos os horários disponíveis para o profissional autenticado.
    """
    user_id = request.auth  # Obtém o ID do profissional autenticado
    print(f"ID do profissional autenticado: {user_id}")  # Verifique o ID

    # Filtra os horários do profissional logado
    horarios_profissional = HorarioEspecialista.objects.filter(profissional_id=user_id)
    print(f"Horários do profissional: {horarios_profissional}")  # Verifique se retorna horários

    if not horarios_profissional.exists():
        return {"message": "Nenhum horário encontrado para este profissional."}

    horarios_disponiveis = []
    data_atual = timezone.now().date()  # Use timezone.now() para pegar a data atual corretamente

    # Itera sobre cada horário do profissional e verifica disponibilidade para datas futuras
    for horario in horarios_profissional:
        dia_semana = horario.dia_semana
        hora_inicio = horario.hora_inicio
        hora_fim = horario.hora_fim
       
        # Itera sobre as próximas duas semanas para verificar disponibilidade
        for i in range(1, 30):  # 30 dias
            data_verificacao = data_atual + timedelta(days=i)
            dia_da_semana = DIA_SEMANA_MAPA[data_verificacao.weekday()] 
          
            # Verifica se o dia da semana corresponde ao que está cadastrado
            if dia_da_semana == dia_semana:
                # Verifica se já existe agendamento nesse dia e horário
                
                 agendamento_existente = Agendamento.objects.filter(
                    profissional_id=user_id,
                    data=data_verificacao,
                    horario_id=horario.id,
                    horario__hora_inicio__lte=hora_fim,
                    horario__hora_fim__gte=hora_inicio,
                    status="PENDENTE"
                ).exists()



                 # Apenas adiciona o horário se não houver agendamento pendente
                 if not agendamento_existente:
                    horarios_disponiveis.append({
                        "data": data_verificacao,
                        "id_horario": horario.id,
                        "hora_inicio": hora_inicio,
                        "hora_fim": hora_fim
                    })

    return {"horarios_disponiveis": horarios_disponiveis}
#####Novo endpoint
@router.get("/agendamentos/horarios/", auth=jwt_auth)
def listar_horarios_e_agendamentos(request):
    """
    Retorna todos os horários e agendamentos (passados, presentes e futuros) para o profissional autenticado.
    Caso tenha um agendamento, retorna o horário, id do agendamento, nome do paciente e tipo de seção.
    """
    user_id = request.auth  # ID do profissional autenticado

    # Obter os horários do profissional autenticado
    horarios_profissional = HorarioEspecialista.objects.filter(profissional_id=user_id)
    
    if not horarios_profissional.exists():
        return JsonResponse({"message": "Nenhum horário encontrado para este profissional."}, status=404)

    horarios_disponiveis = []
    data_atual = timezone.now().date()

    # Loop por cada horário cadastrado do profissional
    for horario in horarios_profissional:
        dia_semana = horario.dia_semana
        hora_inicio = horario.hora_inicio
        hora_fim = horario.hora_fim

        # Busca todos os agendamentos para o horário e dia da semana específico
        agendamentos = Agendamento.objects.filter(
            Q(status="PENDENTE") | Q(status="CONFIRMADO"),
            profissional_id=user_id,
            horario_id=horario.id,
          
        ).values("id", "paciente__nome", "horario__hora_inicio", "horario__hora_fim", "data", "tipo_secao")

        # Processa os agendamentos encontrados
        for agendamento in agendamentos:
            horarios_disponiveis.append({
                "id_horario": horario.id,
                "data": agendamento["data"],
                "hora_inicio": agendamento["horario__hora_inicio"],
                "hora_fim": agendamento["horario__hora_fim"],
                "id_agendamento": agendamento["id"],
                "nome_paciente": agendamento["paciente__nome"],
                "tipo_secao": agendamento["tipo_secao"],  # Adiciona o campo tipo_secao
            })

        # Adiciona horários sem agendamento para o dia da semana cadastrado
        for i in range(-365, 366):  # Considera um ano de datas passadas e futuras
            data_verificacao = data_atual + timedelta(days=i)
            dia_da_semana = DIA_SEMANA_MAPA[data_verificacao.weekday()]

            # Adiciona o horário disponível caso seja o mesmo dia da semana e não tenha agendamento
            if dia_da_semana == dia_semana and not any(
                agendamento["data"] == data_verificacao for agendamento in agendamentos
            ):
                horarios_disponiveis.append({
                    "id_horario": horario.id,
                    "data": data_verificacao,
                    "hora_inicio": hora_inicio,
                    "hora_fim": hora_fim
                })

    return JsonResponse({"horarios_disponiveis": horarios_disponiveis}, status=200)

@router.post("/agendamentos/", auth=jwt_auth)
def criar_agendamento(request, agendamento_data: AgendamentoCreateSchema):
    try:
        # Extrai o user_id do request.auth
        user_id = request.auth
        profissional = Profissional.objects.get(id=user_id)
        
        # Obtenha o paciente e o horário usando os IDs do schema
        paciente = Paciente.objects.get(id=agendamento_data.paciente_id)
        horario = HorarioEspecialista.objects.get(id=agendamento_data.horario_id)

        # Mapeamento dos valores numéricos dos dias da semana para os dias em português
        dias_semana_map = {
            0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta',
            4: 'Sexta', 5: 'Sábado', 6: 'Domingo'
        }

        # Verifique se o dia da semana do horário corresponde ao dia da semana da data
        if isinstance(agendamento_data.data, str):
            data_agendamento = datetime.strptime(agendamento_data.data, "%Y-%m-%d").date()
        elif isinstance(agendamento_data.data, date):
            data_agendamento = agendamento_data.data
        else:
            return JsonResponse({"message": "Formato de data inválido."}, status=400)

        dia_semana_agendamento = data_agendamento.weekday()  # 0 = segunda-feira, 6 = domingo
        if dias_semana_map[dia_semana_agendamento] != horario.dia_semana:
            return JsonResponse({"message": "O dia da semana da data não corresponde ao dia do horário."}, status=400)

        # Verifique se já existe um agendamento pendente para o horário
        agendamento_existente = Agendamento.objects.filter(
            profissional=profissional,
            paciente=paciente,
            horario=horario,
            data=agendamento_data.data,
            status="PENDENTE"
        ).exists()

        if agendamento_existente:
            return JsonResponse({"message": "Já existe um agendamento pendente para este horário."}, status=400)

        # Cria o novo agendamento
        novo_agendamento = Agendamento.objects.create(
            profissional=profissional,
            paciente=paciente,
            horario=horario,
            data=agendamento_data.data,
            status="PENDENTE",
            tipo_secao=agendamento_data.tipo_secao  

        )

        return JsonResponse({"message": "Agendamento criado com sucesso!", "agendamento_id": novo_agendamento.id}, status=201)

    except Profissional.DoesNotExist:
        return JsonResponse({"message": "Profissional não encontrado."}, status=404)
    except Paciente.DoesNotExist:
        return JsonResponse({"message": "Paciente não encontrado."}, status=404)
    except HorarioEspecialista.DoesNotExist:
        return JsonResponse({"message": "Horário não encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Erro ao criar agendamento: {str(e)}"}, status=500)


  ## retorna os agendamento do profissional   
@router.get("/agendamentos/profissional/", auth=jwt_auth)
def listar_agendamentos_profissional(request):
    """
    Retorna os agendamentos do profissional autenticado.
    """
    user_id = request.auth  # ID do profissional autenticado

    # Filtra os agendamentos do profissional autenticado
   
    agendamentos = Agendamento.objects.filter(profissional_id=user_id).values(
    
        "id", 
        "paciente__nome", 
        "horario",  ##retornar aqui o idhoraario
        "data", 
        "horario__hora_inicio", 
        "horario__hora_fim", 
        "status"
    )

    # Mapeia os dados necessários e retorna como JSON
    return JsonResponse({"agendamentos": list(agendamentos)}, status=200)


@router.put("/agendamentos/{agendamento_id}", auth=jwt_auth)
def atualizar_agendamento(request, agendamento_id: int, payload: AtualizarAgendamentoSchema):
    """
    Atualiza os dados de um agendamento existente.
    """
    # Busca o agendamento pelo ID ou retorna 404 se não encontrado
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)

   
    # Atualiza o status se estiver presente no payload e é um valor válido
    if payload.status and payload.status in ["PENDENTE", "CANCELADO", "CONFIRMADO"]:
        agendamento.status = payload.status
    elif payload.status:
        return {"error": "Status inválido. Use 'PENDENTE', 'CANCELADO' ou 'CONFIRMADO'."}

    # Salva as alterações no banco de dados
    agendamento.save()

    return {"message": "Agendamento atualizado com sucesso.", "agendamento": {
        "id": agendamento.id,
        "data": agendamento.data,
        "status": agendamento.status,
        "profissional_id": agendamento.profissional.id,
        "paciente_id": agendamento.paciente.id,
        "horario_id": agendamento.horario.id,
    }}

### delete agendamento
@router.delete("/agendamentos/{agendamento_id}/", auth=jwt_auth)
def deletar_agendamento(request, agendamento_id: int):
    """
    Deleta um agendamento específico do profissional autenticado.
    """
    try:
        user_id = request.auth  # Obtém o ID do profissional autenticado

        # Tenta obter o agendamento com o ID fornecido que pertence ao profissional autenticado
        agendamento = Agendamento.objects.get(id=agendamento_id, profissional_id=user_id)

        # Exclui o agendamento
        agendamento.delete()
        
        return JsonResponse({"message": "Agendamento deletado com sucesso!"}, status=200)

    except Agendamento.DoesNotExist:
        return JsonResponse({"message": "Agendamento não encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Erro ao deletar agendamento: {str(e)}"}, status=500)


@router.post("/consultas/", auth=jwt_auth)
def criar_consulta(request, consulta_data: ConsultaCreateSchema):
    try:
        # ID do profissional autenticado
        user_id = request.auth  

        # Verifica se o agendamento existe e pertence ao profissional autenticado
        agendamento = Agendamento.objects.get(id=consulta_data.agendamento_id, profissional_id=user_id)

        # Obtém os dados do paciente e do horário associados ao agendamento
        paciente = agendamento.paciente  # Paciente já está relacionado ao Agendamento
        horario = agendamento.horario  # Horário já está relacionado ao Agendamento
        profissional = agendamento.profissional
        # Cria a nova consulta vinculada ao agendamento e preenche os campos automaticamente
        nova_consulta = Consulta.objects.create(
            agendamento=agendamento,
            observacoes=consulta_data.observacoes,
            diagnostico=consulta_data.diagnostico,
            prescricoes=consulta_data.prescricoes,
            valor_consulta=profissional.valor_consulta,  # Valor da consulta, se necessário
            valor_final = profissional.valor_consulta,
            profissional=agendamento.profissional,  # Profissional vem do agendamento
            paciente=paciente,  # Paciente vem do agendamento
            link_video_chamada = consulta_data.link_video_chamada,
            data=agendamento.data,  # Data da consulta é a mesma do agendamento
            hora=horario.hora_inicio,  # Horário da consulta é o hora_inicio do agendamento
            nome_paciente=paciente.nome,  # Nome do paciente
            telefone_paciente=paciente.celular  # Telefone do paciente
        )

        # Atualiza as informações do paciente
        paciente.qtd_consultas += 1
        paciente.dt_ultima_consulta = timezone.now().date()
        paciente.save()

        return JsonResponse({"message": "Consulta criada com sucesso!", "consulta_id": nova_consulta.id}, status=201)

    except Agendamento.DoesNotExist:
        return JsonResponse({"message": "Agendamento não encontrado ou não pertence ao profissional."}, status=404)
    except HorarioEspecialista.DoesNotExist:
        return JsonResponse({"message": "Horário do agendamento não encontrado."}, status=404)
    except Paciente.DoesNotExist:
        return JsonResponse({"message": "Paciente não encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Erro ao criar consulta: {str(e)}"}, status=500)


@router.get("/consultas/", auth=jwt_auth)
def listar_consultas(request):
    user_id = request.auth  # ID do profissional autenticado
    
    # Filtra consultas apenas para os agendamentos do profissional
    consultas = Consulta.objects.filter(agendamento__profissional_id=user_id)
    
    consultas_data = [
        {
            "consulta_id": consulta.id,
            "paciente_id": consulta.paciente.id,  # Aqui pegamos o ID do paciente
            "nome_paciente": consulta.paciente.nome,  # Aqui pegamos o nome do paciente
            "telefone_paciente": consulta.paciente.celular,  # Aqui pegamos o telefone do paciente
            "horario_consulta": consulta.hora,
            "data_realizacao": consulta.data_realizacao,
            "data":consulta.data,
            "observacoes": consulta.observacoes,
            "diagnostico": consulta.diagnostico,
            "prescricoes": consulta.prescricoes,
            "valor_consulta": consulta.valor_consulta,
            "desconto": consulta.desconto,
            "valor_final_consulta": consulta.valor_final
        }
        for consulta in consultas
    ]

    return JsonResponse({"consultas": consultas_data}, status=200)


@router.get("/consultas/{consulta_id}/", auth=jwt_auth)
def obter_consulta(request, consulta_id: int):
    try:
        user_id = request.auth  # ID do profissional autenticado

        # Busca a consulta que pertence ao profissional
        consulta = Consulta.objects.get(id=consulta_id, agendamento__profissional_id=user_id)

        consulta_data = {
            "consulta_id": consulta.id,
            "data_realizacao": consulta.data_realizacao,
            "observacoes": consulta.observacoes,
            "diagnostico": consulta.diagnostico,
            "data": consulta.data,
            "prescricoes": consulta.prescricoes, 
           "valor_consulta": consulta.valor_consulta,
            "desconto": consulta.desconto
        }

        return JsonResponse({"consulta": consulta_data}, status=200)

    except Consulta.DoesNotExist:
        return JsonResponse({"message": "Consulta não encontrada ou não pertence ao profissional."}, status=404)
    
@router.put("/consultas/{consulta_id}/", auth=jwt_auth)
def atualizar_consulta(request, consulta_id: int, consulta_data: ConsultaUpdateSchema):
    try:
        user_id = request.auth  # ID do profissional autenticado

        # Busca a consulta que pertence ao profissional
        consulta = Consulta.objects.get(id=consulta_id, agendamento__profissional_id=user_id)

        # Atualiza os dados da consulta
        consulta.observacoes = consulta_data.observacoes
        consulta.diagnostico = consulta_data.diagnostico
        consulta.prescricoes = consulta_data.prescricoes
        consulta.desconto =  consulta_data.desconto
        consulta.save()

        return JsonResponse({"message": "Consulta atualizada com sucesso!"}, status=200)

    except Consulta.DoesNotExist:
        return JsonResponse({"message": "Consulta não encontrada ou não pertence ao profissional."}, status=404)


@router.delete("/consultas/{consulta_id}/", auth=jwt_auth)
def deletar_consulta(request, consulta_id: int):
    try:
        user_id = request.auth  # ID do profissional autenticado

        # Busca a consulta que pertence ao profissional
        consulta = Consulta.objects.get(id=consulta_id, agendamento__profissional_id=user_id)
        consulta.delete()

        return JsonResponse({"message": "Consulta deletada com sucesso!"}, status=200)

    except Consulta.DoesNotExist:
        return JsonResponse({"message": "Consulta não encontrada ou não pertence ao profissional."}, status=404)


@router.post("/despesas/", auth=jwt_auth)
def criar_despesa(request, payload: DespesaCreateSchema):
    user_id = request.auth
    profissional = get_object_or_404(Profissional, id=user_id)

    # Cria uma nova despesa com os dados recebidos
    nova_despesa = Despesa(
        profissional=profissional,
        descricao=payload.descricao,
        tipo=payload.tipo,
        valor=payload.valor,
        data=payload.data
    )
    nova_despesa.save()
    return {"success": True, "message": "Despesa criada com sucesso", "id_despesa": nova_despesa.id}

## lista despesas
@router.get("/despesas/", auth=jwt_auth)
def listar_despesas(request):
    user_id = request.auth
    profissional = get_object_or_404(Profissional, id=user_id)

    # Obtém todas as despesas do profissional
    despesas = Despesa.objects.filter(profissional=profissional)
    despesas_data = [
        {
            "id": despesa.id,
            "descricao": despesa.descricao,
            "tipo": despesa.tipo,
            "valor": despesa.valor,
            "data": despesa.data
        }
        for despesa in despesas
    ]
    return {"despesas": despesas_data}

## edita despesa
@router.put("/despesas/{despesa_id}/", auth=jwt_auth)
def editar_despesa(request, despesa_id: int, payload: DespesaUpdateSchema):
    user_id = request.auth
    despesa = get_object_or_404(Despesa, id=despesa_id, profissional_id=user_id)

    # Atualiza os campos da despesa com os dados recebidos
    if payload.descricao is not None:
        despesa.descricao = payload.descricao
    if payload.tipo is not None:
        despesa.tipo = payload.tipo
    if payload.valor is not None:
        despesa.valor = payload.valor
    if payload.data is not None:
        despesa.data = payload.data

    despesa.save()
    return {"success": True, "message": "Despesa atualizada com sucesso"}

## deleta despesa
@router.delete("/despesas/{despesa_id}/", auth=jwt_auth)
def deletar_despesa(request, despesa_id: int):
    user_id = request.auth
    despesa = get_object_or_404(Despesa, id=despesa_id, profissional_id=user_id)

    despesa.delete()
    return {"success": True, "message": "Despesa deletada com sucesso"}