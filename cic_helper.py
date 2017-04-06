#  -*- coding: utf-8 -*-
#    @package: cic_helper.py
#    @author: Rodrigo Bonifacio (rbonifacio@unb.br)
#


from mwebcrawler import Cursos, Oferta

disciplinas_ofertadas  = Oferta.disciplinas(116) 

for k in disciplinas_ofertadas: 
  print k, ' dados ', disciplinas_ofertadas[k] 


