from openai import OpenAI
from decouple import config
import pandas as pd
import csv
import os

API_KEY = config('KEY')

# obtido na documentacao https://github.com/openai/openai-python
client = OpenAI(api_key=API_KEY)

print(API_KEY)


def generate_reply(prompt):
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    # Extract and return the generated reply
    reply = response.choices[0].message
    return reply


output_filepath = "gpt_output.csv"

# dividir arquivo em pedaços iteráveis de 20
label_content = pd.read_csv(
    "compiled_sample.csv", chunksize=20)

# sequencia para não sobrecarregar max. tokens
print("DF loaded")
i = 1
for chunk in label_content:
    # prompt padrão
    file = open("control2.config")
    flag = int(file.read())
    # adição da amostra de nossa base ao prompt
    for index, row in chunk.iterrows():
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
        tweet_id = row['id']
        tweet_text = row['text']
        user_prompt += f"\n\nTweet ID: {tweet_id}\n{tweet_text}\n"

        if i > flag:
            reply = generate_reply(user_prompt)
            with open(output_filepath, 'a', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(
                    csv_file, quoting=csv.QUOTE_NONE, escapechar=' ')
                writer.writerow([reply.content])
            file = open("control.config", 'w')
            file.write(str(i))
            file.close()
    print(f"Chunk {i} salvo com sucesso.")
    i += 1
    user_prompt = ""
print("Todos os chunks foram salvos com sucesso.")
