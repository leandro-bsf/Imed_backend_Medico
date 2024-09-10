from django.contrib import admin
from .models import Profissional

@admin.register(Profissional)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone')  # Campos que você quer exibir na lista de usuários
    search_fields = ('nome', 'email')  # Campos que você quer permitir pesquisar
