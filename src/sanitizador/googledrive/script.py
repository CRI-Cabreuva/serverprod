#!/usr/bin/env python3

import os
import datetime
import openai



def triggerOpenai(texto):

    prompt = f""" Vou fornecer-lhe duas partes de um documento obtido por OCR, que corresponde a uma matrícula ou certidão de matrícula de registro de imóveis. Você deverá manter o contexto da primeira parte para que ele se alinhe corretamente com a segunda parte. O processo envolverá a limpeza dos dados para garantir a clareza e a precisão das informações, focando especialmente em:
    DADOS ESSENCIAIS QUE NÃO PODEM FALTA:
        - Descrição perimétrica do terreno,
        - Proprietários,
        - Contribuinte,
        - Registro anterior,
        - Cada ato descrito no documento.

É importante que, ao invés de sumarizar, você apresente o texto completo, corrigindo possíveis erros gramaticais para manter a integridade das informações. A sanitização deve permitir a compreensão clara de:

- Títulos dos atos: Preserve o início dos atos, como "av. 01 - Em 27 de março de 1992.", que geralmente surge após a assinatura do ato anterior. Nunca elimine estes títulos na conversão. 

Diretrizes:
- No início das suas respostas, mencione apenas o número da matrícula e a data de abertura, seguindo o modelo: "Matrícula [número-matrícula] aberta em [dd/mm/aaaa]". Esses dados devem ser extraídos das menções ao CNM no texto original. O CNM tem a estrutura "CNM nº cccccc.d.mmmmmmm-dv", onde "cccccc" é o CNS do cartório, que deve ser ignorado, assim como ".d." e "dv", que são dígitos verificadores. Utilize apenas o número da matrícula, "mmmmmmm", removendo zeros à esquerda.
- Você deve tratar as duas partes do arquivos como uma, então não é necessario repetir as diretrizes, somente continuar.
- Ao fornecer a segunda parte de um documento, continue diretamente da última informação registrada na primeira parte, sem repetir a estrutura inicial do documento. Se a primeira parte terminou na seção 'Atos', com 'Av.02 - Em 07 de novembro de 1988', a segunda parte deve prosseguir com o próximo ato relevante, como 'Av.03 - Em 08 de novembro de 1988', sem reintroduzir as seções de 'Descrição Perimétrica', 'Proprietários', etc. O foco deve estar em adicionar informações sequenciais, mantendo a continuidade e evitando duplicações. 
- Mantenha a formatação do texto (Caixa alta, Caixa baixa, etc...)
- Mantenha o padrão de documento abaixo:
    - Matrícula [número-matrícula] aberta em [dd/mm/aaaa]
    - Descrição perimetrica
        - Não é necessario titulo
    - Proprietarios
    - Registro Anterior
        - Somente registro
        - desconsiderar textos após o número do registro anterior
    - Contribuinte
    - Atos
        - Mantenha o padrão "av. ## - " e "R.## - "
        - Se o título do ato não for identificável, use "XXX - ATO INELEGIVEL".
O objetivo é sanear o documento mantendo todas as informações essenciais intactas. {texto}"""

    try:
        # Notice the use of openai.ChatCompletion here
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Example of a chat-based model
            messages=[
                {"role": "system", "content": "Você é um sanitizador de OCR"},
                {"role": "user", "content": prompt},
            ]
        )
        # Extracting the response
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)

data_limite = datetime.datetime(2024, 1, 15)  # Data limite para a modificação dos arquivos

def listar_e_criar_minutas(diretorio, prefixo="mat", sufixo=".pdf.ocr.txt", novo_sufixo=".minuta.txt"):
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

                        # Calcula o ponto de divisão do conteúdo (dividindo pela metade, por exemplo)
                        ponto_divisao = len(conteudo_original) // 2

                        # Divide o conteúdo em duas partes
                        primeira_parte = conteudo_original[:ponto_divisao]
                        segunda_parte = conteudo_original[ponto_divisao:]

                        # Envia a primeira parte para a função triggerOpenai e guarda o resultado
                        resultado_primeira_parte = triggerOpenai("essa é a primeira parte: " + primeira_parte)

                        # Envia a segunda parte para a função triggerOpenai e guarda o resultado
                        resultado_segunda_parte = triggerOpenai("continuação: " + segunda_parte)

                        # Combina os dois resultados
                        resultado_final = resultado_primeira_parte + resultado_segunda_parte

                    # Após obter o resultado combinado, cria o novo arquivo com o resultado
                    with open(caminho_novo_arquivo, 'w') as arquivo_novo:
                        arquivo_novo.write(resultado_final)

                    # Adiciona a matrícula e o caminho do novo arquivo à lista de arquivos processados
                    arquivos_processados.append((matricula, caminho_novo_arquivo))
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



