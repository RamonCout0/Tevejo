from django.contrib import admin

# Register your models here.

from .models import Comunidade, Post, Comentario

admin.site.register(Comunidade)
admin.site.register(Post)
admin.site.register(Comentario)





