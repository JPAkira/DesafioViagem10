from django.core.management.base import BaseCommand
import pandas as pd
import os
from django.conf import settings
import csv

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('nome_do_arquivo')

    def handle(self, *args, **options):

        # Criar dataframe
        nome_do_arquivo = options['nome_do_arquivo']
        data = os.path.join(settings.BASE_DIR, nome_do_arquivo)
        df = pd.DataFrame()

        # Erros
        erros = []

        # Abrir arquivo
        with open(data, mode="r") as arquivo_csv:
            leitor_csv = csv.reader(arquivo_csv)

            for linha in leitor_csv:
                registros = len(linha)-1
                if not (registros % 2) == 0:
                    erros.append(f"O arquivo deve conter Eleitorado, uma sequência de 2 valores 'votos' 'partido'")
                    return print(erros)
                votos = iter(linha[1:])
                for voto in votos:
                    
                    # Variaveis.
                    eleitorado = linha[0]
                    try:
                        nr_votos = int(voto)
                    except:
                        nr_votos = voto
                    partido = next(votos).replace(" ", "")
                    partido_nome = get_full_display(partido)

                    # Validação
                    eleitorado_e_valido = validar_string(eleitorado, erros)
                    partido_e_valido = validar_string(partido, erros)
                    nr_votos_e_valido = validar_integer(nr_votos, erros)
                    if not partido_nome:
                        erros.append(f"{partido}: Partido não existente")

                    if not erros:
                        # Adicionar registro após validação
                        df = pd.concat([df, pd.DataFrame.from_records([{'Eleitorado': eleitorado, 'Votos': nr_votos, 'Partido': partido, "Partido Nome": partido_nome}])])
            
        
        df['Porcentagem'] = df['Votos']/df['Votos'].sum() * 100
        df.reset_index(drop=True, inplace=True)

        if erros:
            gerar_arquivo_erro(erros)
            for erro in erros:
                print(erro)
        else:
            df.to_csv("resultado", sep=',', encoding='utf-8')
            print(df)
     
def validar_string(var, erros):
    ''' Validações para campos do tipo texto '''
    if not isinstance(var, str):
        erros.append(f"{var}: Tipo de variável inválido. Somente texto é válido")
        return erros
    if len(var) == 0:
        erros.append(f"{var}: Este valor é obrigatório")
    if len(var) > 155:
        erros.append(f"{var}: Este valor está acima do limite de 155 caracteres")
    if erros:
        return False
    return True

def validar_integer(var, erros):
    ''' Validação para os inteiros '''
    if not isinstance(var, int):
        erros.append(f"{var}: Tipo de variável inválido. Somente inteiro é válido")
        return erros
    if var <= 0:
        erros.append(f"{var}: Este valor é obrigatório")
    if len(str(var)) > 8:
        erros.append(f"{var}: Este valor está acima do limite de 8 digitos")
    if erros:
        return False
    return True

def get_full_display(code):
    ''' Recuperar o valor completo baseado no código '''
    choices = {
        'C': "Partido Conservador",
        'L': "Partido Trabalhista",
        'UKIP': "UKIP",
        'LD': "Liberais Democratas",
        'G': "Partido Verde",
        'Ind': "Independente",
        'SNP': "SNP",
    }

    display = choices.get(str(code))

    return display

def gerar_arquivo_erro(erros):
    erros_file = os.path.join(settings.BASE_DIR, 'erros.txt')
    with open(erros_file, mode="a", encoding='utf-8') as erros_file:
        for erro in erros:
            erros_file.write(erro)
            erros_file.write("\n")
