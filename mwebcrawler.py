#  -*- coding: utf-8 -*-
#    @package: mwebcrawler.py
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
busca = re.findall
RequestException = requests.exceptions.RequestException


def mweb(nivel, pagina, cod):
    '''Retorna a página no Matrícula Web referente às especificações dadas.'''
    escopo = 'matriculaweb.unb.br/%s' % nivel
    pagina = '%s.aspx?cod=%s' % (pagina, cod)
    html = requests.get('https://%s/%s' % (escopo, pagina))
    return html.content


class Nivel:
    '''Enumeração de níveis de cursos oferecidos.'''
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
    def curriculo(curso, nivel=Nivel.GRADUACAO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        disciplinas definidas no currículo do curso.

        Argumentos:
        curso -- o código do curso.
        nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados

        No caso de disciplinas de cadeias seletivas, o resultado é uma lista em
        que cada item tem uma relação 'OU' com os demais, e cada item é um
        dicionário cujos itens têm uma relação 'E' entre si. Por exemplo:
        o resultado da busca por 6912 (Engenharia Mecatrônica) tem como uma das
        cadeias resultantes (a cadeia '2'), a seguinte lista:
        [{'114014': 'QUIMICA GERAL'}, {'114634': 'QUI GERAL EXPERIMENTAL',
                                       '114626': 'QUIMICA GERAL TEORICA'}]

        que deve ser interpretado como
        114014 OU (114626 E 114634)

        Ou seja, para graduação na habilitação 6912, é preciso ter sido
        aprovado na disciplina QUIMICA GERAL ou ter sido aprovado nas
        disciplinas QUI GERAL EXPERIMENTAL e QUIMICA GERAL TEORICA.
        '''

        OBR_OPT = 'DISCIPLINAS OBRIGATÓRIAS (.*?)</table></td>(.*?)' \
                  'DISCIPLINAS OPTATIVAS (.*?)</table></td>'
        CADEIAS = 'CADEIA: (\d+)(.*?)</table>'
        DISCIPLINA = 'disciplina.aspx\?cod=(\d+)>.*?</b> - (.*?)</a></td>' \
                     '<td><b>(.*?)</b></td><td>(\d+) (\d+) (\d+) (\d+)</td>' \
                     '<td>(.*?)</td></tr>'

        disciplinas = {'obrigatórias': {}, 'cadeias': {}, 'optativas': {}}
        try:
            if verbose:
                log('Buscando currículo do curso ' + str(curso))
            pagina_html = mweb(nivel, 'curriculo', curso)
            obr_e_opts = busca(OBR_OPT, pagina_html)

            for obrigatorias, cadeias, optativas in obr_e_opts:
                disciplinas['obrigatórias'] = {}
                for (cod, nome, e_ou, teor,
                     prat, ext, est, area) in busca(DISCIPLINA, obrigatorias):
                    creditos = {'Teoria': int(teor), 'Prática': int(prat),
                                'Extensão': int(ext), 'Estudo': int(est)}
                    disciplinas['obrigatórias'][cod] = {'Nome': nome.strip(),
                                                        'Créditos': creditos,
                                                        'Área': area.strip()}

                for ciclo, discs in busca(CADEIAS, cadeias):
                    disciplinas['cadeias'][ciclo] = []
                    current = {}
                    for (cod, nome, e_ou, teor,
                         prat, ext, est, area) in busca(DISCIPLINA, discs):
                        creditos = {'Teoria': int(teor), 'Prática': int(prat),
                                    'Extensão': int(ext), 'Estudo': int(est)}
                        current[cod] = {'Nome': nome.strip(),
                                        'Créditos': creditos,
                                        'Área': area.strip()}
                        if e_ou.strip() != 'E':
                            disciplinas['cadeias'][ciclo].append(current)
                            current = {}

                for (cod, nome, e_ou, teor,
                     prat, ext, est, area) in busca(DISCIPLINA, optativas):
                    creditos = {'Teoria': int(teor), 'Prática': int(prat),
                                'Extensão': int(ext), 'Estudo': int(est)}
                    disciplinas['optativas'][cod] = {'Nome': nome.strip(),
                                                     'Créditos': creditos,
                                                     'Área': area.strip()}
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (curso, nivel, erro)

        return disciplinas

    @staticmethod
    def fluxo(habilitacao, nivel=Nivel.GRADUACAO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        disciplinas por período definidas no fluxo da habilitação.

        Argumentos:
        habilitacao -- o código da habilitação do curso.
        nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        PERIODO = '<b>PERÍODO: (\d+).*?CRÉDITOS:</b> (\d+)</td>' \
                  '(.*?)</tr></table>'
        DISCIPLINA = 'disciplina.aspx\?cod=\d+>(\d+)</a>'

        disciplinas = {}
        try:
            if verbose:
                log('Buscando disciplinas no fluxo da habilitação ' +
                    str(habilitacao))
            pagina_html = mweb(nivel, 'fluxo', habilitacao)
            oferta = busca(PERIODO, pagina_html)
            for periodo, creditos, dados in oferta:
                periodo = int(periodo)
                disciplinas[periodo] = {}
                disciplinas[periodo]['Créditos'] = creditos
                disciplinas[periodo]['Disciplinas'] = busca(DISCIPLINA, dados)
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' %
            #       (habilitacao, nivel, erro)

        return disciplinas

    @staticmethod
    def habilitacoes(curso, nivel=Nivel.GRADUACAO,
                     campus=Campus.DARCY_RIBEIRO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        informações referentes a cada habilitação no curso.

        Argumentos:
        curso -- o código do curso.
        nivel -- nível acadêmico do curso: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        OPCAO = '<a name=\d+></a><tr .*?><td  colspan=3><b>(\d+) - (.*?)' \
                '</b></td></tr>.*?' \
                'Grau: </td><td .*?>(.*?)</td></tr>.*?' \
                'Limite mínimo de permanência: </td>' \
                '<td align=right>(\d+)</td>.*?' \
                'Limite máximo de permanência: </td>.*?' \
                '<td align=right>(\d+)</td>.*?' \
                'Quantidade de Créditos para Formatura: </td>' \
                '<td align=right>(\d+)</td>.*?' \
                'Quantidade mínima de Créditos Optativos ' \
                'na Área de Concentração: </td>' \
                '<td align=right>(\d+)</td>.*?' \
                'Quantidade mínima de Créditos Optativos na Área Conexa: ' \
                '</td><td align=right>(\d+)</td>.*?' \
                'Quantidade máxima de Créditos no Módulo Livre: </td>' \
                '<td align=right>(\d+)</td>'

        dados = {}
        try:
            if verbose:
                log('Buscando informações da habilitação do curso ' +
                    str(curso))
            pagina_html = mweb(nivel, 'curso_dados', curso)
            habilitacoes = busca(OPCAO, pagina_html)
            for (habilitacao, nome, grau, l_min, l_max,
                 formatura, obr, opt, livre) in habilitacoes:
                dados[habilitacao] = {}
                dados[habilitacao]['Nome'] = nome
                dados[habilitacao]['Grau'] = grau
                dados[habilitacao]['Limite mínimo de permanência'] = l_min
                dados[habilitacao]['Limite máximo de permanência'] = l_max
                dados[habilitacao]['Créditos para Formatura'] = formatura
                dados[habilitacao]['Mínimo de Créditos Optativos na '
                                   'Área de Concentração'] = obr
                dados[habilitacao]['Quantidade mínima de Créditos Optativos '
                                   'na Área Conexa'] = opt
                dados[habilitacao]['Quantidade máxima de Créditos no '
                                   'Módulo Livre'] = livre
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' % (curso, nivel, erro)

        return dados

    @staticmethod
    def relacao(nivel=Nivel.GRADUACAO, campus=Campus.DARCY_RIBEIRO,
                verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a relação de
        cursos existentes.

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
                 '<td>(.*?)</td>' \
                 '<td>\d+</td>' \
                 '.*?aspx\?cod=(\d+)>(.*?)</a></td>' \
                 '<td>(.*?)</td></tr>'

        lista = {}
        try:
            if verbose:
                log('Buscando lista de cursos')
            pagina_html = mweb(nivel, 'curso_rel', campus)
            cursos_existentes = busca(CURSOS, pagina_html)
            for modalidade, codigo, denominacao, turno in cursos_existentes:
                lista[codigo] = {}
                lista[codigo]['Modalidade'] = modalidade
                lista[codigo]['Denominação'] = denominacao
                lista[codigo]['Turno'] = turno
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar relação de cursos para %s em %d.\n%s' %
            #     (nivel, campus, erro)

        return lista


class Disciplina:
    '''Métodos de busca associados a informações de disciplinas.'''

    @staticmethod
    def informacoes(disciplina, nivel=Nivel.GRADUACAO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com as informações da
        disciplina.

        Argumentos:
        disciplina -- o código da disciplina.
        nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        DISCIPLINAS = 'Órgão:</b> </td><td>(\w+) - (.*?)</td></tr>.*?' \
                      'Denominação:</b> </td><td>(.*?)</td></tr>.*?' \
                      'Nível:</b> </td><td>(.*?)</td></tr>.*?' \
                      'Vigência:</b> </td><td>(.*?)</td></tr>.*?' \
                      'Pré-req:</b> </td><td class=PadraoMenor>(.*?)' \
                      '</td></tr>.*?' \
                      'Ementa:</b> </td><td class=PadraoMenor>' \
                      '<p align=justify>(.*?)</P></td></tr>.*?' \
                      '(?:.*Programa:</b> </td><td class=PadraoMenor>' \
                      '<p align=justify>(.*?)</P></td></tr>)?.*?' \
                      'Bibliografia:</b> </td><td class=PadraoMenor>' \
                      '<p align=justify>(.*?)</P></td></tr>'

        infos = {}
        try:
            if verbose:
                log('Buscando informações da disciplina ' + str(disciplina))
            pagina_html = mweb(nivel, 'disciplina', disciplina)
            informacoes = busca(DISCIPLINAS, pagina_html)
            for (sigla, nome, denominacao, nivel, vigencia,
                 pre_req, ementa, programa, bibliografia) in informacoes:
                infos['Sigla do Departamento'] = sigla
                infos['Nome do Departamento'] = nome
                infos['Denominação'] = denominacao
                infos['Nível'] = nivel  # sobrescreve o argumento da função
                infos['Vigência'] = vigencia
                infos['Pré-requisitos'] = pre_req.replace('<br>', ' ')
                infos['Ementa'] = ementa.replace('<br />', '\n')
                if programa:
                    infos['Programa'] = programa.replace('<br />', '\n')
                infos['Bibliografia'] = bibliografia.replace('<br />', '\n')
        except RequestException:  # as erro
            pass
            # print 'Erro ao buscar %s para %s.\n%s' %
            #       (disciplina, nivel, erro)

        return infos

    @staticmethod
    def pre_requisitos(disciplina, nivel=Nivel.GRADUACAO, verbose=False):
        '''Dado o código de uma disciplina, acessa o Matrícula Web e retorna
        uma lista com os códigos das disciplinas que são pré-requisitos para a
        dada.

        Argumentos:
        disciplina -- o código da disciplina.
        nivel -- nível acadêmico da disciplina: graduacao ou posgraduacao.
                 (default graduacao)
        verbose -- indicação dos procedimentos sendo adotados

        Cada item da lista tem uma relação 'OU' com os demais, e cada item é
        uma outra lista cujos itens têm uma relação 'E' entre si. Por exemplo:
        o resultado da busca por 116424 (Transmissão de Dados) é:
        [['117251'], ['116394', '113042']]
        que deve ser interpretado como
        ['117251'] OU ['116394' E '113042']

        Ou seja, para cursar a disciplina 116424, é preciso ter sido aprovado
        na disciplina 117251 (ARQ DE PROCESSADORES DIGITAIS) ou ter sido
        aprovado nas disciplinas 116394 (ORG ARQ DE COMPUTADORES) e 113042
        (Cálculo 2).
        '''
        DISCIPLINAS = '<td valign=top><b>Pré-req:</b> </td>' \
                      '<td class=PadraoMenor>(.*?)</td></tr>'
        CODIGO = '(\d{6})'

        pre_req = []
        try:
            if verbose:
                log('Buscando a lista de pré-requisitos para a disciplina ' +
                    str(disciplina))
            pagina_html = mweb(nivel, 'disciplina_pop', disciplina)
            requisitos = busca(DISCIPLINAS, pagina_html)
            for requisito in requisitos:
                for disciplinas in requisito.split(' OU<br>'):
                    pre_req.append(busca(CODIGO, disciplinas))
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' %
            #       (disciplina, nivel, erro)

        return [cod_disc for cod_disc in pre_req if cod_disc]


class Oferta:
    '''Métodos de busca associados a informações da oferta de disciplinas.'''
    @staticmethod
    def departamentos(nivel=Nivel.GRADUACAO,
                      campus=Campus.DARCY_RIBEIRO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        departamentos com ofertas do semestre atual.

        Argumentos:
        nivel -- nível acadêmico do Departamento: graduacao ou posgraduacao.
                 (default graduacao)
        campus -- o campus onde o curso é oferecido: DARCY_RIBEIRO, PLANALTINA,
                  CEILANDIA ou GAMA
                  (default DARCY_RIBEIRO)
        verbose -- indicação dos procedimentos sendo adotados
        '''
        DEPARTAMENTOS = '<tr CLASS=PadraoMenor bgcolor=.*?>'\
                        '<td>\d+</td><td>(\w+)</td>' \
                        '.*?aspx\?cod=(\d+)>(.*?)</a></td></tr>'

        deptos = {}
        try:
            if verbose:
                log('Buscando a informações de departamentos com oferta')
            pagina_html = mweb(nivel, 'oferta_dep', campus)
            deptos_existentes = busca(DEPARTAMENTOS, pagina_html)
            for sigla, codigo, denominacao in deptos_existentes:
                deptos[codigo] = {}
                deptos[codigo]['Sigla'] = sigla
                deptos[codigo]['Denominação'] = denominacao
        except RequestException:
            pass
            # print 'Erro ao buscar %s em %d.\n%s' % (nivel, campus, erro)

        return deptos

    @staticmethod
    def disciplinas(departamento, nivel=Nivel.GRADUACAO, verbose=False):
        '''Acessa o Matrícula Web e retorna um dicionário com a lista de
        disciplinas ofertadas por um departamento.

        Argumentos:
        departamento -- o código do Departamento que oferece as disciplinas
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
                    str(departamento))
            pagina_html = mweb(nivel, 'oferta_dis', departamento)
            ofertadas = busca(DISCIPLINAS, pagina_html)
            for codigo, nome in ofertadas:
                oferta[codigo] = nome
        except RequestException:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' %
            #       (departamento, nivel, erro)

        return oferta

    @staticmethod
    def lista_de_espera(disciplina, turma='\w+', nivel=Nivel.GRADUACAO,
                        verbose=False):
        '''Dado o código de uma disciplina, acessa o Matrícula Web e retorna um
        dicionário com a lista de espera para turmas ofertadas da disciplina.

        Argumentos:
        disciplina -- o código da disciplina
        turma -- identificador da turma
                 (default '\w+') (todas as disciplinas)
        nivel -- nível acadêmico da disciplina buscada: graduacao ou
                 posgraduacao.
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
                log('Buscando turmas com lista de espera para a disciplina ' +
                    str(disciplina))
            pagina_html = mweb(nivel, 'faltavaga_rel', disciplina)
            turmas_com_demanda = busca(TABELA, pagina_html)
            for tabela in turmas_com_demanda:
                for turma, vagas_desejadas in busca(TURMAS, tabela):
                    vagas = int(vagas_desejadas)
                    if vagas > 0:
                        demanda[turma] = vagas
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s' %
            #       (disciplina, nivel, erro)

        return demanda

    @staticmethod
    def turmas(disciplina, depto=116, nivel=Nivel.GRADUACAO, verbose=False):
        '''Dado o código de uma disciplina, e o do Departamento que a oferece,
        acessa o Matrícula Web e retorna um dicionário com a lista de turmas
        ofertadas para uma disciplina.

        Argumentos:
        disciplina -- o código da disciplina.
        depto -- o código do departamento que oferece a disciplina.
                 (default 116) 116: CIC, 650:Gama
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
                log('Buscando as turmas da disciplina ' + str(disciplina))
            filtro = str(disciplina)
            if depto:
                filtro += '&dep=' + str(depto)
            pagina_html = mweb(nivel, 'oferta_dados', filtro)
            turmas_ofertadas = busca(TURMAS, pagina_html)
            for turma, ocupadas, professores, aux, reserva in turmas_ofertadas:
                oferta[turma] = {}
                oferta[turma]['Alunos Matriculados'] = int(ocupadas)
                oferta[turma]['Professores'] = professores.split('<br>')
                if reserva:
                    oferta[turma]['Turma Reservada'] = reserva
        except RequestException:  # as erro:
            pass
            # print 'Erro ao buscar %s para %s.\n%s'
            #       % (disciplina, nivel, erro)

        return oferta


def log(msg):
    '''Log de mensagens.'''
    print(msg)
