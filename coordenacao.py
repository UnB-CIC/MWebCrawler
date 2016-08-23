#  -*- coding: utf-8 -*-
#       @file: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.

import mwebcrawler as UnB

class CIC:
    '''Enumeração dos códigos/habilitações dos cursos associados.'''
    BACHARELADO = {'codigo': 370, 'habilitacao': 1856}
    LICENCIATURA = {'codigo': 906, 'habilitacao': 1899}
    ENGENHARIA_MECATRONICA = {'codigo': 949, 'habilitacao': 6912}
    ENGENHARIA_DE_COMPUTACAO = {'codigo': 1341, 'habilitacao': 1741}

    class ICC:
        ENGENHARIA_CIVIL = {'codigo': 582, 'habilitacao': 6220}
        ENGENHARIA_DE_PRODUCAO = {'codigo': 1376, 'habilitacao': 6017}
        ENGENHARIA_ELETRICA = {'codigo': 591, 'habilitacao': 6335}
        ENGENHARIA_FLORESTAL = {'codigo': 396, 'habilitacao': 6521}
        ENGENHARIA_MECANICA = {'codigo': 604, 'habilitacao': 6424}
        ESTATISTICA = {'codigo': 353, 'habilitacao': 1716}
        MATEMATICA = {'codigo': 141, 'habilitacao': 1341}
        MATEMATICA_LICENCIATURA = {'codigo': 141, 'habilitacao': 1325}
        MATEMATICA_NOTURNO = {'codigo': 752, 'habilitacao': 1368}


    @classmethod
    def todas_CIC(cls):
        '''Retorna a lista de todos os cursos com disciplinas obrigatórias
        do CIC em seus currículos.
        '''
        return[cls.BACHARELADO['habilitacao'],
               cls.LICENCIATURA['habilitacao'],
               cls.ENGENHARIA_DE_COMPUTACAO['habilitacao'],
               cls.ENGENHARIA_MECATRONICA['habilitacao'],
               cls.ICC.ENGENHARIA_CIVIL['habilitacao'],
               cls.ICC.ENGENHARIA_ELETRICA['habilitacao'],
               cls.ICC.ENGENHARIA_FLORESTAL['habilitacao'],
               cls.ICC.ENGENHARIA_MECANICA['habilitacao'],
               cls.ICC.ENGENHARIA_DE_PRODUCAO['habilitacao'],
               cls.ICC.ESTATISTICA['habilitacao'],
               cls.ICC.MATEMATICA['habilitacao'],
               cls.ICC.MATEMATICA_LICENCIATURA['habilitacao'],
               cls.ICC.MATEMATICA_NOTURNO['habilitacao']]


def alunos_matriculados(codigo, nivel=UnB.Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos matriculados em todas as turmas da disciplina
    do código dado.

    Argumentos:
    codigo -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    disciplinas = UnB.Oferta.turmas(codigo, nivel, verbose=verbose)

    return sum([disciplinas[t]['Alunos Matriculados'] for t in disciplinas])


def demanda_nao_atendida(codigo, nivel=UnB.Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos inscritos na lista de espera da disciplina do
    código dado. Considera todas as turmas.

    Argumentos:
    codigo -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    lista = UnB.Oferta.lista_de_espera(codigo, nivel=nivel, verbose=verbose)
    return sum(lista.values())


def ocupacao(oferta, cursos, nivel=UnB.Nivel.GRADUACAO, verbose=False):
    '''Retorna dois dicionários (obrigatórias e optativas) com o total de
    alunos inscritos em cada turma de cada disciplina ofertada por cada curso.

    Argumentos:
    oferta -- dicionário com a lista de oferta
    cursos -- lista com os cursos com disciplinas (da oferta) em seus
              curriculos
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    obr, opt = set(), set()
    for codigo in cursos:
        disciplinas = UnB.Cursos.curriculo(codigo, nivel, verbose)
        obr.update(disciplinas['obrigatórias'])
        opt.update(disciplinas['optativas'])
    opt = opt.difference(obr)

    obrigatorias, optativas = {}, {}
    for cod in obr:
        if cod in oferta:
            turmas = UnB.Oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                obrigatorias[key] = turmas[t]['Alunos Matriculados']
    for cod in opt:
        if cod in oferta:
            turmas = UnB.Oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                optativas[key] = turmas[t]['Alunos Matriculados']
    return obrigatorias, optativas


def ocupacao_minima(oferta, cursos, quorum, nivel=UnB.Nivel.GRADUACAO,
                    verbose=False):
    '''Retorna dois dicionários (obrigatórias e optativas) com o total de
    alunos inscritos em cada turma de cada disciplina ofertada cuja quantidade
    de alunos seja igual ou superior ao limite dado.

    Argumentos:
    oferta -- dicionário com a lista de oferta
    cursos -- lista com os cursos com disciplinas (da oferta) em seus
              curriculos
    quorum -- quantidade mínima de alunos em uma turma
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    obr, opt = ocupacao(oferta, cursos, nivel, verbose)

    obrigatorias = {k: v for k, v in obr.items() if v >= quorum}
    optativas = {k: v for k, v in opt.items() if v >= quorum}

    return obrigatorias, optativas


if __name__ == '__main__':
    import sys
    dept = 116 if len(sys.argv) < 2 else int(sys.argv[1])
    nivel = UnB.Nivel.GRADUACAO if len(sys.argv) < 3 else sys.argv[2]
    quorum_minimo = 1 if len(sys.argv) < 4  else int(sys.argv[3])
    verbose = False

    oferta = UnB.Oferta.disciplinas(dept, nivel, verbose)

    # print '\nAlunos matriculados:'
    # for codigo in sorted(oferta, key=oferta.get):
    #     alunos = alunos_matriculados(codigo, nivel, verbose)
    #     if alunos > 0:
    #         print '%s %s (%d alunos)' % (codigo, oferta[codigo], alunos)

    # print '\nDemanda não atendida:'
    # for codigo in sorted(oferta, key=oferta.get):
    #     demanda = demanda_nao_atendida(codigo, nivel, verbose)
    #     if demanda > 0:
    #         print '%s %s (%d alunos)' % (codigo, oferta[codigo], demanda)

    # print '\nOcupação de turmas:'
    # cursos_atendidos = CIC.todas_CIC()
    # obr, opt = ocupacao_minima(oferta, cursos_atendidos, quorum=quorum_minimo,
    #                            nivel, verbose)
    # with open('obrigatorias.csv', 'w') as f:
    #     for codigo in sorted(obr, key=obr.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(obr[codigo])]) + '\n')
    # with open('optativas.csv', 'w') as f:
    #     for codigo in sorted(opt, key=opt.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(opt[codigo])]) + '\n')

    pass
