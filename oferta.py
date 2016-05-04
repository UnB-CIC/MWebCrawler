#  -*- coding: utf-8 -*-
#       @file: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de web-crawling para buscar informações da lista de oferta de cursos
# da UnB. O programa busca as informações com base em expressões regulares que,
# assume-se, representam a estrutura de uma página do Matrícula Web. Caso esta
# estrutura seja alterada, as expressões aqui precisam ser atualizadas de
# acordo.
#
# Erros em requests são ignorados silenciosamente.


from utils import *


def departamentos(codigo='\d+', nivel='graduacao', campus=DARCY_RIBEIRO):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de
    departamentos com ofertas.

    Argumentos:
    codigo -- o código do Departamento.
            (default \d+)
    nivel -- nível acadêmico do Departamento: graduacao ou posgraduacao.
             (default graduacao)
    campus -- o campus onde o curso é oferecido: DARCY_RIBEIRO, PLANALTINA,
              CEILANDIA ou GAMA
              (default DARCY_RIBEIRO)


    O argumento 'codigo' deve ser uma expressão regular.
    """
    DEPARTAMENTOS = '<tr CLASS=PadraoMenor bgcolor=.*?>'\
                    '<td>\d+</td><td>(\w+)</td>' \
                    '.*?aspx\?cod=(%s)>(.*?)</a></td></tr>' % codigo

    deptos = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'oferta_dep', campus))
        deptos_existentes = encontra_padrao(DEPARTAMENTOS, pagina_html.content)
        for codigo, sigla, denominacao in deptos_existentes:
            deptos[codigo] = {}
            deptos[codigo]['sigla'] = sigla
            deptos[codigo]['denominacao'] = denominacao
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return deptos


def disciplinas(dept=116, nivel='graduacao'):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas ofertadas por um departamento.

    Argumentos:
    dept -- o código do Departamento que oferece as disciplinas
            (default 116)
    nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao.
             (default graduacao)

    Lista completa dos Departamentos da UnB:
    matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=1
    """
    DISCIPLINAS = 'oferta_dados.aspx\?cod=(\d+).*?>(.*?)</a>'

    oferta = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'oferta_dis', dept))
        ofertadas = encontra_padrao(DISCIPLINAS, pagina_html.content)
        for codigo, nome in ofertadas:
            oferta[codigo] = nome
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return oferta


def lista_de_espera(codigo, turma='\w+', nivel='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
    dicionário com a lista de espera para as turmas ofertadas da disciplina.

    Argumentos:
    codigo -- o código da disciplina
    turma -- identificador da turma
             (default '\w+') (todas as disciplinas)
    nivel -- nível acadêmico da disciplina buscada: graduacao ou posgraduacao.
             (default graduacao).

    O argumento 'turma' deve ser uma expressão regular.
    """
    TABELA = '<td><b>Turma</b></td>    ' \
             '<td><b>Vagas<br>Solicitadas</b></td>  </tr>' \
             '<tr CLASS=PadraoMenor bgcolor=.*?>  ' \
             '.*?</tr><tr CLASS=PadraoBranco>'
    TURMAS = '<td align=center >(%s)</td>  ' \
             '<td align=center >(\d+)</td></tr>' % turma

    demanda = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'faltavaga_rel', codigo))
        turmas_com_demanda = encontra_padrao(TABELA, pagina_html.content)
        for tabela in turmas_com_demanda:
            for turma, vagas_desejadas in encontra_padrao(TURMAS, tabela):
                vagas = int(vagas_desejadas)
                if vagas > 0:
                    demanda[turma] = vagas
    except RequestException as erro:
        pass
        #print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return demanda


def pre_requisitos(codigo, nivel='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna uma
    lista com os códigos das disciplinas que são pré-requisitos para a dada.

    Argumentos:
    codigo -- o código da disciplina.
    nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
             (default graduacao)

    Cada item da lista tem uma relação 'OU' com os demais, e cada item é uma
    outra lista cujos itens têm uma relaçã 'E' entre si. Por exemplo: o
    resultado da busca por 116424 (Transmissão de Dados) é:
    [['117251'], ['116394', '113042']]
    que deve ser lido como
    ['117251'] OU ['116394' E '113042']

    Ou seja, para cursar a disciplina 116424, é preciso ter sido aprovado na
    disciplina 117251(ARQ DE PROCESSADORES DIGITAIS) ou ter sido aprovado nas
    disciplina 116394 (ORG ARQ DE COMPUTADORES) e 113042 (Cálculo 2).
    """
    DISCIPLINAS = '<td valign=top><b>Pré-req:</b> </td>' \
                  '<td class=PadraoMenor>(.*?)</td></tr>'
    CODIGO = '(\d{6})'

    pre_req = []
    try:
        pagina_html = busca(url_mweb(nivel, 'disciplina_pop', codigo))
        requisitos = encontra_padrao(DISCIPLINAS, pagina_html.content)
        for requisito in requisitos:
            for disciplinas in requisito.split(' OU<br>'):
                pre_req.append(encontra_padrao(CODIGO, disciplinas))
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return filter(None, pre_req)


def turmas(codigo, nivel='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
    dicionário com a lista de turmas ofertadas para uma disciplina.

    Argumentos:
    codigo -- o código da disciplina.
    nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
             (default graduacao)
    """
    TURMAS = '<b>Turma</b>.*?<font size=4><b>(\w+)</b></font></div>' \
             '.*?' \
             '<td>Ocupadas</td>' \
             '<td><b><font color=(?:red|green)>(\d+)</font></b></td>' \
             '.*?' \
             '<center>(.*?)<br></center>' \
             '.*?' \
             '(Reserva para nivel.*?<td align=left>(.*?)</td>.*?)?' \
             '<td colspan=6 bgcolor=white height=20>'

    oferta = {}
    try:
        pagina_html = busca(url_mweb(nivel, 'oferta_dados', codigo))
        turmas_ofertadas = encontra_padrao(TURMAS, pagina_html.content)
        for turma, ocupadas, professores, aux, reserva in turmas_ofertadas:
            vagas = int(ocupadas)
            if vagas > 0:
                oferta[turma] = {}
                oferta[turma]['matriculados'] = vagas
                oferta[turma]['professores'] = professores.split('<br>')
                if reserva:
                    oferta[turma]['reserva'] = reserva
    except RequestException as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

    return oferta


# deptos = departamentos()
# for d in deptos:
#     print d, deptos[d]

# oferta = disciplinas()
# for d in oferta:
#     print d, oferta[d]

# l_espera = lista_de_espera(113476)
# for turma in l_espera:
#     print turma, l_espera[turma]

# disciplinas_ = pre_requisitos(116424)
# for d in disciplinas_:
#     print d

# turmas_ = turmas(116319)
# for d in turmas_:
    # print d, turmas_[d]
