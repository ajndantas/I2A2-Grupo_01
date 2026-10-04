#Importações necessárias
import cv2 # OPEN-CV para manipulação de imagens
from pytesseract import image_to_string, pytesseract # TESSERACT para OCR
import pdf2image
import numpy as np
from os import name
from magic import from_buffer
from pathlib import Path

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
    
    def __init__(self, lang='por'):
        """
        Inicializa a classe NotaFiscalOCR.

        Args:
            lang (str): Idioma para o Tesseract. Default é 'por' (português).
        """
        self.lang = lang

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
        
        tipo = from_buffer(conteudo, mime=True)
                        
        if tipo == 'application/pdf' or (tipo == 'application/octet-stream' and conteudo.name.endswith('.pdf')):
            return self.carregar_pdf(conteudo)
        
        else:
            print('\nExtraindo o texto da imagem...')
                        
            file_bytes = np.asarray(bytearray(conteudo), dtype=np.uint8) # UTLIZANDO O ARQUIVO EM MEMÓRIA
            imagem = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        
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
        
        print('\nExtraindo o texto do PDF...')
        
        if name == 'nt':
            imagens = pdf2image.convert_from_bytes(conteudo, poppler_path=self.poppler_path) # Devolve uma imagem por página de PDF. Todas empilhadas
            
        elif name == 'posix':
            imagens = pdf2image.convert_from_bytes(conteudo) # Devolve uma imagem por página de PDF. Todas empilhadas
            
        if not imagens:
            raise FileNotFoundError(f"PDF não encontrado ou vazio")
            
        
        #return cv2.cvtColor(np.array(imagens[0]), cv2.COLOR_RGB2BGR) # IMAGENS[0] É A PRIMEIRA PÁGINA DO PDF, CONVERTIDA PARA FORMATO COMPATÍVEL COM OPENCV
        return [cv2.cvtColor(np.array(imagem), cv2.COLOR_RGB2BGR) for imagem in imagens]
    

    def preprocessar_imagem(self, imagem):
        """
        Realiza pré-processamento na imagem:
        - Conversão para escala de cinza.
        - Binarização com threshold fixo.

        Args:
            imagem (numpy.ndarray): Imagem original.

        Returns:
            numpy.ndarray: Imagem binarizada.
        """
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY) 
                     
        _, binarizada = cv2.threshold(cinza, 150, 255, cv2.THRESH_BINARY)
        
        return binarizada
        
    def extrair_texto(self, imagem_processada):
        """
        Executa o OCR utilizando Tesseract na imagem processada.

        Args:
            imagem_processada (numpy.ndarray): Imagem binarizada.

        Returns:
            str: Texto extraído.
        """
        #config = r'--oem 3 --psm 6 -l {}'.format(self.lang)
        config = r'--oem 3 --psm 11 -l {}'.format(self.lang)
        
        #config += ' -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,-/()$%:' #INSERIDO

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

        tipo = from_buffer(conteudo, mime=True)

        if tipo == 'application/pdf' or (tipo == 'application/octet-stream' and conteudo.name.endswith('.pdf')):

            imagens = self.carregar_arquivo(conteudo) # RETORNA UMA IMAGEM OU UMA LISTA DE IMAGENS, NO CASO DE PDF
            imagens_proc = [self.preprocessar_imagem(imagem) for imagem in imagens]

            textos = [self.extrair_texto(imagem_proc) for imagem_proc in imagens_proc]

        else:
            
            imagem = self.carregar_arquivo(conteudo)
            imagem_proc = self.preprocessar_imagem(imagem)

            textos = self.extrair_texto(imagem_proc)


        print("Texto extraído:\n")
        print(textos)

        return textos


# TESTE
if __name__ == "__main__":

    ocr = NotaFiscalOCR()

#    with open("Apólice 1 - automóvel.pdf", "rb") as apolice: 
    with open("SOMPO_D&O_condicoes_gerais.png", "rb") as apolice:
        ocr.main(apolice.read())