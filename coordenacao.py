#  -*- coding: utf-8 -*-
#       @file: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


import oferta
import curso


def alunos_matriculados(codigo, nivel='graduacao'):
    """Retorna o total de alunos matriculados em todas as turmas da disciplina
    do código dado.

    Argumentos:
    codigo -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    """
    disciplinas = oferta.turmas(cod, nivel)

    return sum([disciplinas[t]['Alunos Matriculados'] for t in disciplinas])


def demanda_nao_atendida(codigo, nivel='graduacao'):
    """Retorna o total de alunos inscritos na lista de espera da disciplina do
    código dado. Considera todas as turmas.

    Argumentos:
    codigo -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    """
    lista = oferta.lista_de_espera(cod, nivel)
    return sum(lista.values())


def monitoria(oferta_, num_bolsas):
    """Indica a distribuição de bolsas de monitoria conforme regras aprovadas
    em colegiado de curso.

    Argumentos:
    oferta_ -- um iterável cujos elementos são os códigos das disciplinas
    num_bolsas -- a quantidade de bolsas a serem distribuídas
    """
    MIN_ALUNOS_POR_TURMA = 10

    def processa(categoria, bolsas, num_bolsas):
        for k in sorted(categoria, key=categoria.get, reverse=True):
            if num_bolsas == 0:
                break

            if k not in bolsas:
                bolsas[k] = 0
            bolsas[k] += 1
            num_bolsas -= 1
        return num_bolsas

    cursos_CIC = [curso.Habilitacao.BACHARELADO,
                  curso.Habilitacao.LICENCIATURA,
                  curso.Habilitacao.ENGENHARIA_DE_COMPUTACAO,
                  curso.Habilitacao.ENGENHARIA_MECATRONICA]
    obrigatorias = {}
    for codigo in cursos_CIC:
        disciplinas_obr = curso.obrigatorias(codigo)
        for cod in disciplinas_obr:
            if cod not in obrigatorias and cod in oferta_:
                turmas = oferta.turmas(cod)
                for t in turmas:
                    key = cod + ' ' + t
                    obrigatorias[key] = turmas[t]['Alunos Matriculados']

    optativas = {}
    for cod in oferta_:
        if cod not in obrigatorias:
            turmas = oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                optativas[key] = turmas[t]['Alunos Matriculados']

    bolsas = {}
    # Regra 1
    num_bolsas = processa(obrigatorias, bolsas, num_bolsas)

    # Regra 2
    num_bolsas = processa(optativas, bolsas, num_bolsas)

    # Regra 3
    while num_bolsas > 0:
        num_bolsas = processa(obrigatorias, bolsas, num_bolsas)

    return bolsas


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        oferta_ = oferta.disciplinas(dept=sys.argv[1])
    else:
        oferta_ = oferta.disciplinas()

    # print '\nAlunos matriculados:'
    # for cod in sorted(oferta_, key=oferta_.get):
    #     alunos = alunos_matriculados(cod)
    #     if alunos > 0:
    #         print '%s %s (%d alunos)' % (cod, oferta_[cod], alunos)

    # print '\nDemanda não atendida:'
    # for cod in sorted(oferta_, key=oferta_.get):
    #     demanda = demanda_nao_atendida(cod)
    #     if demanda > 0:
    #         print '%s %s (%d alunos)' % (cod, oferta_[cod], demanda)

    print '\nMonitoria:'
    i = 1
    NUM_BOLSAS = 39
    bolsas = monitoria(oferta_, NUM_BOLSAS)
    for k in sorted(bolsas):
        cod, t = k.split(' ')
        turmas = oferta.turmas(cod)
        print i,')', cod, oferta_[cod], t, bolsas[k], '(', turmas[t]['Alunos Matriculados'],')'
        i = i + 1
