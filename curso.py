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


def curriculo(codigo, nivel='graduacao', verbose=False):
    '''Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas definidas no currículo do curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    verbose -- indicação dos procedimentos sendo adotados
    '''

    OBR_OPT = 'DISCIPLINAS OBRIGATÓRIAS (.*?)</table></td>.*?' \
              'DISCIPLINAS OPTATIVAS (.*?)</table></td>'
    DISCIPLINA = 'disciplina.aspx\?cod=(\d+)>.*?</b> - (.*?)</a>'

    disciplinas = {}
    try:
        if verbose:
            log('Buscando currículo do curso ' + str(codigo))
        pagina_html = busca(url_mweb(nivel, 'curriculo', codigo))
        lista_de_disciplinas = encontra_padrao(OBR_OPT, pagina_html.content)
        for obrigatorias, optativas in lista_de_disciplinas:
            disciplinas['obrigatórias'] = {}
            for cod, disc in encontra_padrao(DISCIPLINA, obrigatorias):
                disciplinas['obrigatórias'][cod] = disc.strip()
            disciplinas['optativas'] = {}
            for cod, disc in encontra_padrao(DISCIPLINA, optativas):
                disciplinas['optativas'][cod] = disc.strip()
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return disciplinas


def cursos(codigo='\d+', nivel='graduacao',
           campus=UnBEnum.Campus.DARCY_RIBEIRO, verbose=False):
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
            curso[opcao]['Créditos para Formatura'] = formatura
            curso[opcao]['Mínimo de Créditos Optativos na '
                         'Área de Concentração'] = obr
            curso[opcao]['Quantidade mínima de Créditos Optativos na '
                         'Área Conexa'] = opt
            curso[opcao]['Quantidade máxima de Créditos no '
                         'Módulo Livre'] = livre
    except RequestException:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return curso


if __name__ == '__main__':
    # curriculo_ = curriculo(1856)
    # for disciplina in sorted(curriculo_):
    #     print disciplina, curriculo_[disciplina]

    # cursos_ = cursos()
    # for c in cursos_:
    #     print c, cursos_[c]

    # disciplinas = disciplina(181196)
    # for codigo in disciplinas:
    #     print codigo, disciplinas[codigo]

    # habilitacao_ = habilitacao(370)
    # for info in habilitacao_:
    #     print info, habilitacao_[info]

    # periodos = fluxo(6912)  # 1856)
    # for p in sorted(periodos):
    #     print "Período ", p, periodos[p]

    pass
