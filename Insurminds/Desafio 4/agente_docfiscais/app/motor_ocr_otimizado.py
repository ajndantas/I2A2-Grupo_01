#Importações necessárias

import cv2 # OPEN-CV para manipulação de imagens
from pytesseract import image_to_string, pytesseract # TESSERACT para OCR
import pdf2image
import pymupdf # PyMuPDF para extração direta de texto de PDFs digitais
import numpy as np
import os
from os import name
from concurrent.futures import ThreadPoolExecutor
from magic import from_buffer
from pathlib import Path
from fastapi import HTTPException

ENV_PATH = (
                 Path(__file__) # O CAMINHO DO ARQUIVO ATUAL
                .resolve() # RESOLVE O CAMINHO ABSOLUTO
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
            )


class NotaFiscalOCR:
    """
    Classe responsável por realizar OCR em notas fiscais eletrônicas,
    utilizando Tesseract e OpenCV com pré-processamento.

    Atributos:
        lang (str): Idioma para o Tesseract (padrão 'por').
    """
    
    def __init__(self, lang='por', psm=6, dpi=200, max_workers=None, min_chars_pagina=10):
        """
        Inicializa a classe NotaFiscalOCR.

        Args:
            lang (str): Idioma para o Tesseract. Default é 'por' (português).
            psm (int): Modo de segmentação de página do Tesseract (6 = bloco único; 11 = texto esparso, mais lento).
            dpi (int): Resolução usada para rasterizar PDFs.
            max_workers (int): Nº de páginas processadas em paralelo. Default: nº de CPUs.
            min_chars_pagina (int): Mínimo de caracteres para considerar que a página de um PDF tem texto; abaixo disso usa OCR.
        """
        self.lang = lang
        self.psm = psm
        self.dpi = dpi
        self.max_workers = max_workers or os.cpu_count() or 1
        self.min_chars_pagina = min_chars_pagina

        # Cada Tesseract usa 1 thread; o paralelismo é feito entre páginas
        os.environ.setdefault('OMP_THREAD_LIMIT', '1')

        # PARA WINDOWS
        if name == 'nt':
            self.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" 
            self.poppler_path = f"{ENV_PATH}/poppler/poppler/poppler-24.08.0/Library/bin"
            
        
        # PARA LINUX
        elif name == 'posix':
            self.tesseract_cmd = "/usr/bin/tesseract"            
                        
        pytesseract.tesseract_cmd = self.tesseract_cmd
        

    def carregar_arquivo(self, conteudo: bytes):
        """
        Carrega a imagem da nota fiscal a partir do caminho informado.

        Args:
            conteudo (Bytes): bytes do arquivo de imagem.

        Returns:
            numpy.ndarray: Imagem carregada.

        Exception:
            FileNotFoundError: Se o arquivo não for encontrado.
        """
        
        if self._eh_pdf(conteudo):
            return self.carregar_pdf(conteudo)

        else:
            file_bytes = np.frombuffer(conteudo, dtype=np.uint8) # UTLIZANDO O ARQUIVO EM MEMÓRIA
            imagem = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
                        
            if imagem is None or imagem.size == 0:
                raise FileNotFoundError(f"Imagem não encontrada ou vazia")

            return imagem
        
    
    def carregar_pdf(self, conteudo: bytes):
        """
        Carrega um PDF e converte cada página do PDF em uma imagen, gerando uma lista de imagens. 

        Args:
            conteudo (bytes): Bytes do arquivo PDF.

        Returns:
            numpy.ndarray: Imagem da primeira página do PDF.

        Exception:
            FileNotFoundError: Se o arquivo não for encontrado.
        """
        
        # Escala de cinza direto no Poppler (evita conversão RGB->BGR->cinza)
        opcoes = dict(dpi=self.dpi, grayscale=True, thread_count=self.max_workers)
        if name == 'nt':
            opcoes['poppler_path'] = self.poppler_path

        imagens = pdf2image.convert_from_bytes(conteudo, **opcoes) # Devolve uma imagem por página de PDF

        if not imagens:
            raise FileNotFoundError(f"PDF não encontrado ou vazio")

        return [np.array(imagem) for imagem in imagens]
    

    def extrair_texto_pdf(self, conteudo: bytes) -> str:
        """
        Extrai o texto diretamente de um PDF digital (não escaneado), sem OCR.

        Páginas sem camada de texto (ex.: páginas escaneadas dentro de um PDF misto)
        são processadas por OCR como fallback.

        Args:
            conteudo (bytes): Bytes do arquivo PDF.

        Returns:
            str: Texto de todas as páginas, separado por quebra de linha.
        """
        with pymupdf.open(stream=conteudo, filetype='pdf') as documento:
            if documento.page_count == 0:
                raise FileNotFoundError("PDF não encontrado ou vazio")

            textos = [pagina.get_text('text', sort=True) for pagina in documento]

            # Páginas sem texto selecionável: OCR apenas nelas
            sem_texto = [i for i, texto in enumerate(textos) if len(texto.strip()) < self.min_chars_pagina]
            if sem_texto:
                imagens = {}
                for i in sem_texto:
                    pixmap = documento[i].get_pixmap(
                        dpi=self.dpi,
                        colorspace=pymupdf.csGRAY,
                        alpha=False,
                    )
                    imagens[i] = np.frombuffer(
                        pixmap.samples,
                        dtype=np.uint8,
                    ).reshape(pixmap.height, pixmap.width)

                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    ocr = executor.map(
                        lambda i: self.extrair_texto(self.preprocessar_imagem(imagens[i])),
                        sem_texto,
                    )
                    for i, texto in zip(sem_texto, ocr):
                        textos[i] = texto


        return '\n'.join(textos)

    def preprocessar_imagem(self, imagem):
        """
        Realiza pré-processamento na imagem:
        - Conversão para escala de cinza.
        - Binarização com threshold de Otsu.

        Args:
            imagem (numpy.ndarray): Imagem original.

        Returns:
            numpy.ndarray: Imagem binarizada.
        """
        cinza = imagem if imagem.ndim == 2 else cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

        _, binarizada = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binarizada
        
    def extrair_texto(self, imagem_processada):
        """
        Executa o OCR utilizando Tesseract na imagem processada.

        Args:
            imagem_processada (numpy.ndarray): Imagem binarizada.

        Returns:
            str: Texto extraído.
        """
        config = f'--oem 3 --psm {self.psm} -l {self.lang}'

        altura = imagem_processada.shape[0]
        altura_maxima = 20000
        sobreposicao = 200
        passo = altura_maxima - sobreposicao
        textos = [
            image_to_string(
                imagem_processada[inicio:inicio + altura_maxima, :],
                config=config,
            )
            for inicio in range(0, altura, passo)
        ]
        
        return '\n'.join(textos)

    def main(self, conteudo: bytes) -> str:
        """
        Executa o pipeline completo:
        - Carrega e exibe a imagem original.
        - Pré-processa e exibe a imagem binarizada.
        - Realiza OCR e imprime o texto extraído.
        - Extrai campos específicos e os exibe.

        Args:
            caminho_arquivo (str): Caminho do arquivo da nota fiscal.

        Returns:
            tuple: Texto extraído (str), campos extraídos (dict)
        """
        
        print("Extraíndo texto...\n")

        if self._eh_pdf(conteudo):

            # PDF digital: leitura direta da camada de texto (OCR só nas páginas sem texto)
            textos = self.extrair_texto_pdf(conteudo)

        else:
            
            imagem = self.carregar_arquivo(conteudo)
            imagem_proc = self.preprocessar_imagem(imagem)

            try:
                textos = self.extrair_texto(imagem_proc)                

            except pytesseract.TesseractError as e: # Erro image too large
                raise HTTPException(status_code=500, detail=f"Erro ao extrair texto: {e}. Converta a imagem para PDF e tente novamente.")

        
        print("Texto extraído:\n", textos)

        return textos

    @staticmethod
    def _eh_pdf(conteudo: bytes) -> bool:
        """Detecta PDF pelo conteúdo (uma única chamada ao libmagic)."""
        return from_buffer(conteudo, mime=True) == 'application/pdf'


# TESTE
if __name__ == "__main__":

    ocr = NotaFiscalOCR()

    #with open("essor_responsa_civil_diretores_administradores_conselheiros.pdf", "rb") as apolice: 
    with open("SOMPO_D&O_condicoes_gerais.png", "rb") as apolice:
        ocr.main(apolice.read())