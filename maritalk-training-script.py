import maritalk
import pandas as pd
from decouple import config
import csv


# arquivo de saida
output_filepath = "maritalk_output.csv"
# arquivo com 400 linhas exemplo
label_content = pd.read_csv(
    'compiled_sample.csv', chunksize=5, usecols=['id', 'text'])

# prompt padrão
user_prompt = f"""Contexto: Identificação e Rotulagem de Tweets - Eleições Brasileiras 2022 e Ataques ao Palácio do Planalto (8 de janeiro) 
                Por favor, avalie os tweets a seguir e rotule-os com base nos seguintes critérios:
                Objetivo: Identificar e rotular tweets que contenham ataques à identidade ou ameaças, no contexto das eleições brasileiras de 2022 e aos eventos de 8 de janeiro com ataque ao Palácio do Planalto, Congresso, STF e Senado Federal.
                Critérios de Rotulagem:
                - SIM: Se o tweet se encaixa em um dos dois critérios abaixo:
                1) Ataques à Identidade: Tweets que contêm linguagem ou conteúdo que ataca, discrimina, marginaliza ou mostra hostilidade/intolerância com base em grupo, sociedade, etnia, religião, gênero, etc.
                2) Ameaças: Tweets que promovem, incentivam ou glorificam o rompimento da ordem institucional, atos de violência, ideologias violentas ou figuras históricas associadas à violência extrema ou violação dos direitos humanos e sociais. Inclui a promoção de manifestações violentas, defesa de regimes autoritários ou ideologias extremistas (por exemplo, fascismo, nazismo, glorificação de juntas militares).
                3) Tweets apenas noticiando os eventos, sem explicitamente estimular e motivar, não deverão ser considerados.
                - NAO: Tweets que não contêm linguagem ou conteúdo que se enquadre nos critérios de 'SIM'.
                - INCONCLUSIVO: Se você tem alguma dúvida quanto a sim ou não.
                Instruções Adicionais:
                - Retorne o ID do Tweet passado como parâmetro e o rótulo apenas.
                - Utilize formato CSV.
                - Avalie o contexto do tweet para determinar a intenção por trás do conteúdo.
                - Considere tanto o texto explícito quanto às insinuações implícitas que podem sugerir ataques à identidade ou ameaças.
                - Ignore tweets que contenham críticas políticas ou sociais construtivas, a menos que promovam violência ou intolerância.
                Conteúdo a ser rotulado: """


print("DF loaded")
i = 1
for chunk in label_content:
    model = maritalk.MariTalk(
        # No momento, suportamos os modelos sabia-2-medium e sabia-2-small
        key=config('SK_MARITALK'),
        model='sabia-2-medium'
    )

    # prompt padrão
    file = open("control_maritalk.config")
    flag = int(file.read())

    if i > flag:
        # adição da amostra de nossa base ao prompt
        user_prompt = f"""Contexto: Identificação e Rotulagem de Tweets - Eleições Brasileiras 2022 e Ataques ao Palácio do Planalto (8 de janeiro) 
                        Por favor, avalie os tweets a seguir e rotule-os com base nos seguintes critérios:
                        Objetivo: Identificar e rotular tweets que contenham ataques à identidade ou ameaças, no contexto das eleições brasileiras de 2022 e aos eventos de 8 de janeiro com ataque ao Palácio do Planalto, Congresso, STF e Senado Federal.
                        Critérios de Rotulagem:
                        - SIM: Se o tweet se encaixa em um dos dois critérios abaixo:
                        1) Ataques à Identidade: Tweets que contêm linguagem ou conteúdo que ataca, discrimina, marginaliza ou mostra hostilidade/intolerância com base em grupo, sociedade, etnia, religião, gênero, etc.
                        2) Ameaças: Tweets que promovem, incentivam ou glorificam o rompimento da ordem institucional, atos de violência, ideologias violentas ou figuras históricas associadas à violência extrema ou violação dos direitos humanos e sociais. Inclui a promoção de manifestações violentas, defesa de regimes autoritários ou ideologias extremistas (por exemplo, fascismo, nazismo, glorificação de juntas militares).
                        3) Tweets apenas noticiando os eventos, sem explicitamente estimular e motivar, não deverão ser considerados.
                        - NAO: Tweets que não contêm linguagem ou conteúdo que se enquadre nos critérios de 'SIM'.
                        - INCONCLUSIVO: Se você tem alguma dúvida quanto a sim ou não.
                        Instruções Adicionais:
                        - Retorne o ID do Tweet passado como parâmetro e o rótulo apenas, nada além disso.
                        - Utilize formato CSV.
                        - Avalie o contexto do tweet para determinar a intenção por trás do conteúdo.
                        - Considere tanto o texto explícito quanto às insinuações implícitas que podem sugerir ataques à identidade ou ameaças.
                        - Ignore tweets que contenham críticas políticas ou sociais construtivas, a menos que promovam violência ou intolerância.
                        Exemplo de Saída:
                        "1596911784883109889,SIM
                        1603328988415401985,NAO
                        1612686812295888900,SIM"
                        Conteúdo a ser rotulado: \n"""

        user_prompt = user_prompt + \
            '\n'.join([f"{id}, {text}" for id, text in zip(
                chunk['id'], chunk["text"])])
        reply = model.generate(user_prompt)
        for model_answer in reply['answer'].split("\n"):
            with open(output_filepath, 'a') as the_file:
                the_file.write(model_answer+"\n")
        file = open("control_maritalk.config", 'w')
        file.write(str(i))
        file.close()
    print(f"Chunk {i} salvo com sucesso.")
    i += 1
    user_prompt = ""
print("Todos os chunks foram salvos com sucesso.")
