#  -*- coding: utf-8 -*-
#       @file: alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para alunos.


import oferta


def pre_requisitos(codigo, prefixo=''):
    '''Dado o código de uma disciplina, obtém recursivamente a lista de
    disciplinas que são pré-requisitos para o código dado e as escreve na saída
    padrão, acrescentando um caractere de tabulação ao prefixo a cada nível de
    profundidade.

    Argumentos:
    codigo -- o código do Departamento que oferece as disciplinas
            (default 116)
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao.
    '''
    print '%s%s' % (prefixo, codigo)
    prefixo = '\t' + prefixo
    for preq in oferta.pre_requisitos(codigo):
        for c in preq:
            pre_requisitos(c, prefixo)
