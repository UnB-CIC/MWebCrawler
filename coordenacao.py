#  -*- coding: utf-8 -*-
#       @file: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


import oferta
import curso


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
    disciplinas = oferta.turmas(cod, nivel, verbose=verbose)

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
    lista = oferta.lista_de_espera(cod, nivel, verbose=verbose)
    return sum(lista.values())


def ocupacao(oferta_, cursos, nivel='graduacao', verbose=False):
    '''Retorna dois dicionários (obrigatórias e optativas) com o total de
    alunos inscritos em cada turma de cada disciplina ofertada.

    Argumentos:
    oferta_ -- dicionário com a lista de oferta
    cursos -- lista com os cursos com disciplinas (da oferta) em seus curriculos
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    obr, opt = set(), set()
    for codigo in cursos:
        disciplinas = curso.curriculo(codigo, nivel, verbose)
        obr.update(disciplinas['obrigatórias'])
        opt.update(disciplinas['optativas'])
    opt = opt.difference(obr)

    obrigatorias, optativas = {}, {}
    for cod in obr:
        if cod in oferta_:
            turmas = oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                obrigatorias[key] = turmas[t]['Alunos Matriculados']
    for cod in opt:
        if cod in oferta_:
            turmas = oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                optativas[key] = turmas[t]['Alunos Matriculados']
    return obrigatorias, optativas


def ocupacao_minima(oferta_, cursos, quorum, nivel='graduacao', verbose=False):
    '''Retorna dois dicionários (obrigatórias e optativas) com o total de
    alunos inscritos em cada turma de cada disciplina ofertada cuja quantidade
    de alunos seja igual ou superior ao limite dado.

    Argumentos:
    oferta_ -- dicionário com a lista de oferta
    cursos -- lista com os cursos com disciplinas (da oferta) em seus curriculos
    quorum -- quantidade mínima de alunos em uma turma
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    obr, opt = ocupacao(oferta_, cursos, nivel, verbose)

    obrigatorias = {k: v for k, v in obr.items() if v >= quorum}
    optativas = {k: v for k, v in opt.items() if v >= quorum}

    return obrigatorias, optativas


if __name__ == '__main__':
    import sys

    quorum_minimo = 1

    if len(sys.argv) > 1:
        oferta_ = oferta.disciplinas(dept=sys.argv[1])
        if len(sys.argv) > 2:
            quorum_minimo = int(sys.argv[2])
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


    # '\nOcupação de turmas:'
    cursos_atendidos = curso.UnB.Habilitacao.todas_CIC()
    obr, opt = ocupacao_minima(oferta_, cursos_atendidos, quorum_minimo)
    with open('obrigatorias.csv', 'w') as f:
        for codigo in sorted(obr, key=obr.get, reverse=True):
            cod, t = codigo.split(' ')
            f.write(','.join([cod, oferta_[cod], t, str(obr[codigo])]) + '\n')
    with open('optativas.csv', 'w') as f:
        for codigo in sorted(opt, key=opt.get, reverse=True):
            cod, t = codigo.split(' ')
            f.write(','.join([cod, oferta_[cod], t, str(opt[codigo])]) + '\n')
