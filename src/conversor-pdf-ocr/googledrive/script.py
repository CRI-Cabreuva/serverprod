#!/usr/bin/env python3

import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract
from PIL import Image
from spellchecker import SpellChecker
import os
import shutil
import datetime
import numpy as np
import openai


# Configurar o pytesseract
pytesseract.pytesseract.tesseract_cmd = (r'/usr/bin/tesseract')

def file_size(file_path):
    size_in_bytes = os.path.getsize(file_path)
    size_in_kb = size_in_bytes / 1024
    return size_in_kb < 20000

def extrair_imagens_do_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    imagens = []

    for i in range(len(doc)):
        for img_index, img in enumerate(doc.get_page_images(i)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            try:
                # Se pix é CMYK ou tem canal alfa, mas verifica antes se o espaço de cores é nulo
                if pix.colorspace and (pix.n < 4 or pix.alpha):
                    # Remover canal alfa se existir e converter para RGB se necessário
                    if pix.alpha or pix.colorspace.name != "RGB":
                        pix1 = fitz.Pixmap(fitz.csRGB, pix) if pix.colorspace else None
                        if pix1:  # Verifica se a conversão foi bem-sucedida
                            pil_img = Image.frombytes("RGB", (pix1.width, pix1.height), pix1.samples)
                            imagens.append(np.array(pil_img))
                        pix1 = None
                    else:
                        pil_img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                        imagens.append(np.array(pil_img))
                elif not pix.colorspace:  # Se o espaço de cores for nulo, pode optar por pular ou tratar de forma diferente
                    print(f"Aviso: Imagem na página {i}, índice {img_index} tem espaço de cores indefinido e será ignorada.")
            except Exception as e:
                print(f"Erro ao processar imagem na página {i}, índice {img_index}: {e}")
            finally:
                pix = None  # Garantir que pix seja descartado corretamente

    return imagens

def preprocessar_imagem_para_ocr(imagem):
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, binarizada = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    nitida = cv2.GaussianBlur(binarizada, (0,0), 3)
    nitida = cv2.addWeighted(binarizada, 1.5, nitida, -0.5, 0)
    return nitida

def extrair_texto(imagem):
    return pytesseract.image_to_string(imagem)

# diretorio_base = "/home/dev/resources/test"  # Substitua pelo caminho do seu diretório "digital"
diretorio_base = "/home/dev/resources/googledrive/" 
data_limite = datetime.datetime(2024, 1, 15)  # Data limite para a modificação dos arquivos
extensoes_permitidas = ['.pdf']  # Adicione as extensões de arquivo que você deseja incluir

def listar_arquivos_modificados(diretorio, extensoes):
    arquivos_modificados = []

    for pasta_atual, subpastas, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            nome, extensao = os.path.splitext(arquivo)
            if extensao in extensoes:
                # Verifica se existe um arquivo .txt correspondente no mesmo diretório
                caminho_txt = os.path.join(pasta_atual, nome +  extensao + '.ocr' + '.txt')
                if not os.path.exists(caminho_txt):
                    caminho_completo = os.path.join(pasta_atual, arquivo)
                    data_modificacao = datetime.datetime.fromtimestamp(os.path.getmtime(caminho_completo))
                    
                    if data_modificacao > data_limite:
                        arquivos_modificados.append((nome, extensao))
                        # print(f"Nome: {nome}; Extensão: {extensao} Caminho Completo: {caminho_completo}; data: {data_modificacao}; Caminho Diretório: {pasta_atual}")

                        # # Nome do arquivo onde salvar os resultados
                        nome_arquivo_saida = os.path.join(pasta_atual, nome +  extensao + '.ocr' + '.txt')
                        # print(f'Arquivo de Saida: {nome_arquivo_saida}\nArquivo Original: {caminho_completo}')


                        fileSize = file_size(caminho_completo)

                        # if fileSize:

                        imagens = extrair_imagens_do_pdf(caminho_completo)

                        status = os.path.join(pasta_atual, nome + '_aguarde_' + '.txt')

                        # Abrir (ou criar) o arquivo de saída e processar cada imagem
                        print(f'Arquivo sendo processado: {nome}\nCaminho: {caminho_completo}\n')
                        with open(status, 'w') as caminho_status:
                            for imagem in imagens:
                                imagem_processada = preprocessar_imagem_para_ocr(imagem)
                                texto = extrair_texto(imagem_processada)
                                caminho_status.write(texto + "\n\n")

                        os.rename(status, nome_arquivo_saida)

                        
                        print(f'Arquivo: {nome_arquivo_saida}\n\n')

    return arquivos_modificados

if os.path.exists(diretorio_base):
    arquivos_modificados = listar_arquivos_modificados(diretorio_base, extensoes_permitidas)
    for nome, extensao in arquivos_modificados:
        print(f"Nome: {nome}, Extensão: {extensao}")
else:
    print(f"O diretório {diretorio_base} não existe.")



