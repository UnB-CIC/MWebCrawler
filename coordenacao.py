#  -*- coding: utf-8 -*-
#    @package: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.

from mwebcrawler import Campus, Cursos, Disciplina, Nivel, Oferta


def alunos_matriculados(disciplina, nivel=Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos matriculados em todas as turmas da disciplina
    do código dado.

    Argumentos:
    disciplina -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    disciplinas = Oferta.turmas(disciplina, nivel, verbose=verbose)

    return sum([disciplinas[t]['Alunos Matriculados'] for t in disciplinas])


def demanda_nao_atendida(disciplina, nivel=Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos inscritos na lista de espera da disciplina do
    código dado. Considera todas as turmas.

    Argumentos:
    disciplina -- o código da disciplina
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    verbose -- indicação dos procedimentos sendo adotados
    '''
    lista = Oferta.lista_de_espera(disciplina, nivel=nivel, verbose=verbose)
    return sum(lista.values())


def ocupacao(oferta, cursos, nivel=Nivel.GRADUACAO, verbose=False):
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
        disciplinas = Cursos.curriculo(codigo, nivel, verbose)
        if 'obrigatórias' in disciplinas:
            obr.update(disciplinas['obrigatórias'])
        if 'optativas' in disciplinas:
            opt.update(disciplinas['optativas'])
    opt = opt.difference(obr)

    obrigatorias, optativas = {}, {}
    for cod in obr:
        if cod in oferta:
            turmas = Oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                obrigatorias[key] = turmas[t]['Alunos Matriculados']
    for cod in opt:
        if cod in oferta:
            turmas = Oferta.turmas(cod)
            for t in turmas:
                key = cod + ' ' + t
                optativas[key] = turmas[t]['Alunos Matriculados']
    return obrigatorias, optativas


def ocupacao_minima(oferta, cursos, quorum, nivel=Nivel.GRADUACAO,
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


def lista_obrigatorias(habilitacoes, deptos, nivel=Nivel.GRADUACAO,
                       campus=Campus.DARCY_RIBEIRO, verbose=False):
    '''Retorna, para cada curso dado, um dicionário contendo as disciplinas
    consideradas obrigatórias: as listadas como tal no currículo e as listadas
    como cadeias/ciclos).

    Argumentos:
    habilitacoes -- coleção de códigos de habilitações com disciplinas (da
                    oferta) em seus currículos
    deptos -- coleção de siglas de departamentos da UnB para os quais se deseja
              identificar as disciplinas obrigatórias
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    campus -- o campus onde a habilitação é oferecida: DARCY_RIBEIRO,
              PLANALTINA, CEILANDIA ou GAMA
              (default DARCY_RIBEIRO)
    verbose -- indicação dos procedimentos sendo adotados
    '''
    lista = {}
    for opcao in habilitacoes:
        lista[opcao] = {}
        curriculo = Cursos.curriculo(opcao, nivel, verbose)
        obrigatorias = curriculo.get('obrigatórias')
        for ciclo in curriculo.get('cadeias'):
            for item in curriculo['cadeias'][ciclo]:
                obrigatorias.update(item)
        for disciplina in obrigatorias:
            infos = Disciplina.informacoes(disciplina, nivel, verbose)
            depto = infos.get('Sigla do Departamento')
            if depto in deptos:
                if depto not in lista[opcao]:
                    lista[opcao][depto] = {}
                lista[opcao][depto][disciplina] = infos['Denominação']
    return lista


if __name__ == '__main__':
    # import sys
    # dept = 116 if len(sys.argv) < 2 else int(sys.argv[1])
    # nivel = Nivel.GRADUACAO if len(sys.argv) < 3 else sys.argv[2]
    # campus = Campus.DARCY_RIBEIRO
    # quorum_minimo = 1 if len(sys.argv) < 4 else int(sys.argv[3])
    # verbose = False

    # oferta = Oferta.disciplinas(dept, nivel, verbose)

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
    # cursos = Cursos.relacao(nivel, campus, verbose)
    # habilitacoes = [h
    #                 for curso in cursos
    #                 for h
    #                 in Cursos.habilitacoes(curso, nivel, campus, verbose)]
    # obr, opt = ocupacao_minima(oferta, habilitacoes, quorum_minimo, nivel,
    #                            verbose)
    # with open('obrigatorias.csv', 'w') as f:
    #     for codigo in sorted(obr, key=obr.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(obr[codigo])]) + '\n')
    # with open('optativas.csv', 'w') as f:
    #     for codigo in sorted(opt, key=opt.get, reverse=True):
    #         cod, t = codigo.split(' ')
    #         f.write(','.join([cod, oferta[cod], t, str(opt[codigo])]) + '\n')

    nivel = Nivel.GRADUACAO
    campus = Campus.DARCY_RIBEIRO
    verbose = False
    cursos = Cursos.relacao(nivel, campus, verbose)
    habilitacoes = [h for curso in cursos for h in Cursos.habilitacoes(curso)]
    # habilitacoes = [6912]  # Eng. Mecatrônica
    deptos = ['CIC']  # , 'ENE', 'ENM']
    lista = lista_obrigatorias(habilitacoes, deptos, nivel, campus, verbose)
    print lista
    pass
