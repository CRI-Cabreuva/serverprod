#!/usr/bin/env python3

import sys
sys.path.append('/home/dev/prod/utils/')

import os
import datetime
import utils

data_limite = datetime.datetime(2024, 1, 15)  # Data limite para a modificação dos arquivos

def listar_e_criar_minutas(diretorio, prefixo="mat", sufixo=".minuta.txt", novo_sufixo=".abertura.txt", sufixoLog=".abertura.log.txt"):
    arquivos_processados = []

    for pasta_atual, subpastas, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.startswith(prefixo) and arquivo.endswith(sufixo):
                matricula = arquivo[len(prefixo):-len(sufixo)]
                novo_nome_arquivo = prefixo + matricula + novo_sufixo
                caminho_novo_arquivo = os.path.join(pasta_atual, novo_nome_arquivo)
                caminho_original_arquivo = os.path.join(pasta_atual, arquivo)
                
                # Se o arquivo de minuta não existir, imprime o conteúdo do arquivo original
                if not os.path.exists(caminho_novo_arquivo):
                    print(f"Arquivo de minuta não existe: {caminho_novo_arquivo}, imprimindo o conteúdo do arquivo original...")
                    with open(caminho_original_arquivo, 'r') as arquivo_original:
                        conteudo_original = arquivo_original.read()

                        
                        prompt = utils.get_prompt_drive("/home/dev/prompt/Dev/Prompt abridor de matricula/")
                        nameLog = prefixo + matricula + sufixoLog
                        pathLog = os.path.join(pasta_atual+ "/" + nameLog)
                        resultado = utils.get_gpt4_response(prompt, conteudo_original, pathLog)

                    # Após imprimir, cria o novo arquivo de minuta (ou qualquer outra ação desejada)
                        with open(caminho_novo_arquivo, 'w') as arquivo_novo:
                            arquivo_novo.write(resultado)
                        arquivos_processados.append((matricula, caminho_novo_arquivo))
                else:
                    # Se o arquivo já existir, simplesmente pula para o próximo
                    continue

    return arquivos_processados

diretorio_base = "/home/dev/resources/googledrive/"

if os.path.exists(diretorio_base):
    arquivos_processados = listar_e_criar_minutas(diretorio_base)
    for matricula, caminho_arquivo in arquivos_processados:
        print(f"Matrícula: {matricula}, Arquivo Criado: {caminho_arquivo}")
else:
    print(f"O diretório {diretorio_base} não existe.")



