#  -*- coding: utf-8 -*-
#       @file: curso.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de web-crawling para buscar informações da lista de cursos da UnB. O
# programa busca as informações com base em expressões regulares que, assume-se
# representam a estrutura de uma página do Matrícula Web. Caso esta estrutura
# seja alterada, as expressões aqui precisam ser atualizadas de acordo.
#
# Erros em requests são ignorados silenciosamente.


from utils import *


class UnB:
    class Curso:
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


def cursos(codigo='\d+', nivel='graduacao', campus=DARCY_RIBEIRO, verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com a lista de cursos.

    Argumentos:
    codigo -- o código do curso
            (default \d+) (todos)
    nivel -- nível acadêmico dos cursos: graduacao ou posgraduacao.
             (default graduacao)
    campus -- o campus onde o curso é oferecido: DARCY_RIBEIRO, PLANALTINA,
              CEILANDIA ou GAMA
              (default DARCY_RIBEIRO)
    verbose -- indicação dos procedimentos sendo adotados

    O argumento 'codigo' deve ser uma expressão regular.
    '''

    CURSOS = '<tr CLASS=PadraoMenor bgcolor=.*?>'\
             '<td>(\w+)</td>' \
             '<td>\d+</td>' \
             '.*?aspx\?cod=(%s)>(.*?)</a></td>' \
             '<td>(.*?)</td></tr>' % codigo

    lista = {}
    try:
        if verbose:
            log('Buscando lista de cursos')
        pagina_html = busca(url_mweb(nivel, 'curso_rel', campus))
        cursos_existentes = encontra_padrao(CURSOS, pagina_html.content)

        if verbose:
            log('Processando a lista de cursos')
        for modalidade, codigo, denominacao, turno in cursos_existentes:
            lista[codigo] = {}
            lista[codigo]['Modalidade'] = modalidade
            lista[codigo]['Denominação'] = denominacao
            lista[codigo]['Turno'] = turno
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s em %d.\n%s' %
        #     (codigo, nivel, campus, erro)

    return lista


def disciplina(codigo, nivel='graduacao', verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com as informações da
    disciplina.

    Argumentos:
    codigo -- o código da disciplina.
    nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
             (default graduacao)
    verbose -- indicação dos procedimentos sendo adotados
    '''
    DISCIPLINAS = 'Órgão:</b> </td><td>(\w+) - (.*?)</td></tr>' \
                  '.*?' \
                  'Denominação:</b> </td><td>(.*?)</td></tr>' \
                  '.*?' \
                  'Nível:</b> </td><td>(.*?)</td></tr>' \
                  '.*?' \
                  'Vigência:</b> </td><td>(.*?)</td></tr>' \
                  '.*?' \
                  'Pré-req:</b> </td><td class=PadraoMenor>(.*?)</td></tr>' \
                  '.*?' \
                  'Ementa:</b> </td><td class=PadraoMenor>' \
                  '<p align=justify>(.*?)</P></td></tr>' \
                  '.*?' \
                  'Programa:</b> </td><td class=PadraoMenor>' \
                  '<p align=justify>(.*?)</P></td></tr>' \
                  '.*?' \
                  'Bibliografia:</b> </td><td class=PadraoMenor>' \
                  '<p align=justify>(.*?)</P></td></tr>'

    disc = {}
    try:
        if verbose:
            log('Buscando informações da disciplina ' + str(codigo))
        pagina_html = busca(url_mweb(nivel, 'disciplina', codigo))
        ofertadas = encontra_padrao(DISCIPLINAS, pagina_html.content)
        disc['Código do Departamento'] = ofertadas[0][0]
        disc['Nome do Departamento'] = ofertadas[0][1]
        disc['Denominação'] = ofertadas[0][2]
        disc['Nivel'] = ofertadas[0][3]
        disc['Vigência'] = ofertadas[0][4]
        disc['Pré-requisitos'] = ofertadas[0][5].replace('<br>', ' ')
        disc['Ementa'] = ofertadas[0][6].replace('<br />', '\n')
        disc['Programa'] = ofertadas[0][7].replace('<br />', '\n')
        disc['Bibliografia'] = ofertadas[0][8].replace('<br />', '\n')
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return disc


def habilitacao(codigo, nivel='graduacao', verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com a lista de
    informações referentes a cada habilitação no curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    verbose -- indicação dos procedimentos sendo adotados
    '''
    OPCAO = '<a href=curriculo.aspx\?cod=(\d+)>' \
            '.*?' \
            'Grau: </td><td .*?>(\w+)</td>' \
            '.*?' \
            'Limite mínimo de permanência: </td>' \
            '<td align=right>(\d+)</td>' \
            '.*?' \
            'Limite máximo de permanência: </td>' \
            '<td align=right>(\d+)</td>' \
            '.*?' \
            'Quantidade de Créditos para Formatura: </td>' \
            '<td align=right>(\d+)</td>' \
            '.*?' \
            'Quantidade mínima de Créditos Optativos ' \
            'na Área de Concentração: </td>' \
            '<td align=right>(\d+)</td>' \
            '.*?' \
            'Quantidade mínima de Créditos Optativos na Área Conexa: </td>' \
            '<td align=right>(\d+)</td>' \
            '.*?' \
            'Quantidade máxima de Créditos no Módulo Livre: </td>' \
            '<td align=right>(\d+)</td>'

    curso = {}
    try:
        if verbose:
            log('Buscando informações da habilitação do curso ' + str(codigo))
        pagina_html = busca(url_mweb(nivel, 'curso_dados', codigo))
        oferta = encontra_padrao(OPCAO, pagina_html.content)
        for opcao, grau, min, max, formatura, obr, opt, livre in oferta:
            curso[opcao] = {}
            curso[opcao]['Grau'] = grau
            curso[opcao]['Limite mínimo de permanência'] = min
            curso[opcao]['Limite máximo de permanência'] = max
            curso[opcao]['Quantidade de Créditos para Formatura'] = formatura
            curso[opcao]['Quantidade mínima de Créditos Optativos na Área de Concentração'] = obr
            curso[opcao]['Quantidade mínima de Créditos Optativos na Área Conexa'] = opt
            curso[opcao]['Quantidade máxima de Créditos no Módulo Livre'] = livre
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return curso


def fluxo(codigo, nivel='graduacao', verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas por período definidas no fluxo do curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    verbose -- indicação dos procedimentos sendo adotados
    '''
    PERIODO = '<b>PERÍODO: (\d+).*?CRÉDITOS:</b> (\d+)</td>(.*?)</tr></table>'
    DISCIPLINA = 'disciplina.aspx\?cod=\d+>(\d+)</a>'

    curso = {}
    try:
        if verbose:
            log('Buscando disciplinas no fluxo do curso ' + str(codigo))
        pagina_html = busca(url_mweb(nivel, 'fluxo', codigo))
        oferta = encontra_padrao(PERIODO, pagina_html.content)
        for periodo, creditos, dados in oferta:
            periodo = int(periodo)
            curso[periodo] = {}
            curso[periodo]['Créditos'] = creditos
            curso[periodo]['Disciplinas'] = encontra_padrao(DISCIPLINA, dados)
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return curso

def curriculo(codigo, nivel='graduacao', verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas definidas no currículo do curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    verbose -- indicação dos procedimentos sendo adotados
    '''

    OBR_OPT = 'DISCIPLINAS OBRIGATÓRIAS (.*?)</table></td>.*?DISCIPLINAS OPTATIVAS (.*?)</table></td>'
    DISCIPLINA = 'disciplina.aspx\?cod=(\d+)>.*?</b> - (.*?)</a>'

    disciplinas = {}
    try:
        if verbose:
            log('Buscando lista de disciplinas do currículo do curso ' + str(codigo))
        pagina_html = busca(url_mweb(nivel, 'curriculo', codigo))
        lista_de_disciplinas = encontra_padrao(OBR_OPT, pagina_html.content)
        for obrigatorias, optativas in lista_de_disciplinas:
            disciplinas['obrigatórias'] = {cod:disc.strip() for cod, disc in encontra_padrao(DISCIPLINA, obrigatorias)}
            disciplinas['optativas'] = {cod:disc.strip() for cod, disc in encontra_padrao(DISCIPLINA, optativas)}
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return disciplinas


if __name__ == '__main__':
    # cursos_ = cursos()
    # for c in cursos_:
    #     print c, cursos_[c]

    # d = disciplina(181196)
    # for c in d:
    #     print c, d[c]

    # oferta = habilitacao(370)
    # for h in oferta:
    #     print h, oferta[h]

    # periodos = fluxo(6912)  # 1856)
    # for p in sorted(periodos):
    #     print "Período ", p, periodos[p]

    # disciplinas = curriculo(1856)
    # for p in sorted(disciplinas):
    #     print p, disciplinas[p]

    pass
