# Instalação no Colab (ignore se já tiver instalado no local)
# %pip install -qqq pytesseract opencv-python matplotlib

#Importações necessárias
import cv2 # OPEN-CV para manipulação de imagens
from pytesseract import image_to_string
import matplotlib.pyplot as plt
import re

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
        self.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        

    def carregar_imagem(self, caminho_imagem):
        """
        Carrega a imagem da nota fiscal a partir do caminho informado.

        Args:
            caminho_imagem (str): Caminho do arquivo de imagem.

        Returns:
            numpy.ndarray: Imagem carregada.

        Exception:
            FileNotFoundError: Se o arquivo não for encontrado.
        """
        imagem = cv2.imread(caminho_imagem)
        if imagem is None:
            raise FileNotFoundError(f"Imagem não encontrada: {caminho_imagem}")
        return imagem

    def exibir_imagem(self, imagem, titulo="Imagem"):
        """
        Exibe uma imagem utilizando Matplotlib.

        Args:
            imagem (numpy.ndarray): Imagem a ser exibida.
            titulo (str): Título da imagem na visualização.
        """
        plt.figure(figsize=(10, 10))
        if len(imagem.shape) == 2:
            plt.imshow(imagem, cmap='gray')
        else:
            plt.imshow(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
        plt.title(titulo)
        plt.axis('off')
        plt.show()

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
        config = r'--oem 3 --psm 6 -l {}'.format(self.lang)
        texto = image_to_string(imagem_processada, config=config)
        return texto

    def extrair_campos(self, texto):
        """
        Extrai campos específicos do texto utilizando expressões regulares:
        - CNPJs
        - Datas
        - Valores em R$

        Args:
            texto (str): Texto extraído pelo OCR.

        Returns:
            dict: Campos extraídos com listas de valores encontrados.
        """
        cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
        data_pattern = r'\d{2}/\d{2}/\d{4}'
        valor_pattern = r'R\$ ?\d{1,3}(?:\.\d{3})*,\d{2}'

        cnpjs = re.findall(cnpj_pattern, texto)
        datas = re.findall(data_pattern, texto)
        valores = re.findall(valor_pattern, texto)

        resultado = {
            'CNPJs': cnpjs,
            'Datas': datas,
            'Valores': valores
        }

        return resultado

    def main(self, caminho_imagem):
        """
        Executa o pipeline completo:
        - Carrega e exibe a imagem original.
        - Pré-processa e exibe a imagem binarizada.
        - Realiza OCR e imprime o texto extraído.
        - Extrai campos específicos e os exibe.

        Args:
            caminho_imagem (str): Caminho do arquivo da nota fiscal.

        Returns:
            tuple: Texto extraído (str), campos extraídos (dict)
        """
        imagem = self.carregar_imagem(caminho_imagem)
        self.exibir_imagem(imagem, "Imagem Original")

        imagem_proc = self.preprocessar_imagem(imagem)
        self.exibir_imagem(imagem_proc, "Imagem Processada")

        texto = self.extrair_texto(imagem_proc)
        print("Texto extraído:\n")
        print(texto)

        #campos = self.extrair_campos(texto)
        #print("\nCampos encontrados:")
        #for campo, valores in campos.items():
        #    print(f"{campo}: {valores}")

        #return texto, campos

# Exemplo de uso
if __name__ == "__main__":
    caminho_imagem = 'nota_fiscal_exemplo.png'  # Nome do arquivo a ser importado
    ocr = NotaFiscalOCR()
    ocr.main(caminho_imagem)

