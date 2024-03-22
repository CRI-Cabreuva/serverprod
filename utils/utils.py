#!/usr/bin/env python3

import openai
import os
import glob
import boto3
import json
import textract
import docx2txt

from docx import Document
from datetime import datetime


# KEY PARA CHAMADAS OPENAI
openai.api_key = os.getenv('api_key_openai')


#                           get_gpt4_response
# -------------------------------------------------------------------------
# Função para fazer chamada na API da openai com GPT-4
# Também irá chamar outra função "create_log_gpt4" para criar arquivo de log
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import openai - para usar api da OPENAI
# from datetime import datetime - para variaveis de horario e data

def get_gpt4_response(promptUser, attachmentUser, pathFile):

    prompt = f"{promptUser} {attachmentUser}"

    initNow = datetime.now()
    initData = initNow.strftime("%d/%m/%Y")
    initHour = initNow.strftime("%H:%M:%S")

    try:
        # Notice the use of openai.ChatCompletion here
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Example of a chat-based model
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ]
        )

        create_log_gpt4(response, initData, initHour, pathFile)
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)



#                           get_claude_2_1_response
# -------------------------------------------------------------------------
# Função para fazer chamada na API da AWS bedrock no modelo ANTHROPIC CLAUDE 2.1
# 
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import boto3 - Fazer chamada na bedrock
# import json - Importar a response da request em JSON
    
def get_claude_2_1_response(promptUser, attachmentUser,  pathFile):

    initNow = datetime.now()
    initData = initNow.strftime("%d/%m/%Y")
    initHour = initNow.strftime("%H:%M:%S")

    # Inicialize o cliente do Bedrock Runtime
    brt = boto3.client(service_name='bedrock-runtime')

    # Prepare o corpo da solicitação
    body = json.dumps({
        "prompt": f"\n\nHuman: {promptUser} {attachmentUser}\n\nAssistant:",
        "max_tokens_to_sample": 2000,
        "temperature": 0.0,
        "top_p": 0.9,
    })

    # Substitua 'modelId' pelo ID do modelo Claude 2.1
    modelId = 'anthropic.claude-v2:1'
    accept = 'application/json'
    contentType = 'application/json'

    # Faça a chamada de inferência
    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    # response_body = json.loads(response['body'].read().decode('utf-8'))
    response_body = json.loads(response['body'].read().decode('utf-8'))
    # Agora, response_body deve ser um dicionário Python contendo os dados que você espera

    input_token_count = response['ResponseMetadata'].get('HTTPHeaders', {}).get('x-amzn-bedrock-input-token-count')
    output_token_count = response['ResponseMetadata'].get('HTTPHeaders', {}).get('x-amzn-bedrock-output-token-count')

    create_log_claude_2_1(initData, initHour, input_token_count, output_token_count, pathFile)


    return response_body.get('completion')

#                      get_claude_3_sonnet_response
# -------------------------------------------------------------------------
# Função para fazer chamada na API da AWS bedrock no modelo ANTHROPIC CLAUDE 3
# Modelo: Sonnet
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import boto3 - Fazer chamada na bedrock
# import json - Importar a response da request em JSON

def get_claude_3_sonnet_response(promptUser, attachmentUser,  pathFile):

    initNow = datetime.now()
    initData = initNow.strftime("%d/%m/%Y")
    initHour = initNow.strftime("%H:%M:%S")

    # Inicialize o cliente do Bedrock Runtime
    brt = boto3.client(service_name='bedrock-runtime')

    # Prepare o corpo da solicitação
    body = json.dumps({
        "prompt": f"\n\nHuman: {promptUser} {attachmentUser}\n\nAssistant:",
        "max_tokens_to_sample": 2000,
        "temperature": 0.0,
        "top_p": 0.9,
    })

    # Substitua 'modelId' pelo ID do modelo Claude 2.1
    modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
    accept = 'application/json'
    contentType = 'application/json'

    # Faça a chamada de inferência
    response = brt.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    # response_body = json.loads(response['body'].read().decode('utf-8'))
    response_body = json.loads(response['body'].read().decode('utf-8'))
    # Agora, response_body deve ser um dicionário Python contendo os dados que você espera

    input_token_count = response['ResponseMetadata'].get('HTTPHeaders', {}).get('x-amzn-bedrock-input-token-count')
    output_token_count = response['ResponseMetadata'].get('HTTPHeaders', {}).get('x-amzn-bedrock-output-token-count')

    create_log_claude_2_1(initData, initHour, input_token_count, output_token_count, pathFile)


    return response_body.get('completion')





#                           create_log_claude_2_1
# -------------------------------------------------------------------------
# Função para criar arquivo de log com dados de consumo da API do ANTHROPIC CLAUDE 2.1
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import os
# from datetime import datetime - para variaveis de horario e data

def create_log_claude_2_1(initData, initHour, input_token_count, output_token_count, pathFile):

        finishNow = datetime.now()
        finishData = finishNow.strftime("%d/%m/%Y")
        finishHour = finishNow.strftime("%H:%M:%S")

        format = "%H:%M:%S"
        initHour_dt = datetime.strptime(initHour, format)
        finishHour_dt = datetime.strptime(finishHour, format)
        diferrenceHour = round((finishHour_dt - initHour_dt).total_seconds() / 60, 2)  

        tokenCalculatorInput = (int(input_token_count) / 1000) * 0.008
        tokenCalculatorOutput = (int(output_token_count) / 1000) * 0.0024

        totalPrincingToken = round((tokenCalculatorInput + tokenCalculatorOutput) * 4.93, 2)
        

        dataTXT = f"\nLOG {pathFile}\n\ndata de inicio: {initData}\nhora de inicio: {initHour}\nErros: 0\ndata de conclusão: {finishData}\nhora de conclusão: {finishHour}\ntempo para conclusão: {diferrenceHour} minutos\nquantidade de tokens de entrada: {input_token_count}\nquantidade de tokens de saída: {output_token_count}\ncusto de IA estimado em tokens: R$ {totalPrincingToken} (Dolar atual R$ 4,93)\n"
        print(f"{dataTXT}")

        with open(pathFile, 'w') as arquivo_novo:
            arquivo_novo.write(dataTXT)



#                           create_log_gpt4
# -------------------------------------------------------------------------
# Função para criar arquivo de log com dados de consumo da API do GPT-4 
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import os
# from datetime import datetime - para variaveis de horario e data

def create_log_gpt4(response, initData, initHour, pathFile):

        finishNow = datetime.now()
        finishData = finishNow.strftime("%d/%m/%Y")
        finishHour = finishNow.strftime("%H:%M:%S")

        format = "%H:%M:%S"
        initHour_dt = datetime.strptime(initHour, format)
        finishHour_dt = datetime.strptime(finishHour, format)
        diferrenceHour = round((finishHour_dt - initHour_dt).total_seconds() / 60, 2)  

        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]

        
        tokenCalculatorInput = (prompt_tokens / 1000) * 0.03
        tokenCalculatorOutput = (completion_tokens / 1000) * 0.06
        totalPrincingToken = round((tokenCalculatorInput + tokenCalculatorOutput) * 4.93, 2)
        

        dataTXT = f"ARQUIVO DE LOG {pathFile}\n\ndata de inicio: {initData}\nhora de inicio: {initHour}\nErros: 0\ndata de conclusão: {finishData}\nhora de conclusão: {finishHour}\ntempo para conclusão: {diferrenceHour} minutos\nquantidade de tokens de entrada: {prompt_tokens}\nquantidade de tokens de saída: {completion_tokens}\ncusto de IA estimado em tokens: R$ {totalPrincingToken} (Dolar atual R$ 4,93)"
        print(f"{dataTXT}")

        with open(pathFile, 'w') as arquivo_novo:
            arquivo_novo.write(dataTXT)



#                           get_prompt_drive
# -------------------------------------------------------------------------
# Função para ler prompt que está em yaml do drive e armazenar em string
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import glob
#  

def get_prompt_drive(pathFile):

        path = pathFile 

        inUse = '* EM USO.yml'

        # Usando glob para encontrar arquivos que correspondam ao padrão
        fileSearch = glob.glob(path + inUse)
        
        # Checando se algum arquivo foi encontrado e lendo o primeiro que corresponder
        if fileSearch:
            fileSearchReady = fileSearch[0]  # Pegando o primeiro arquivo encontrado
            with open(fileSearchReady, 'r', encoding='utf-8') as file:
                prompt = file.read()
            return prompt
        else:
            return "Nenhum prompt foi encontrado"  



#                           request_for_test_gpt4
# -------------------------------------------------------------------------
# Função para fazer chamada de teste na API da openai com GPT-4
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# import openai - para usar api da OPENAI

def request_for_test_gpt4(promptUser):

    try:
        # Notice the use of openai.ChatCompletion here
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Example of a chat-based model
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": promptUser},
            ]
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)




#                           convert_doc_to_txt
# -------------------------------------------------------------------------
# Função para ler documento doc e docx e armazenar em variavel
# -------------------------------------------------------------------------
#                        Bibliotecas a importar
# from docx import Document - biblioteca ler documento docx
# import docx2txt
# import textract

    
def convert_doc_to_txt(filePath):

    if filePath.endswith('.docx'):
        doc = Document(filePath)
        full_text = [para.text for para in doc.paragraphs]
        return '\n'.join(full_text)
    elif filePath.endswith('.doc'):
        text = textract.process(filePath).decode('utf-8')
        return text
    else:
        raise ValueError("Unsupported file format. Only .docx and .doc are supported.")
