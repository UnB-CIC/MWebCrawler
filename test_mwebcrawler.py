#  -*- coding: utf-8 -*-
##    @package test_mwebcrawler.py
#      @author Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de teste do MWebCrawler. Por vezes o MatriculaWeb "não funciona",
# fazendo com que o(s) teste(s ) falhe(m). Nestes casos, o ideal é  esperar
# um pouco e tentar executar os testes novamente.
#
# Por exemplo, a página de listagem de Departamentos com oferta de disciplinas:
# https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=1
# não carrega completamente (?), faltando informações de oferta dos Campi. Isto
# implica em falha de TestOferta.test_departamentos.


from mwebcrawler import Campus, Cursos, Disciplina, Nivel, Oferta
import unittest


class TestCursos(unittest.TestCase):
    def test_curriculo(self):
        opcao = '6912'  # Mecatrônica
        disciplinas = Cursos.curriculo(opcao, nivel=Nivel.GRADUACAO, verbose=False)

        self.assertIn('obrigatórias', disciplinas)
        self.assertIn('116319', disciplinas['obrigatórias'])

        self.assertIn('cadeias', disciplinas)
        self.assertIn('6', disciplinas['cadeias'])
        for item in disciplinas['cadeias']['6']:
            self.assertTrue(('167011' in item) or ('111830' in item and '111848' in item))

        self.assertIn('optativas', disciplinas)
        self.assertIn('113417', disciplinas['optativas'])

    def test_fluxo(self):
        opcao = '1741'  # Eng. Computação
        fluxo = Cursos.fluxo(opcao, nivel=Nivel.GRADUACAO, verbose=False)

        for p in range(1, 11):
            self.assertIn(p, fluxo)

        self.assertIn('Créditos', fluxo[8])
        self.assertEquals('16', fluxo[8]['Créditos'])

        self.assertIn('Disciplinas', fluxo[8])
        for d in ['168921', '184802', '207438']:
            self.assertIn(d, fluxo[8]['Disciplinas'])

    def test_habilitacoes(self):
        curso = 949  # Eng. Mecatrônica
        habilitacoes = Cursos.habilitacoes(curso, nivel=Nivel.GRADUACAO, campus=Campus.DARCY_RIBEIRO, verbose=False)

        self.assertIn('6912', habilitacoes)
        self.assertIn('Nome', habilitacoes['6912'])
        self.assertEquals('Engenharia de Controle e Automação', habilitacoes['6912']['Nome'])
        self.assertIn('Grau', habilitacoes['6912'])
        self.assertEquals('Engenheiro de Controle e Automação', habilitacoes['6912']['Grau'])
        self.assertIn('Limite mínimo de permanência', habilitacoes['6912'])
        self.assertEquals('8', habilitacoes['6912']['Limite mínimo de permanência'])
        self.assertIn('Limite máximo de permanência', habilitacoes['6912'])
        self.assertEquals('18', habilitacoes['6912']['Limite máximo de permanência'])
        self.assertIn('Créditos para Formatura', habilitacoes['6912'])
        self.assertEquals('274', habilitacoes['6912']['Créditos para Formatura'])
        self.assertIn('Mínimo de Créditos Optativos na Área de Concentração', habilitacoes['6912'])
        self.assertEquals('0', habilitacoes['6912']['Mínimo de Créditos Optativos na Área de Concentração'])
        self.assertIn('Quantidade mínima de Créditos Optativos na Área Conexa', habilitacoes['6912'])
        self.assertEquals('0', habilitacoes['6912']['Quantidade mínima de Créditos Optativos na Área Conexa'])
        self.assertIn('Quantidade máxima de Créditos no Módulo Livre', habilitacoes['6912'])
        self.assertEquals('24', habilitacoes['6912']['Quantidade máxima de Créditos no Módulo Livre'])

    def test_relacao(self):
        cursos = Cursos.relacao(nivel=Nivel.GRADUACAO, campus=Campus.DARCY_RIBEIRO, verbose=False)

        # Códigos selecionados aleatoriamente
        for curso in ['19', '264', '1511', '230', '1414', '281', '451', '167', '1163', '299']:
            self.assertIn(curso, cursos)


class TestDisciplina(unittest.TestCase):
    def test_informacoes(self):
        codigo = 116319  # Estruturas de Dados
        informacoes = Disciplina.informacoes(codigo, nivel=Nivel.GRADUACAO, verbose=False)

        self.assertIn('Sigla do Departamento', informacoes)
        self.assertEquals('CIC', informacoes['Sigla do Departamento'])
        self.assertIn('Nome do Departamento', informacoes)
        self.assertEquals('Departamento de Ciência da Computação',
                          informacoes['Nome do Departamento'])
        self.assertIn('Denominação', informacoes)
        self.assertEquals('ESTRUTURAS DE DADOS', informacoes['Denominação'])
        self.assertIn('Nível', informacoes)
        self.assertEquals('Graduação', informacoes['Nível'])
        self.assertIn('Vigência', informacoes)
        self.assertEquals('1971/2', informacoes['Vigência'])
        self.assertIn('Pré-requisitos', informacoes)
        self.assertIn('116301', informacoes['Pré-requisitos'])
        self.assertIn('Ementa', informacoes)
        self.assertIn('Pilha', informacoes['Ementa'])
        self.assertIn('Programa', informacoes)
        self.assertIn('Gerenciamento dinâmico', informacoes['Programa'])
        self.assertIn('Bibliografia', informacoes)
        self.assertIn('Tenenbaum', informacoes['Bibliografia'])

    def test_pre_requisitos(self):
        codigo = 116424  # Transmissão de Dados

        pre_reqs = Disciplina.pre_requisitos(codigo, nivel=Nivel.GRADUACAO, verbose=False)
        self.assertEquals([['117251'], ['116394', '113042']], pre_reqs)


class TestOferta(unittest.TestCase):
    def test_departamentos(self):
        deptos = Oferta.departamentos(nivel=Nivel.GRADUACAO, campus=Campus.DARCY_RIBEIRO, verbose=False)

        # Códigos escolhidos aleatoriamente
        for depto in ['115', '138', '159', '351', '550']:
            self.assertIn(depto, deptos)

        self.assertIn('Denominação', deptos['351'])
        self.assertEquals('Centro Apoio ao Desenvolvimento Tecnológico', deptos['351']['Denominação'])
        self.assertIn('Sigla', deptos['351'])
        self.assertEquals('CDT', deptos['351']['Sigla'])

        # Campi
        for depto in ['638', '650', '660']:
            self.assertIn(depto, deptos)

    def test_disciplinas(self):
        disciplinas = Oferta.disciplinas(116, nivel=Nivel.GRADUACAO, verbose=False)

        self.assertIn('116394', disciplinas)
        self.assertEquals('ORGANIZACAO E ARQUITETURA DE COMPUTADORES', disciplinas['116394'])

    def test_lista_de_espera(self):
        codigo = 113476  # Algoritmos e Programação de Computadores
        le = Oferta.lista_de_espera(codigo, turma='A', nivel=Nivel.GRADUACAO, verbose=False)

        self.assertIn('A', le)
        self.assertLessEqual(0, le['A'])

        le = Oferta.lista_de_espera(codigo, nivel=Nivel.GRADUACAO, verbose=False)
        self.assertIn('A', le)
        self.assertLessEqual(0, le['A'])

    def test_turmas(self):
        codigo = 116319  # ESTRUTURAS DE DADOS
        turmas = Oferta.turmas(codigo, nivel=Nivel.GRADUACAO, verbose=False)

        for t in ['A', 'B', 'C', 'E']:
            self.assertIn(t, turmas)


if __name__ == '__main__':
    unittest.main()
