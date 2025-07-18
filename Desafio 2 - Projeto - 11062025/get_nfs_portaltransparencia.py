"""
Functions to retrieve and process NF data from Portal Transparência API.
"""

from requests import get
from urllib3 import disable_warnings,exceptions

disable_warnings(exceptions.InsecureRequestWarning)


def consultar_nfs_portaltransparencia(mes, ano):
    """
    Retrieves the Nota Fiscal data from the transparency portal for the given month and year.

    Parameters:
        mes (int or str): Month as number (1-12)
        ano (int or str): Year
    
    Returns:
        Response object or data from the API
    """
    mes = str(mes).zfill(2)
    ano = str(ano)
    
    url = f'https://portaldatransparencia.gov.br/download-de-dados/notas-fiscais/{ano}{mes}'
    
    print('Downloading from URL:', url)
    
    response = get(url, verify=False, timeout=10)
    
    if response.status_code == 200:
        filename = f'notas_fiscais_{ano}{mes}.zip'  # or other appropriate extension
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f'File saved as {filename}')
        return filename
    
    else:
        print(f'Failed to download file: HTTP status {response.status_code}')
        return None

def main(mes,ano):
    
    """
        Main function to execute the primary logic of the script.
    """        
    consultar_nfs_portaltransparencia(mes,ano)

if __name__ == "__main__":
    
    mes='01'
    ano='2025'
    
    main(mes=mes,ano=ano)