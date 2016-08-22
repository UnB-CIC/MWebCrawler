#  -*- coding: utf-8 -*-
#       @file: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de web-crawling para buscar informações de cursos da UnB. O programa
# busca as informações com base em expressões regulares que, assume-se,
# representam a estrutura de uma página do Matrícula Web. Caso esta estrutura
# seja alterada, as expressões aqui precisam ser atualizadas de acordo.
#
# Erros em requests são ignorados silenciosamente.


import requests
import re

# Renomeando funções/classes para maior clareza de código.
busca = requests.get
encontra_padrao = re.findall
RequestException = requests.exceptions.RequestException


GRADUACAO = 'graduacao'
POS = 'posgraduacao'


class Campus:
    '''Enumeração dos códigos de cada campus.'''
    DARCY_RIBEIRO = 1
    PLANALTINA = 2
    CEILANDIA = 3
    GAMA = 4


class Cursos:
    '''Métodos de busca associados a informações de cursos.'''
    @staticmethod
    def curriculo(codigo, nivel=GRADUACAO, verbose=False):
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
            obr_e_opts = encontra_padrao(OBR_OPT, pagina_html.content)
            for obrigatorias, optativas in obr_e_opts:
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

    @staticmethod
    def fluxo(codigo, nivel=GRADUACAO, verbose=False):
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

    @staticmethod
    def habilitacoes(codigo, nivel=GRADUACAO, campus=Campus.DARCY_RIBEIRO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        informações referentes a cada habilitação no curso.

        Argumentos:
        codigo -- o código do curso.
        nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        OPCAO = '<a name=\d+></a><tr .*?><td  colspan=3><b>(\d+) - (.*?)</b></td></tr>'\
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

        dados = {}
        try:
            if verbose:
                log('Buscando informações da habilitação do curso ' + str(codigo))
            pagina_html = busca(url_mweb(nivel, 'curso_dados', codigo))
            oferta = encontra_padrao(OPCAO, pagina_html.content)
            for opcao, nome, grau, min, max, formatura, obr, opt, livre in oferta:
                dados[opcao] = {}
                dados[opcao]['Nome'] = nome
                dados[opcao]['Grau'] = grau
                dados[opcao]['Limite mínimo de permanência'] = min
                dados[opcao]['Limite máximo de permanência'] = max
                dados[opcao]['Créditos para Formatura'] = formatura
                dados[opcao]['Mínimo de Créditos Optativos na '
                             'Área de Concentração'] = obr
                dados[opcao]['Quantidade mínima de Créditos Optativos na '
                             'Área Conexa'] = opt
                dados[opcao]['Quantidade máxima de Créditos no '
                             'Módulo Livre'] = livre
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return dados


    @staticmethod
    def relacao(nivel=GRADUACAO, campus=Campus.DARCY_RIBEIRO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de cursos.

        Argumentos:
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
                 '.*?aspx\?cod=(\d+)>(.*?)</a></td>' \
                 '<td>(.*?)</td></tr>'

        lista = {}
        print 'nivel ', nivel
        try:
            if verbose:
                log('Buscando lista de cursos')
            pagina_html = busca(url_mweb(nivel, 'curso_rel', campus))
            print pagina_html.content
            cursos_existentes = encontra_padrao(CURSOS, pagina_html.content)
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

class Disciplina:
    '''Métodos de busca associados a informações de disciplinas.'''

    @staticmethod
    def informacoes(codigo, nivel=GRADUACAO, verbose=False):
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
                      '<p align=justify>(.*?)</P></td></tr>.*?' \
                      '(?:.*Programa:</b> </td><td class=PadraoMenor>' \
                      '<p align=justify>(.*?)</P></td></tr>)?' \
                      '.*?' \
                      'Bibliografia:</b> </td><td class=PadraoMenor>' \
                      '<p align=justify>(.*?)</P></td></tr>'
                      # 'Programa'  pode não estar definido

        disc = {}
        try:
            if verbose:
                log('Buscando informações da disciplina ' + str(codigo))
            pagina_html = busca(url_mweb(nivel, 'disciplina', codigo))
            informacoes = encontra_padrao(DISCIPLINAS, pagina_html.content)
            for sigla, nome, denominacao, nivel, vigencia, pre_req, ementa, programa, bibliografia in informacoes:
                disc['Sigla do Departamento'] = sigla
                disc['Nome do Departamento'] = nome
                disc['Denominação'] = denominacao
                disc['Nivel'] = nivel
                disc['Vigência'] = vigencia
                disc['Pré-requisitos'] = pre_req.replace('<br>', ' ')
                disc['Ementa'] = ementa.replace('<br />', '\n')
                if programa:
                    disc['Programa'] = programa.replace('<br />', '\n')
                disc['Bibliografia'] = bibliografia.replace('<br />', '\n')
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return disc

    @staticmethod
    def pre_requisitos(codigo, nivel=GRADUACAO, verbose=False):
        '''Dado o código de uma disciplina, acessa o Matrícula Web e retorna uma
        lista com os códigos das disciplinas que são pré-requisitos para a dada.

        Argumentos:
        codigo -- o código da disciplina.
        nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados

        Cada item da lista tem uma relação 'OU' com os demais, e cada item é uma
        outra lista cujos itens têm uma relação 'E' entre si. Por exemplo: o
        resultado da busca por 116424 (Transmissão de Dados) é:
        [['117251'], ['116394', '113042']]
        que deve ser lido como
        ['117251'] OU ['116394' E '113042']

        Ou seja, para cursar a disciplina 116424, é preciso ter sido aprovado na
        disciplina 117251(ARQ DE PROCESSADORES DIGITAIS) ou ter sido aprovado nas
        disciplina 116394 (ORG ARQ DE COMPUTADORES) e 113042 (Cálculo 2).
        '''
        DISCIPLINAS = '<td valign=top><b>Pré-req:</b> </td>' \
                      '<td class=PadraoMenor>(.*?)</td></tr>'
        CODIGO = '(\d{6})'

        pre_req = []
        try:
            if verbose:
                log('Buscando a lista de pré-requisitos para a disciplina ' +
                    str(codigo))
            pagina_html = busca(url_mweb(nivel, 'disciplina_pop', codigo))
            requisitos = encontra_padrao(DISCIPLINAS, pagina_html.content)
            for requisito in requisitos:
                for disciplinas in requisito.split(' OU<br>'):
                    pre_req.append(encontra_padrao(CODIGO, disciplinas))
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return filter(None, pre_req)

class Oferta:
    '''Métodos de busca associados a informações da oferta de disciplinas.'''
    @staticmethod
    def departamentos(nivel=GRADUACAO, campus=Campus.DARCY_RIBEIRO,
                      verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        departamentos com ofertas do semestre atual.

        Argumentos:
        nivel -- nível acadêmico do Departamento: graduacao ou posgraduacao.
                 (default graduacao)
        campus -- o campus onde o curso é oferecido: DARCY_RIBEIRO, PLANALTINA,
                  CEILANDIA ou GAMA
                  (default DARCY_RIBEIRO)
        verbose -- indicação dos procedimentos sendo adotados


        O argumento 'codigo' deve ser uma expressão regular.
        '''
        DEPARTAMENTOS = '<tr CLASS=PadraoMenor bgcolor=.*?>'\
                        '<td>\d+</td><td>(\w+)</td>' \
                        '.*?aspx\?cod=(\d+)>(.*?)</a></td></tr>'

        deptos = {}
        try:
            if verbose:
                log('Buscando a informações de departamentos com oferta')
            pagina_html = busca(url_mweb(nivel, 'oferta_dep', campus))
            deptos_existentes = encontra_padrao(DEPARTAMENTOS, pagina_html.content)
            for sigla, codigo, denominacao in deptos_existentes:
                deptos[codigo] = {}
                deptos[codigo]['Sigla'] = sigla
                deptos[codigo]['Denominação'] = denominacao
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s em %d.\n%s' %
            #     (codigo, nivel, campus, erro)

        return deptos

    @staticmethod
    def disciplinas(dept, nivel=GRADUACAO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        disciplinas ofertadas por um departamento.

        Argumentos:
        dept -- o código do Departamento que oferece as disciplinas
        nivel -- nível acadêmico das disciplinas buscadas: graduacao ou
                 posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados

        Lista completa dos Departamentos da UnB:
        matriculaweb.unb.br/matriculaweb/graduacao/oferta_dep.aspx?cod=1
        '''
        DISCIPLINAS = 'oferta_dados.aspx\?cod=(\d+).*?>(.*?)</a>'

        oferta = {}
        try:
            if verbose:
                log('Buscando a informações de disciplinas do departamento ' +
                    str(dept))
            pagina_html = busca(url_mweb(nivel, 'oferta_dis', dept))
            ofertadas = encontra_padrao(DISCIPLINAS, pagina_html.content)
            for codigo, nome in ofertadas:
                oferta[codigo] = nome
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return oferta

    @staticmethod
    def lista_de_espera(codigo, turma='\w+', nivel=GRADUACAO, verbose=False):
        '''Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
        dicionário com a lista de espera para as turmas ofertadas da disciplina.

        Argumentos:
        codigo -- o código da disciplina
        turma -- identificador da turma
                 (default '\w+') (todas as disciplinas)
        nivel -- nível acadêmico da disciplina buscada: graduacao ou posgraduacao.
                 (default graduacao).
        verbose -- indicação dos procedimentos sendo adotados

        O argumento 'turma' deve ser uma expressão regular.
        '''
        TABELA = '<td><b>Turma</b></td>    ' \
                 '<td><b>Vagas<br>Solicitadas</b></td>  </tr>' \
                 '<tr CLASS=PadraoMenor bgcolor=.*?>  ' \
                 '.*?</tr><tr CLASS=PadraoBranco>'
        TURMAS = '<td align=center >(%s)</td>  ' \
                 '<td align=center >(\d+)</td></tr>' % turma

        demanda = {}
        try:
            if verbose:
                log('Buscando as turmas com lista de espera para a disciplina ' +
                    str(codigo))
            pagina_html = busca(url_mweb(nivel, 'faltavaga_rel', codigo))
            turmas_com_demanda = encontra_padrao(TABELA, pagina_html.content)
            for tabela in turmas_com_demanda:
                for turma, vagas_desejadas in encontra_padrao(TURMAS, tabela):
                    vagas = int(vagas_desejadas)
                    if vagas > 0:
                        demanda[turma] = vagas
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return demanda

    @staticmethod
    def turmas(codigo, nivel=GRADUACAO, verbose=False):
        '''Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
        dicionário com a lista de turmas ofertadas para uma disciplina.

        Argumentos:
        codigo -- o código da disciplina.
        nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        TURMAS = '<b>Turma</b>.*?<font size=4><b>(\w+)</b></font></div>' \
                 '.*?' \
                 '<td>Ocupadas</td>' \
                 '<td><b><font color=(?:red|green)>(\d+)</font></b></td>' \
                 '.*?' \
                 '<center>(.*?)(?:|<br>)</center>' \
                 '.*?' \
                 '(Reserva para curso.*?<td align=left>(.*?)</td>.*?)?' \
                 '<td colspan=6 bgcolor=white height=20>'

        oferta = {}
        try:
            if verbose:
                log('Buscando as turmas da disciplina ' + str(codigo))
            pagina_html = busca(url_mweb(nivel, 'oferta_dados', codigo))
            turmas_ofertadas = encontra_padrao(TURMAS, pagina_html.content)
            for turma, ocupadas, professores, aux, reserva in turmas_ofertadas:
                oferta[turma] = {}
                oferta[turma]['Alunos Matriculados'] = int(ocupadas)
                oferta[turma]['Professores'] = professores.split('<br>')
                if reserva:
                    oferta[turma]['Turma Reservada'] = reserva
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (codigo, nivel, erro)

        return oferta


def url_mweb(nivel, pagina, cod):
    '''Retorna a url para acessar uma página no Matrícula Web.'''
    url_base = 'matriculaweb.unb.br/' + str(nivel)
    link = str(pagina) + '.aspx?cod=' + str(cod)
    return 'https://%s/%s' % (url_base, link)


def log(msg):
    '''Log de mensagens.'''
    print msg


if __name__ == '__main__':
    # curriculo = Cursos.curriculo(1856)
    # for disciplina in sorted(curriculo):
    #     print disciplina, curriculo[disciplina]

    # periodos = Cursos.fluxo(6912)  # 1856)
    # for p in sorted(periodos):
    #     print "Período ", p, periodos[p]

    # habilitacoes = Cursos.habilitacoes(370)
    # for k, v in habilitacoes.items():
    #     print k, v

    # cursos = Cursos.relacao()
    # for k, v in cursos.items():
    #     print k, v

    # informacoes = Disciplina.informacoes(113476)
    # informacoes = Disciplina.informacoes(114626)
    # for k, v in informacoes.items():
    #     print k, v,'\n'

    # pre_requisitos = Disciplina.pre_requisitos(113476)
    # pre_requisitos = Disciplina.pre_requisitos(116319)
    # print pre_requisitos

    # departamentos = Oferta.departamentos()
    # for k, v in departamentos.items():
    #     print k, v

    # disciplinas = Oferta.disciplinas(116)
    # for k, v in disciplinas.items():
    #     print k, v

    # l_espera = Oferta.lista_de_espera(113476)
    # for turma in l_espera:
    #     print turma, l_espera[turma]

    # turmas = Oferta.turmas(113476)
    # for k, v in turmas.items():
    #     print k, v

    pass