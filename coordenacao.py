#  -*- coding: utf-8 -*-
#    @package: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.

from mwebcrawler import (Campus, Cursos, Departamento, Disciplina,
                         Habilitacoes, Nivel, Oferta)


def alunos_matriculados(disciplina, depto=Departamento.CIC,
                        nivel=Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos matriculados em todas as turmas da disciplina
    do código dado.

    Argumentos:
    disciplina -- o código da disciplina
    nivel -- nível acadêmico da disciplina buscada
             (default Nivel.GRADUACAO)
    depto -- o código do departamento que oferece a disciplina
             (default Departamento.CIC)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
    '''
    disciplinas = Oferta.turmas(disciplina, depto, nivel, verbose)

    return sum([disciplinas[t]['Alunos Matriculados'] for t in disciplinas])


def demanda_nao_atendida(disciplina, nivel=Nivel.GRADUACAO, verbose=False):
    '''Retorna o total de alunos inscritos na lista de espera da disciplina do
    código dado. Considera todas as turmas.

    Argumentos:
    disciplina -- o código da disciplina
    nivel -- nível acadêmico da disciplina buscada
             (default Nivel.GRADUACAO)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
    '''
    lista = Oferta.lista_de_espera(disciplina, nivel=nivel, verbose=verbose)
    return sum(lista.values())


def ocupacao(oferta, cursos, nivel=Nivel.GRADUACAO, verbose=False):
    '''Retorna dois dicionários (obrigatórias e optativas) com o total de
    alunos inscritos em cada turma de cada disciplina ofertada por cada curso.

    Argumentos:
    oferta -- dicionário com a lista de oferta
    cursos -- lista com os cursos com disciplinas (da oferta) em seus
              currículos
    nivel -- nível acadêmico da disciplina buscada
             (default Nivel.GRADUACAO)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
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
              currículos
    quorum -- quantidade mínima de alunos em uma turma
    nivel -- nível acadêmico das disciplinas buscadas
             (default Nivel.GRADUACAO)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
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
    nivel -- nível acadêmico das disciplinas buscadas
             (default Nivel.GRADUACAO)
    campus -- o campus onde a habilitação é oferecida
              (default Campus.DARCY_RIBEIRO)
    verbose -- indicação dos procedimentos sendo adotados
               (default False)
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




def turmas_reservadas_no_fluxo(habilitacao, filtro_reserva=''):
    '''Mostra a lista de turmas com reserva de vagas das disciplinas do fluxo
    da habilitação dada.

    Argumentos:
    habilitacao -- código da habilitação com disciplinas da oferta
    filtro_reserva -- filtro para reduzir o escopo da busca
                      (default '')
    '''
    fluxo = Cursos.fluxo(habilitacao)

    for periodo in sorted(fluxo.keys()):
        print('Período: %d' % periodo)
        for disciplina in fluxo[periodo]['Disciplinas']:
            turmas = Oferta.turmas(disciplina).items()
            for turma, detalhes in turmas:
                if 'Turma Reservada' in detalhes:
                    for reserva, vagas in detalhes['Turma Reservada'].items():
                        if filtro_reserva in reserva:
                            print('\t  %s (%s) %s %s' % (disciplina, turma,
                                                         reserva, vagas))


if __name__ == '__main__':
    nivel = Nivel.GRADUACAO
    verbose = False
    depto = str(Departamento.CIC)

    # turmas_reservadas_no_fluxo(6912, 'Mecatrônica')

    oferta = Oferta.disciplinas(depto, nivel, verbose)

    print '\nAlunos matriculados no Departamento %s:' % depto
    for codigo in sorted(oferta, key=oferta.get):
        alunos = alunos_matriculados(codigo, depto, nivel, verbose)
        if alunos > 0:
            print '%s %s (%d alunos)' % (codigo, oferta[codigo], alunos)

    print '\nDemanda não atendida:'
    for codigo in sorted(oferta, key=oferta.get):
        demanda = demanda_nao_atendida(codigo, nivel, verbose)
        if demanda > 0:
            print '%s %s (%d alunos)' % (codigo, oferta[codigo], demanda)

    print '\nOcupação de turmas:'
    habilitacoes = [Habilitacoes.BCC, Habilitacoes.LIC, Habilitacoes.ENC,
                    Habilitacoes.ENM]
    obr, opt = ocupacao_minima(oferta, habilitacoes, 1, nivel, verbose)

    print('\tObrigatórias')
    for codigo in sorted(obr, key=obr.get, reverse=True):
        cod, t = codigo.split(' ')
        print('\t%s' % ','.join([cod, oferta[cod], t, str(obr[codigo])]))
    print('\n116479\tOptativas')
    for codigo in sorted(opt, key=opt.get, reverse=True):
        cod, t = codigo.split(' ')
        print('\t%s' % ','.join([cod, oferta[cod], t, str(opt[codigo])]))

    print('Disciplinas obrigatórias de um curso')
    deptos = ['CIC']
    campus = Campus.DARCY_RIBEIRO
    lista = lista_obrigatorias([Habilitacoes.ENM], deptos, nivel, campus,
                               verbose)
    print lista
