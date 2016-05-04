#  -*- coding: utf-8 -*-
#       @file: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


import oferta


def alunos_matriculados(codigo, curso='graduacao'):
    """Retorna o total de alunos matriculados em todas as turmas da disciplina
    do código dado.

    Argumentos:
    codigo -- o código da disciplina
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    """
    disciplinas = oferta.turmas(cod)
    return sum([disciplinas[turma]['matriculados'] for turma in disciplinas])


def demanda_nao_atendida(codigo, curso='graduacao'):
    """Retorna o total de alunos inscritos na lista de espera da disciplina do
    código dado. Considera todas as turmas.

    Argumentos:
    codigo -- o código da disciplina
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    """
    lista = oferta.lista_de_espera(cod)
    return sum(lista.values())


def monitoria(oferta_, num_bolsas):
    """Indica a distribuição de bolsas de monitoria conforme regras aprovadas
    em colegiado de curso.

    Argumentos:
    oferta_ -- um iterável cujos elementos são os códigos das disciplinas
    num_bolsas -- a quantidade de bolsas a serem distribuídas
    """
    def processa(categoria, disciplinas, num_bolsas):
        for k in sorted(categoria, key=categoria.get, reverse=True):
            if num_bolsas == 0:
                break

            cod, t = k.split()
            turma = disciplinas[cod][t]
            turma['monitores'] += 1
            num_bolsas -= 1
            categoria[k] = turma['matriculados'] / turma['monitores']
        return num_bolsas

    disciplinas = {}
    obrigatorias, optativas = {}, {}
    for cod in oferta_:
        disciplinas[cod] = oferta.turmas(cod)
        for t in disciplinas[cod]:
            turma = disciplinas[cod][t]
            turma['monitores'] = 0
            # @to-do Confirmar se a existência de reserva implica na disciplina
            # ser obrigatória. O jeito "certo" seria buscar no fluxo de cada
            # curso...
            if 'reserva' in turma:
                obrigatorias[cod + ' ' + t] = turma['matriculados']
            else:
                optativas[cod + ' ' + t] = turma['matriculados']

    # Regra 1
    num_bolsas = processa(obrigatorias, disciplinas, num_bolsas)

    # Regra 2
    if num_bolsas > 0:
        num_bolsas = processa(optativas, disciplinas, num_bolsas)

    # Regra 3
    if num_bolsas > 0:
        todas = obrigatorias.copy()
        todas.update(optativas)
        while num_bolsas > 0:
            num_bolsas = processa(todas, disciplinas, num_bolsas)

    bolsas = {}
    for cod in disciplinas:
        for t in disciplinas[cod]:
            turma = disciplinas[cod][t]
            if turma['monitores'] > 0:
                bolsas[cod + ' ' + t] = turma['monitores']

    return bolsas


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        oferta_ = oferta.disciplinas(dept=sys.argv[1])
    else:
        oferta_ = oferta.disciplinas()

    print '\nAlunos matriculados:'
    for cod in sorted(oferta_, key=oferta_.get):
        alunos = alunos_matriculados(cod)
        if alunos > 0:
            print '%s %s (%d alunos)' % (cod, oferta_[cod], alunos)

    print '\nDemanda não atendida:'
    for cod in sorted(oferta_, key=oferta_.get):
        demanda = demanda_nao_atendida(cod)
        if demanda > 0:
            print '%s %s (%d alunos)' % (cod, oferta_[cod], demanda)

    print '\nMonitoria:'
    bolsas = monitoria(oferta_, 39)
    for cod in sorted(bolsas):
        print cod, bolsas[cod]
