import requests
import shutil
import os
import sys
import tempfile

def download_by_url(url: str, output: str):
    """
        Downloads a file from a url to a designed path.
    """
    with requests.get(url, stream=True) as r:
        with open(output, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def download(output_directory: str, date: str):
    """
        Downloads a file on http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/
        using the given date.
        output_directory: The directory where the file should be downloaded.
        date: The date selected for the file in the format YYYYMM.
    """
    filename = f'inf_diario_fi_{date}.csv'
    output = os.path.join(output_directory, filename)
    url = f'http://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/{filename}'

    download_by_url(url, output)

    return output


import csv
from pprint import pprint
from datetime import datetime
fundos = {}

#Este script deverá receber como parâmetros 
# o mês desejado no formato YYYYMM, 
# o caminho do diretório onde estão os arquivos, 
# e poderá receber um ou mais CNPJs. 
# Se uma lista de CNPJs for passada por parâmetro, 
# o script deverá calcular os valores para cada CNPJ. 
# Caso nenhum CNPJ seja informado, o script deverá gerar um relatório de todos os fundos disponíveis.

def calculate_fields(date: str, file_path: str, cnpj_list: list = []):

    with open(file_path) as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)

        dt_comptc_index = header.index('DT_COMPTC')
        cnpj_fundo_index = header.index('CNPJ_FUNDO')
        
        date = datetime.strptime(date, '%Y%m')

        for i, row in enumerate(reader):
            
            data_competencia = row[dt_comptc_index]
            data_competencia = datetime.strptime(data_competencia, '%Y-%m-%d')

            cnpj = row[cnpj_fundo_index]

            """
                Compare if the date give in the arguments is different of the date in the file
            """
            if data_competencia.year != date.year and data_competencia.month != date.month:
                continue
            
            if len(cnpj_list) and cnpj not in cnpj_list:
                continue

            if not fundos.get(cnpj, False):
                #Make a dictionary
                fundos[cnpj] = {col:[] for col in header}
            
            for i, col in enumerate(row):
                #Add value of each line referent an specific CNPJ
                fundos[cnpj][header[i]].append(col)
                

    #Iterating by CNPJ and calculates quota variation, value captured and value redeemed
    for key, fundo in fundos.items():
        
        cotas = [float(x) for x in fundo['VL_QUOTA']]
        val_captado = [float(x) for x in fundo['CAPTC_DIA']]
        val_resgatado = [float(x) for x in fundo['RESG_DIA']]

        fundos[key]['var_porc_cota'] = ((cotas[-1] / cotas[0]) - 1) * 100
        fundos[key]['val_captado'] = sum(val_captado)
        fundos[key]['val_retirado'] = sum(val_resgatado)

        pprint(fundos[key])

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Você esqueceu de passar o ano e o mês')
        exit(1)

    path = download(tempfile.gettempdir(), sys.argv[1])
    
    if len(sys.argv) <= 2:
        calculate_fields(sys.argv[1],path)

    else:
        calculate_fields(sys.argv[1],path, sys.argv[2])
