#  -*- coding: utf-8 -*-
#       @file: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Utilidades.

import requests
import re

# Renomeando funções/classes para maior clareza de código.
busca = requests.get
encontra_padrao = re.findall
RequestException = requests.exceptions.RequestException


class UnBEnum:
    '''Enumerações.'''
    class Campus:
        '''Enumeração dos códigos de cada campus.'''
        DARCY_RIBEIRO = 1
        PLANALTINA = 2
        CEILANDIA = 3
        GAMA = 4

    class Curso:
        '''Enumeração dos códigos de cursos.'''
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
        '''Enumeração de habilitação de cursos.'''
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
            '''Retorna a lista de todos os cursos com disciplinas obrigatórias
            do CIC em seus currículos.
            '''
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


def url_mweb(nivel, pagina, cod):
    '''Retorna a url para acessar uma página no Matrícula Web.'''
    url_base = 'matriculaweb.unb.br/' + str(nivel)
    link = str(pagina) + '.aspx?cod=' + str(cod)
    return 'https://%s/%s' % (url_base, link)


def log(msg):
    '''Log de mensagens.'''
    print msg
