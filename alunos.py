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
    nivel -- nível acadêmico das disciplinas buscadas
             (default Nivel.GRADUACAO)
    profundidade -- profundidade da busca
                    (default 0)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
    '''
    disciplinas = {}
    for pre_reqs in Disciplina.pre_requisitos(codigo, nivel, verbose):
        for codigo in pre_reqs:
            disciplinas[codigo] = pre_requisitos(codigo, nivel,
                                                 profundidade + 1, verbose)

    return disciplinas


if __name__ == '__main__':
    cod = 116343  # LINGUAGENS DE PROGRAMACAO
    disciplinas = pre_requisitos(cod)
    for codigo, pre_reqs in disciplinas.items():
        print codigo, pre_reqs
