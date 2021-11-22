from django.contrib import admin

from quiz.base.models import Pergunta, Aluno, Resposta


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'enunciado', 'disponivel', 'alternativa_correta')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'criado_em')


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('respondia_em', 'aluno', 'pergunta', 'pontos')
