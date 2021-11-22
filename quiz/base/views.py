from django.db.models import Sum
from django.shortcuts import render, redirect

from quiz.base.forms import AlunoForm
from quiz.base.models import Pergunta, Aluno, Resposta


def home(request):
    if request.method == 'POST':
        # usuario ja existe
        email = request.POST['email']
        try:
            aluno = Aluno.objects.get(email=email)
            return redirect('/classificacao/')
        except Aluno.DoesNotExist:
            # usuario nao existe
            formulario = AlunoForm(request.POST)
            if formulario.is_valid():
                aluno = formulario.save()
                request.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                contexto = {'formulario': formulario}
                return render(request, 'base/home.html', contexto)
        else:
            request.session['aluno_id'] = aluno.id
            return redirect('/perguntas/1')

    return render(request, 'base/home.html')


PONTUACAO_MAXIMA = 500
erradas = 0


def perguntas(request, indice):
    global erradas
    try:
        aluno_id = request.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        try:
            pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
        except IndexError:
            erradas = 0
            return redirect('/classificacao')
        else:
            contexto = {'indice_da_questao': indice, 'pergunta': pergunta}
            if request.method == 'POST':
                resposta_indice = int(request.POST['resposta_indice'])
                if resposta_indice == pergunta.alternativa_correta:
                    # Armazenar dados da resposta
                    pontos = max(PONTUACAO_MAXIMA - erradas, 10)
                    Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=pontos).save()
                    erradas = 0
                    return redirect(f'/perguntas/{indice + 1}')
                else:
                    erradas += 50
                    contexto['resposta_indice'] = resposta_indice

            return render(request, 'base/game.html', context=contexto)


def classificacao(request):
    try:
        aluno_id = request.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        pontos_dct = Resposta.objects.filter(aluno_id=aluno_id).aggregate(Sum('pontos'))
        pontuacao_do_aluno = pontos_dct['pontos__sum']

        numero_de_aluno_com_maior_pontuacao = Resposta.objects.values('aluno').annotate(Sum('pontos')).filter(
            pontos__sum__gt=pontuacao_do_aluno).count()
        primeiros_alunos_da_classificacao = list(
            Resposta.objects.values('aluno', 'aluno__nome').annotate(Sum('pontos')).order_by('-pontos__sum')[:5]
        )
        contexto = {
            'pontuacao_do_aluno': pontuacao_do_aluno,
            'posicao_do_aluno': numero_de_aluno_com_maior_pontuacao + 1,
            'primeiros_alunos_da_classificacao': primeiros_alunos_da_classificacao
        }
        return render(request, 'base/classificacao.html', contexto)
