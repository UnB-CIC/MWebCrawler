#  -*- coding: utf-8 -*-
#    @package: alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para alunos.


from mwebcrawler import Disciplina, Nivel


def pre_requisitos(codigo, nivel=Nivel.GRADUACAO, profundidade=0,
                   verbose=False):
    '''Dado o código de uma disciplina, obtém recursivamente a lista de
    disciplinas que são pré-requisitos para o código dado e as escreve na saída
    padrão, acrescentando um caractere de tabulação ao prefixo a cada nível de
    profundidade.

    Argumentos:
    codigo -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    profundidade -- profundidade da busca
    verbose -- indicação dos procedimentos sendo adotados
    '''
    disciplinas = {}
    for prerequisitos in Disciplina.pre_requisitos(codigo, nivel, verbose):
        for pr in prerequisitos:
            prs = pre_requisitos(pr, nivel, profundidade + 1, verbose)
            disciplinas[pr] = prs

    return disciplinas


if __name__ == '__main__':
    disciplinas = pre_requisitos(116343)
    for disciplina in disciplinas:
        print disciplina, disciplinas[disciplina]

    pass
