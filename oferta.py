#  -*- coding: utf-8 -*-
#       @file: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de web-crawling para buscar informações da lista de oferta de cursos
# da UnB. O programa busca as informações com base em expressões regulares que,
# assume-se, representam a estrutura de uma página do Matrícula Web. Caso esta
# estrutura seja alterada, as expressões aqui precisam ser atualizadas de
# acordo.


import requests
import re


# Construção de links para o Matrícula Web.
mweb = lambda curso: 'https://matriculaweb.unb.br/matriculaweb/' + str(curso)
link = lambda pagina, cod: str(pagina) + '.aspx?cod=' + str(cod)
mweb_url = lambda curso, pagina, cod: mweb(curso) + '/' + link(pagina, cod)


def departamento(dept=116, curso='graduacao'):
    """Acessa o Matrícula Web e retorna um dicionário com a lista de
    disciplinas ofertadas por um departamento.

    Argumentos:
    dept -- o código do Departamento que oferece as disciplinas
            (default 116)
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao.
             (default graduacao)

    Lista completa dos Departamentos da UnB:
    matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=1
    """
    DISCIPLINAS = 'oferta_dados.aspx\?cod=(\d+).*?>(.*?)</a>'

    oferta = {}
    try:
        html_page = requests.get(mweb_url(curso, 'oferta_dis', dept))
        disciplinas_ofertadas = re.findall(DISCIPLINAS, html_page.content)
        for codigo, nome in disciplinas_ofertadas:
            oferta[codigo] = nome
    except requests.exceptions.ConnectionError as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, curso, erro)

    return oferta


def disciplina(codigo, curso='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
    dicionário com a lista de turmas ofertadas para uma disciplina.

    Argumentos:
    codigo -- o código da disciplina.
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao.
             (default graduacao)
    """
    TURMAS = '<b>Turma</b>.*?<font size=4><b>(\w+)</b></font></div>' \
            '.*?' \
            '<td>Ocupadas</td>' \
            '<td><b><font color=(?:red|green)>(\d+)</font></b></td>' \
            '.*?' \
            '<center>(.*?)<br></center>' \
            '.*?' \
            '(Reserva para curso.*?<td align=left>(.*?)</td>.*?)?' \
            '<td colspan=6 bgcolor=white height=20>'

    oferta = {}
    try:
        html_page = requests.get(mweb_url(curso, 'oferta_dados', codigo))
        turmas_ofertadas = re.findall(TURMAS, html_page.content)
        for turma, ocupadas, professores, aux, reserva in turmas_ofertadas:
            vagas = int(ocupadas)
            if vagas > 0:
                oferta[turma] = {}
                oferta[turma]['matriculados'] = vagas
                oferta[turma]['professores'] = professores.split('<br>')
                if reserva:
                    oferta[turma]['reserva'] = reserva
    except requests.exceptions.ConnectionError as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, curso, erro)

    return oferta


def pre_requisitos(codigo, curso='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna uma
    lista com os códigos das disciplinas que são pré-requisitos para a dada.

    Argumentos:
    codigo -- o código da disciplina.
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao.
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
        html_page = requests.get(mweb_url(curso, 'disciplina_pop', codigo))
        requisitos = re.findall(DISCIPLINAS, html_page.content)
        for requisito in requisitos:
            for disciplinas in requisito.split(' OU<br>'):
                pre_req.append(re.findall(CODIGO, disciplinas))
    except requests.exceptions.ConnectionError as erro:
        pass
        # print 'Erro ao buscar %s para %s.\n%s' % (codigo, curso, erro)

    return filter(None, pre_req)


def lista_de_espera(codigo, turma='\w+', curso='graduacao'):
    """Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
    dicionário com a lista de espera para as turmas ofertadas da disciplina.

    Argumentos:
    codigo -- o código da disciplina
    turma -- identificador da turma
             (default '\w+') (todas as disciplinas)
    curso -- nível acadêmico das disciplinas buscadas: graduacao ou
             posgraduacao
             (default graduacao).
    """
    TABELA = '<td><b>Turma</b></td>    ' \
             '<td><b>Vagas<br>Solicitadas</b></td>  </tr>' \
             '<tr CLASS=PadraoMenor bgcolor=#E7F3D6>  ' \
             '.*?</tr><tr CLASS=PadraoBranco>'
    TURMAS = '<td align=center >(%s)</td>  ' \
            '<td align=center >(\d+)</td></tr>' % turma

    demanda = {}
    try:
        html_page = requests.get(mweb_url(curso, 'faltavaga_rel', codigo))
        turmas_com_demanda = re.findall(TABELA, html_page.content)
        for tabela in turmas_com_demanda:
            for turma, vagas_desejadas in re.findall(TURMAS, tabela):
                vagas = int(vagas_desejadas)
                if vagas > 0:
                    demanda[turma] = vagas
    except requests.exceptions.ConnectionError as erro:
        pass
        #print 'Erro ao buscar %s para %s.\n%s' % (codigo, curso, erro)

    return demanda

# oferta = departamento()
# for d in oferta:
#     print d, oferta[d]

# oferta = disciplina(116319)
# for d in oferta:
#     print d, oferta[d]

# oferta = pre_requisitos(116424)
# for d in oferta:
#     print d

# oferta = lista_de_espera(113476)
# for d in oferta:
#     print d, oferta[d]
