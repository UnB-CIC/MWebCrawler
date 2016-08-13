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

class Habilitacao:
    BACHARELADO = 1856
    LICENCIATURA = 906
    ENGENHARIA_DE_COMPUTACAO = 1341
    ENGENHARIA_MECATRONICA = 6912


def cursos(codigo='\d+', nivel='graduacao', campus=DARCY_RIBEIRO):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de cursos.

    Argumentos:
    codigo -- o código do curso
            (default \d+) (todos)
    nivel -- nível acadêmico dos cursos: graduacao ou posgraduacao.
             (default graduacao)
    campus -- o campus onde o curso é oferecido: DARCY_RIBEIRO, PLANALTINA,
              CEILANDIA ou GAMA
              (default DARCY_RIBEIRO)

    O argumento 'codigo' deve ser uma expressão regular.
    """

    CURSOS = '<tr CLASS=PadraoMenor bgcolor=.*?>'\
             '<td>(\w+)</td>' \
             '<td>\d+</td>' \
             '.*?aspx\?cod=(%s)>(.*?)</a></td>' \
             '<td>(.*?)</td></tr>' % codigo

    lista = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'curso_rel', campus))
        cursos_existentes = encontra_padrao(CURSOS, pagina_html.content)
        for modalidade, codigo, denominacao, turno in cursos_existentes:
            lista[codigo] = {}
            lista[codigo]['Modalidade'] = modalidade
            lista[codigo]['Denominação'] = denominacao
            lista[codigo]['Turno'] = turno
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s em %d.\n%s' %
        #     (codigo, nivel, campus, erro)

    return lista


def disciplina(codigo, nivel='graduacao'):
    """Acessa o Matrícula Web e retorna um dicionário com as informações da
    disciplina.

    Argumentos:
    codigo -- o código da disciplina.
    nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
             (default graduacao)
    """
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
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return disc


def habilitacao(codigo, nivel='graduacao'):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de
    informações referentes a cada habilitação no curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    """
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
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return oferta


def fluxo(codigo, nivel='graduacao'):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas por período definidas no fluxo do curso.

    Argumentos:
    codigo -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    """
    PERIODO = '<b>PERÍODO: (\d+).*?CRÉDITOS:</b> (\d+)</td>(.*?)</tr></table>'
    DISCIPLINA = 'disciplina.aspx\?cod=\d+>(\d+)</a>'

    curso = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'fluxo', codigo))
        oferta = encontra_padrao(PERIODO, pagina_html.content)
        for periodo, creditos, dados in oferta:
            curso[periodo] = {}
            curso[periodo]['Créditos'] = creditos
            curso[periodo]['Disciplinas'] = encontra_padrao(DISCIPLINA, dados)
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return curso


def obrigatorias(curso, nivel='graduacao'):
    """Dado o código de um curso, acessa o Matrícula Web e retorna um
    dicionário com os códigos das disciplinas obrigatórias deste.

    Argumentos:
    curso -- o código do curso.
    nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
             (default graduacao)
    """
    OBRIGATORIAS = 'DISCIPLINAS OBRIGATÓRIAS(.*?)DISCIPLINAS OPTATIVAS'
    DISCIPLINA = 'disciplina.aspx\?cod=(\d+)>.*?</b> - (.*?)</a>'

    disciplinas = {}
    try:

        pagina_html = busca(url_mweb(nivel, 'curriculo', curso))
        disciplinas_obrigatorias = encontra_padrao(OBRIGATORIAS, pagina_html.content)
        for disciplina_obr in disciplinas_obrigatorias:
            for codigo, disciplina in encontra_padrao(DISCIPLINA, disciplina_obr):
                disciplinas[codigo] = disciplina.strip()
    except RequestException as erro:
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

    # oferta = habilitacao(680)
    # for h in oferta:
    #     print h, oferta[h]

    # periodos = fluxo(6912)  # 1856)
    # for p in periodos:
    #     print "Período ", p, periodos[p]

    # disciplinas_obrigatorias = obrigatorias(Habilitacao.MECATRONICA)
    # print 'teste'
    # for cod in disciplinas_obrigatorias:
    #     print cod, disciplinas_obrigatorias[cod]

    pass