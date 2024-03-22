#!/usr/bin/env python3

import os
import datetime
from docx import Document
from docx.shared import Pt

data_limite = datetime.datetime(2024, 1, 15)  # Data limite para a modificação dos arquivos

def criar_docx_com_formato(conteudo, caminho_saida):
    documento = Document()
    estilo = documento.styles['Normal']
    fonte = estilo.font
    fonte.name = 'Arial'
    fonte.size = Pt(11)

    paragrafo = documento.add_paragraph(conteudo)
    for run in paragrafo.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(11)
    
    documento.save(caminho_saida)

def listar_e_criar_minutas(diretorio, prefixo="mat", sufixo=".abertura.txt", novo_sufixo=".matricula.docx"):
    arquivos_processados = []

    for pasta_atual, subpastas, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.startswith(prefixo) and arquivo.endswith(sufixo):
                matricula = arquivo[len(prefixo):-len(sufixo)]
                novo_nome_arquivo = prefixo + matricula + novo_sufixo
                caminho_novo_arquivo = os.path.join(pasta_atual, novo_nome_arquivo)
                caminho_original_arquivo = os.path.join(pasta_atual, arquivo)
                

                if not os.path.exists(caminho_novo_arquivo):
                    with open(caminho_original_arquivo, 'r', encoding='utf-8') as arquivo_original:
                        conteudo_original = arquivo_original.read()
                    
                    criar_docx_com_formato(conteudo_original, caminho_novo_arquivo)
                    arquivos_processados.append((matricula, caminho_novo_arquivo))
                
                    

                else:

                    continue

    return arquivos_processados

diretorio_base = "/home/dev/resources/googledrive"

if os.path.exists(diretorio_base):
    arquivos_processados = listar_e_criar_minutas(diretorio_base)
    for matricula, caminho_arquivo in arquivos_processados:
        print(f"Matrícula: {matricula}, Arquivo Criado: {caminho_arquivo}")
else:
    print(f"O diretório {diretorio_base} não existe.")