#  -*- coding: utf-8 -*-
#       @file: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.

import mwebcrawler as UnB

class Curso:
    '''Enumeração dos códigos de cursos.'''
    BACHARELADO = 370
    LICENCIATURA = 906
    ENGENHARIA_DE_COMPUTACAO = 1341
    ENGENHARIA_MECATRONICA = 949
    ESTATISTICA = 353
    ENGENHARIA_MECANICA = 604
    MATEMATICA = 141
    MATEMATICA_NOTURNO = 752
    MATEMATICA_LICENCIATURA = 141
    ENGENHARIA_ELETRICA = 591
    ENGENHARIA_CIVIL = 582
    ENGENHARIA_FLORESTAL = 396
    ENGENHARIA_DE_PRODUCAO = 1376

class Habilitacao:
    '''Enumeração de habilitação de cursos.'''
    BACHARELADO = 1856
    LICENCIATURA = 1899
    ENGENHARIA_DE_COMPUTACAO = 1741
    ENGENHARIA_MECATRONICA = 6912
    ESTATISTICA = 1716
    ENGENHARIA_MECANICA = 6424
    MATEMATICA = 1341
    MATEMATICA_NOTURNO = 1368
    MATEMATICA_LICENCIATURA = 1325
    ENGENHARIA_ELETRICA = 6335
    ENGENHARIA_CIVIL = 6220
    ENGENHARIA_FLORESTAL = 6521
    ENGENHARIA_DE_PRODUCAO = 6017

    @classmethod
    def todas_CIC(cls):
        '''Retorna a lista de todos os cursos com disciplinas obrigatórias
        do CIC em seus currículos.
        '''
        return[cls.BACHARELADO,
               cls.LICENCIATURA,
               cls.ENGENHARIA_DE_COMPUTACAO,
               cls.ENGENHARIA_MECATRONICA,
               cls.ENGENHARIA_CIVIL,
               cls.ENGENHARIA_ELETRICA,
               cls.ENGENHARIA_FLORESTAL,
               cls.ENGENHARIA_MECANICA,
               cls.ENGENHARIA_DE_PRODUCAO,
               cls.ESTATISTICA,
               cls.MATEMATICA,
               cls.MATEMATICA_LICENCIATURA,
               cls.MATEMATICA_NOTURNO]


def alunos_matriculados(codigo, nivel='graduacao', verbose=False):
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


def demanda_nao_atendida(codigo, nivel='graduacao', verbose=False):
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


def ocupacao(oferta, cursos, nivel='graduacao', verbose=False):
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


def ocupacao_minima(oferta, cursos, quorum, nivel='graduacao', verbose=False):
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
    dept = 116
    nivel = 'graduacao'
    verbose = True
    quorum_minimo = 1

    import sys
    if len(sys.argv) > 1:
        dept = sys.argv[1]
    if len(sys.argv) > 2:
        nivel = sys.argv[1]
    if len(sys.argv) > 3:
        quorum_minimo = int(sys.argv[2])

    oferta = UnB.Oferta.disciplinas(dept=dept, nivel=nivel, verbose=verbose)

    # print '\nAlunos matriculados:'
    # for codigo in sorted(oferta, key=oferta.get):
    #     alunos = alunos_matriculados(codigo, nivel=nivel, verbose=verbose)
    #     if alunos > 0:
    #         print '%s %s (%d alunos)' % (codigo, oferta[codigo], alunos)

    # print '\nDemanda não atendida:'
    # for codigo in sorted(oferta, key=oferta.get):
    #     demanda = demanda_nao_atendida(codigo, nivel=nivel, verbose=verbose)
    #     if demanda > 0:
    #         print '%s %s (%d alunos)' % (codigo, oferta[codigo], demanda)

    # print '\nOcupação de turmas:'
    # cursos_atendidos = Habilitacao.todas_CIC()
    # obr, opt = ocupacao_minima(oferta, cursos_atendidos, quorum=quorum_minimo,
    #                            nivel=nivel, verbose=verbose)

    # with open('obrigatorias.csv', 'w') as f:
    #     for codigo in sorted(obr, key=obr.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(obr[codigo])]) + '\n')
    # with open('optativas.csv', 'w') as f:
    #     for codigo in sorted(opt, key=opt.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(opt[codigo])]) + '\n')

    pass
