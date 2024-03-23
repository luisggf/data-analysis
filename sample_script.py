import pandas as pd
import json
import numpy as np

# extrair valor do atributo da struct json


def extract_attribute(json_str, attribute):
    json_str = json_str.replace("'", "\"").replace("\n", "").replace("\r", "")
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data.get('attributeScores', {}).get(attribute, {}).get('summaryScore', {}).get('value')
    except json.JSONDecodeError:
        return None
    return None


# numero do sample
num_coments = 2000

input_filepath = "./n_data/main-file-w-scrap.csv"

df = pd.read_csv(input_filepath)

# extraindo valores dos atributos
identity_attack = df['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_values = df['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# obtendo media dos atributos notorios da perspective
df['avg_attributes'] = (identity_attack + threat_values) / 2.0

# tratando valores invalidos para ter sample coerente
df['avg_attributes'] = pd.to_numeric(df['avg_attributes'], errors='coerce')
df['avg_attributes'] = df['avg_attributes'].fillna(0)
df['avg_attributes'] = np.clip(df['avg_attributes'], 0, 1)


# discretizar os dados para obter estatisticas
df_greater_than_80 = df[df['avg_attributes'] > 0.80]
df_smaller_than_40 = df[df['avg_attributes'] <= 0.40]
df_between_40_and_80 = df[(df['avg_attributes'] > 0.40)
                          & (df['avg_attributes'] <= 0.80)]

print("Num Tweets > 80: ", len(df_greater_than_80), "Percentage: ", (
    len(df_greater_than_80)/len(df)))

print("Num Tweets <= 40: ", len(df_smaller_than_40), "Porcentage: ", (
    len(df_smaller_than_40)/len(df)))

print("Num Tweets between 80 and 40: ", len(df_between_40_and_80), "Porcentage: ", (
    len(df_between_40_and_80)/len(df)))

# gerar base estratificada
qtd_greater_than_80_stratified = int((
    num_coments * (len(df_greater_than_80)/len(df))))

qtd_smaller_than_40_stratified = int((
    num_coments * (len(df_smaller_than_40)/len(df))))

qtd_between_40_and_80_stratified = int((
    num_coments * (len(df_between_40_and_80)/len(df))))

# downsample para adequar a proporçao da base total
df_greater_than_80 = df_greater_than_80.sample(qtd_greater_than_80_stratified)
print(len(df_greater_than_80))

df_smaller_than_40 = df_smaller_than_40.sample(qtd_smaller_than_40_stratified)
print(len(df_smaller_than_40))

df_between_40_and_80 = df_between_40_and_80.sample(
    qtd_between_40_and_80_stratified)
print(len(df_between_40_and_80))

# unir resultados
df = pd.concat([df_smaller_than_40, df_between_40_and_80, df_greater_than_80])

# embaralhar tweets para diminuir bias
df = df.sample(frac=1).reset_index(drop=True)

df.to_csv("compiled_sample.csv", index=False)
