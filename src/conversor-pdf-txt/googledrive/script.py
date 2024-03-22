#!/usr/bin/env python3

import PyPDF2
import os


def listar_e_criar_minutas(diretorio, novo_sufixo=".pdf.dig.txt"):
    arquivos_processados = []

    for pasta_atual, subpastas, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(".dig.pdf"):
                # Remove o sufixo .dig.pdf para obter a arq
                arq = arquivo[:-len(".dig.pdf")]
                novo_nome_arquivo = arq + novo_sufixo
                caminho_novo_arquivo = os.path.join(pasta_atual, novo_nome_arquivo)
                caminho_original_arquivo = os.path.join(pasta_atual, arquivo)
                
                # Criar o novo arquivo com base no original
                if not os.path.exists(caminho_novo_arquivo):
                    with open(caminho_original_arquivo, 'rb') as arquivo_pdf:
                            leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)

                            # Extrair texto de cada página
                            texto_completo = ''
                            for pagina in leitor_pdf.pages:
                                texto_completo += pagina.extract_text() + '\n'

                            # Salvar o texto extraído em um arquivo de texto
                            with open(caminho_novo_arquivo, 'w', encoding='utf-8') as arquivo_saida:
                                arquivo_saida.write(texto_completo)
                else:
                    # Se o arquivo já existir, simplesmente pula para o próximo
                    continue

    return arquivos_processados

diretorio_base = "/home/dev/resources/googledrive"

if os.path.exists(diretorio_base):
    arquivos_processados = listar_e_criar_minutas(diretorio_base)
    for matricula, caminho_arquivo in arquivos_processados:
        print(f"Matrícula: {matricula}, Arquivo Criado: {caminho_arquivo}")
else:
    print(f"O diretório {diretorio_base} não existe.")