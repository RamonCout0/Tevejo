from django.contrib import admin
from .models import ConteudoEducacional, Tags

admin.site.register(Tags)
admin.site.register(ConteudoEducacional)

# NÃO registre Curador aqui!
# Curador estende Usuario e já é gerenciado em usuarios/admin.py
# Registrar Curador aqui causa conflito de herança multi-tabela e 
# impede o login de superusuários no Django Admin