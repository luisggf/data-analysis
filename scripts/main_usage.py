import json
import pandas as pd
import tldextract
from newspaper import Article
import ast
import numpy as np
import matplotlib.pyplot as plt
from pywebcopy import save_webpage
from urllib.parse import urlparse
import re
import requests
import urllib.request as request
import urllib.parse as parse
from urlextract import URLExtract
from retrying import retry
from unshortenit import UnshortenIt
import urllib
import time


def extract_attribute(json_str, attribute):
    json_str = json_str.replace("'", "\"").replace("\n", "").replace("\r", "")
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data.get('attributeScores', {}).get(attribute, {}).get('summaryScore', {}).get('value')
    except json.JSONDecodeError:
        return None
    return None


# LER SCRAPS CERTIFICADOS E NÃO CERTIFICADOS E PLOTAR CDF DOS ATRIBUTOS THREAT E ID_ATTACK PARA CADA UM
df = pd.read_csv("./Dados/Scrap-Result/certified_scrap.csv",
                 sep='|', encoding='utf-8')
df1 = pd.read_csv("./Dados/Scrap-Result/uncertified_scrap.csv",
                  sep='|', encoding='utf-8')


df['perspective'] = df['perspective'].astype(str)

attributes = ['THREAT', 'IDENTITY_ATTACK']

plt.figure(figsize=(4, 3))

colors_certificadas = {'THREAT': 'b', 'IDENTITY_ATTACK': '#FF6603'}

for attribute in attributes:
    df[attribute] = df['perspective'].apply(
        lambda x: extract_attribute(x, attribute))

    df_filtered = df.dropna(subset=[attribute])

    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)

    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    plt.plot(sorted(values), cumulative_values,
             label=f'Certificadas - {attribute}', color=colors_certificadas[attribute])

colors_nao_certificadas = {'THREAT': 'b', 'IDENTITY_ATTACK': '#FF6603'}

for attribute in attributes:
    df1[attribute] = df1['perspective'].apply(
        lambda x: extract_attribute(x, attribute))

    df_filtered = df1.dropna(subset=[attribute])

    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)

    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    plt.plot(sorted(values), cumulative_values,
             label=f'Não Certificadas - {attribute}', linestyle='dashed', color=colors_nao_certificadas[attribute])

plt.xlabel(f'#Ameaça #Ataque à Identidade')
plt.ylabel('CDF')
plt.legend(fontsize=7)
plt.grid()
plt.show()


# PLOTAR MULTIPLOS A CDF DE MULTIPLOS ATRIBUTOS SEM FILTRO DE CERTIFICADAS OU NÃO CERTIFICADAS


attributes = ['THREAT', 'TOXICITY', 'SEVERE_TOXICITY',
              'PROFANITY', 'INSULT', 'IDENTITY_ATTACK']

plt.figure(figsize=(4, 3))

for attribute in attributes:
    df[attribute] = df['perspective'].apply(
        lambda x: extract_attribute(x, attribute))
    df_filtered = df.dropna(subset=[attribute])
    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)
    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)
    plt.plot(sorted(values), cumulative_values, label=attribute)

plt.xlabel('Valor')
plt.ylabel('Distribuição Acumulada')
plt.title('Distribuição Acumulada dos Atributos')
plt.legend()
plt.grid()
plt.show()


# RECEBER ESTATISTICAS DAS METRICAS DE ENGAJAMENTO

df = pd.read_csv("./Dados/main-file.csv", encoding='utf-8')

identity_attack = df['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
toxicity_values = df['perspective'].apply(
    lambda x: extract_attribute(x, 'TOXICITY'))

df['avg_attributes'] = (identity_attack + toxicity_values) / 2.0

# df_filtrado = df[df['avg_attributes'] > 0.8]
df_filtrado = df
media_impressions = df_filtrado['public_metrics.impression_count'].mean()
std_impressions = df_filtrado['public_metrics.impression_count'].std()
max_impressions = df_filtrado['public_metrics.impression_count'].max()
median_impressions = df_filtrado['public_metrics.impression_count'].median()

media_likes = df_filtrado['public_metrics.like_count'].mean()
std_likes = df_filtrado['public_metrics.like_count'].std()
max_likes = df_filtrado['public_metrics.like_count'].max()
median_likes = df_filtrado['public_metrics.like_count'].median()

media_retweets = df_filtrado['public_metrics.retweet_count'].mean()
std_retweets = df_filtrado['public_metrics.retweet_count'].std()
max_retweets = df_filtrado['public_metrics.retweet_count'].max()
median_retweets = df_filtrado['public_metrics.retweet_count'].median()

media_replys = df_filtrado['public_metrics.reply_count'].mean()
std_replys = df_filtrado['public_metrics.reply_count'].std()
max_replys = df_filtrado['public_metrics.reply_count'].max()
median_replys = df_filtrado['public_metrics.reply_count'].median()

media_quotes = df_filtrado['public_metrics.quote_count'].mean()
std_quotes = df_filtrado['public_metrics.quote_count'].std()
max_quotes = df_filtrado['public_metrics.quote_count'].max()
median_quotes = df_filtrado['public_metrics.quote_count'].median()


print("Métricas Públicas para Linhas com Média INSULT_ATTACK_TOXICITY > 0.8:")
print("Número de Tweets:", len(df_filtrado))
print("Impressions - Média:", round(media_impressions, 2), "Desvio Padrão:",
      round(std_impressions, 2), "Máximo:", max_impressions, "Mediana:", median_impressions)
print("Likes - Média:", round(media_likes, 2), "Desvio Padrão:",
      round(std_likes, 2), "Máximo:", max_likes, "Mediana:", median_likes)
print("Retweets - Média:", round(media_retweets, 2), "Desvio Padrão:",
      round(std_retweets, 2), "Máximo:", max_retweets, "Mediana:", median_retweets)
print("Quotes - Média:", round(media_quotes, 2), "Desvio Padrão:",
      round(std_quotes, 2), "Máximo:", max_quotes, "Mediana:", median_quotes)
print("Replys - Média:", round(media_replys, 2), "Desvio Padrão:",
      round(std_replys, 2), "Máximo:", max_replys, "Mediana:", median_replys)


# PLOTAR CDF DO ATRIBUTOS 'X' DAS METRICAS DE ENGAJAMENTO CONSIDERANDO CERTIFICADAS E NÃO CERTIFICADAS

df_confiaveis = pd.read_csv("./Dados/certified.csv", encoding='utf-8')
df_nao_confiaveis = pd.read_csv("./Dados/uncertified.csv", encoding='utf-8')


idattack_val = df_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
idattack_val2 = df_nao_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = df_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
threat_val2 = df_nao_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

df_confiaveis['media'] = (idattack_val + threat_val) / 2
df_nao_confiaveis['media'] = (idattack_val2 + threat_val2) / 2

df_confiaveis_filtrado = df_confiaveis[df_confiaveis['media'] > 0.8]
df_nao_confiaveis_filtrado = df_nao_confiaveis[df_nao_confiaveis['media'] > 0.8]
atributo = 'public_metrics.like_count'

cores = ['b', '#fc6603']

df_confiaveis = df_confiaveis[df_confiaveis[atributo] > 0]
sorted_confiaveis = df_confiaveis[atributo].sort_values()
sorted_confiaveis_filtrado = df_confiaveis_filtrado[atributo].sort_values()

df_nao_confiaveis = df_nao_confiaveis[df_nao_confiaveis[atributo] > 0]
sorted_nao_confiaveis_filtrado = df_nao_confiaveis_filtrado[atributo].sort_values(
)
sorted_nao_confiaveis = df_nao_confiaveis[atributo].sort_values()

n_confiaveis = len(sorted_confiaveis)
n_confiaveis_filtrado = len(sorted_confiaveis_filtrado)
n_nao_confiaveis = len(sorted_nao_confiaveis)
n_nao_confiaveis_filtrado = len(sorted_nao_confiaveis_filtrado)

cdf_confiaveis = np.arange(1, n_confiaveis + 1) / n_confiaveis
cdf_confiaveis_filtrado = np.arange(
    1, n_confiaveis_filtrado + 1) / n_confiaveis_filtrado
cdf_nao_confiaveis = np.arange(1, n_nao_confiaveis + 1) / n_nao_confiaveis
cdf_nao_confiaveis_filtrado = np.arange(
    1, n_nao_confiaveis_filtrado + 1) / n_nao_confiaveis_filtrado

plt.figure(figsize=(4, 3))
plt.semilogx(sorted_confiaveis, cdf_confiaveis,
             label='Certificada', color=cores[0])
plt.semilogx(sorted_confiaveis_filtrado, cdf_confiaveis_filtrado,
             label='> 0.8', linestyle='dashed', color=cores[0])
plt.semilogx(sorted_nao_confiaveis, cdf_nao_confiaveis,
             label='Não Certificada', color=cores[1])
plt.semilogx(sorted_nao_confiaveis_filtrado, cdf_nao_confiaveis_filtrado,
             linestyle='dashed', label='> 0.8', color=cores[1])

plt.xlabel("# Likes")
plt.ylabel("CDF")
plt.grid(True)
plt.legend(fontsize=7)
plt.show()


# CCOMO URLS DO CAMPO TEXT FORAM EXPANDIDAS (MAIN)

def get_url(text):
    regex = r"^(?:\n|\\n|n)?(.*)$"
    padrao = r"\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    list_url_decodified = []
    list_urls = re.findall(padrao, text)
    urls_filtered = [re.sub(regex, r"\1", url[0]) for url in list_urls]

    print(urls_filtered)
    list_urls_new = []
    for url in urls_filtered:
        if url != '':
            url = re.sub('\\\n', '', url)
            url = re.sub('\\n', '', url)
            url = url.split("\\n")[0]
            list_urls_new.append(url)
    urls_filtered = list_urls_new
    del list_urls_new
    for url in urls_filtered:
        url = get_protocol(url)
        try:
            response = requests.head(url, allow_redirects=True)
            list_url_decodified.append(response.url)
            print(response.url)
        except Exception as e:
            print('Error with:', url, str(e))
            pass
    return list_url_decodified


def get_protocol(url, proxy=None):
    try:
        parsed_url = parse.urlsplit(url.strip())
        url = parse.urlunsplit((
            parsed_url.scheme or "http",
            parsed_url.netloc or parsed_url.path,
            parsed_url.path.rstrip("/") + "" if parsed_url.netloc else "",
            parsed_url.query,
            parsed_url.fragment
        ))

        if proxy:
            handler = request.ProxyHandler(
                dict.fromkeys(("http", "https"), proxy))
            opener = request.build_opener(
                handler, request.ProxyBasicAuthHandler())
        else:
            opener = request.build_opener()

        with opener.open(url) as response:
            expanded_url = urllib.request.urlopen(response.url).geturl()
            if "gettr" in expanded_url:
                return
            return expanded_url
    except:
        return url


chunksize = 1600

file_id = 1

input_filepath = "Tweets-Retweet-unicos-part0"+str(file_id)
output_filepath = "result-part0"+str(file_id)+".csv"
columns = ["id", "text"]

df = pd.read_csv(input_filepath, chunksize=chunksize, names=[
                 'id', 'referenced_tweets.retweeted.id', 'text'])

print("DF loaded")
i = 1
for chunk in df:
    file = open("control.config0"+str(file_id))
    flag = int(file.read())

    if i > flag:
        chunk['urls'] = chunk['text'].apply(get_url)
        chunk.to_csv(output_filepath, mode='a', header=(i == 1),
                     index=False, columns=columns + ['urls'])
        file = open("control.config0"+str(file_id), 'w')
        file.write(str(i))
        file.close()
        print(f"Chunk {i} salvo com sucesso.")
    i += 1
print("Todos os chunks foram salvos com sucesso.")


# COMO MERGE FOI FEITO ENTRE ARQUIVO COM PERSPECTIVE E BASE DE DADOS BRUTA

df = pd.read_csv('./Dados/dataframe-all-attributes.csv')

df['created_at'] = pd.to_datetime(df['created_at'])

# ordem decrescente para deixar MAIS RECENTES no topo
df = df.sort_values(by='created_at', ascending=False)
print(df['created_at'].tail(1))
print(df['created_at'].head(1))

# manter apenas linhas MAIS RECENTES do df, ou seja todas diferentes das mais recentes duplicadas são removidas
# df = df.drop_duplicates(subset='text')

# df.to_csv("arquivo_sem_duplicatas_mais_recentes.csv", index=False)


# COMO HISTOGRAMA FOI CALCULADO


def check_keywords(text, keylist, count_dict):
    words = re.findall(r'\b(\w+)\b', text)
    for word in words:
        if word in keylist:
            if word == 'se' or word == 'SE':
                continue
            count_dict[word] += 1


df = pd.read_csv("main-file.csv")


keywords = ['lula', 'lulista', 'bolsonaro', 'bozo', 'jair', 'simone', 'felipe', 'davila', "d'avila" "d'ávila", 'ciro', 'tebet', 'kelmon', 'padre', 'luiz inacio', 'luiz inácio', 'inácio',
            'soraya', 'jair bolsonaro', 'pt', 'pdt', 'novo', '22', '13', 'ptb', 'mdb', 'pcb', 'pl', 'bolsonarista', 'ptista', 'bolsominion', 'comunista', 'socialista']


estados = ['AC', 'Acre',
           'AL', 'Alagoas',
           'AP', 'Amapá',
           'AP', 'Amapa',
           'AM', 'Amazonas',
           'BA', 'Bahia',
           'CE', 'Ceará',
           'CE', 'Ceara',
           'DF', 'Distrito Federal',
           'ES', 'Espírito Santo',
           'ES', 'Espirito Santo',
           'GO', 'Goiás',
           'GO', 'Goias',
           'MA', 'Maranhão',
           'MA', 'Maranhao',
           'MT', 'Mato Grosso',
           'MS', 'Mato Grosso do Sul',
           'MG', 'Minas Gerais',
           'PA', 'Pará',
           'PB', 'Paraíba',
           'PR', 'Paraná',
           'PE', 'Pernambuco',
           'PI', 'Piauí',
           'RJ', 'Rio de Janeiro',
           'RN', 'Rio Grande do Norte',
           'RS', 'Rio Grande do Sul',
           'RO', 'Rondônia',
           'RO', 'Rondonia',
           'RR', 'Roraima',
           'SC', 'Santa Catarina',
           'SP', 'São Paulo',
           'SP', 'Sao Paulo',
           'SE', 'Sergipe',
           'TO', 'Tocantins']

state_mapping = {
    'Acre': 'AC',
    'Alagoas': 'AL',
    'Amapá': 'AP',
    'Amapa': 'AP',
    'Amazonas': 'AM',
    'Bahia': 'BA',
    'Ceará': 'CE',
    'Ceara': 'CE',
    'Distrito Federal': 'DF',
    'Espírito Santo': 'ES',
    'Espirito Santo': 'ES',
    'Goiás': 'GO',
    'Goias': 'GO',
    'Maranhão': 'MA',
    'Maranhao': 'MA',
    'Mato Grosso': 'MT',
    'Mato Grosso do Sul': 'MS',
    'Minas Gerais': 'MG',
    'Pará': 'PA',
    'Paraíba': 'PB',
    'Paraiba': 'PB',
    'Paraná': 'PR',
    'Parana': 'PR',
    'Pernambuco': 'PE',
    'Piauí': 'PI',
    'Piaui': 'PI',
    'Rio de Janeiro': 'RJ',
    'Rio Grande do Norte': 'RN',
    'Rio Grande do Sul': 'RS',
    'Rondônia': 'RO',
    'Rondonia': 'RO',
    'Roraima': 'RR',
    'Santa Catarina': 'SC',
    'São Paulo': 'SP',
    'Sao Paulo': 'SP',
    'Sergipe': 'SE',
    'Tocantins': 'TO'
}


def extract_attribute(json_str, attribute):
    json_str = json_str.replace("'", "\"").replace("\n", "").replace("\r", "")
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data.get('attributeScores', {}).get(attribute, {}).get('summaryScore', {}).get('value')
    except json.JSONDecodeError:
        return None
    return None


id_attack_values = df['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
toxicity_values = df['perspective'].apply(
    lambda x: extract_attribute(x, 'TOXICITY'))

df['media'] = (id_attack_values + toxicity_values) / 2.0

df_filtrado = df[df['media'] > 0.8]

keyword_counts = {keyword: 0 for keyword in keywords}
estado_counts = {estado: 0 for estado in estados}


df_filtrado['text'].apply(lambda text: check_keywords(
    text.lower(), keywords, keyword_counts))
df_filtrado['text'].apply(
    lambda text: check_keywords(text, estados, estado_counts))

for state_name, state_abbrev in state_mapping.items():
    if state_name in estado_counts and state_abbrev in estado_counts:
        estado_counts[state_abbrev] += estado_counts[state_name]
        del estado_counts[state_name]

sorted_keyword_counts = {k: v for k, v in sorted(
    keyword_counts.items(), key=lambda item: item[1], reverse=True)}
sorted_estado_counts = {k: v for k, v in sorted(
    estado_counts.items(), key=lambda item: item[1], reverse=True)}

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.bar(sorted_keyword_counts.keys(),
        sorted_keyword_counts.values(), color='blue', alpha=0.7)
plt.xlabel('Palavras-Chave')
plt.ylabel('Frequência')
plt.title(
    'Frequência de Menções as Palavras-Chave com Limiar de Toxicidade Superior a 80%')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.subplot(1, 2, 2)
plt.bar(sorted_estado_counts.keys(),
        sorted_estado_counts.values(), color='green', alpha=0.7)
plt.xlabel('Estados')
plt.ylabel('Frequência')
plt.title('Frequência de Menções aos Estados Brasileiros com Limiar de Toxicidade Superior a 80%')
plt.xticks(rotation=90)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()


# COMO URLS FORAM CLASSIFICADAS ENTRE CERTIFICADAS E NÃO CERTIFICADAS
def get_trusted_domains():
    trusted_domains = [
        'acidadeon',
        'acordacidade',
        'agorarn',
        'an.com',
        'atarde',
        'atribuna',
        'bnews',
        'bopaper',
        'boqnews',
        'correio24horas',
        'correiodecarajas',
        'correiodeitapetininga',
        'correiodopovo',
        'costanorte',
        'diarinho',
        'diariocatarinense',
        'diariocomercial',
        'diariodaregiao',
        'diariodoacionista',
        'diariodoamazonas',
        'diariodocomercio',
        'diariodolitoral',
        'diariodonordeste',
        'diariodopara',
        'diariodorio',
        'diariopopular',
        'emdiaes',
        'entreriosjornal',
        'es360',
        'eshoje',
        'estadao',
        'extra',
        'folha',
        'folha1',
        'folhabv',
        'folhadelondrina',
        'folhape',
        'folhavitoria',
        'g1',
        'gauchazh',
        'gaz.com',
        'gazetadelimeira',
        'gazetadigital',
        'gazetadopovo',
        'gazetaonline',
        'gazetasp',
        'hojeemdia',
        'ilustrado',
        'jblitoral',
        'jc.com',
        'jcam',
        'jcnet',
        'jornalcidade',
        'jornalcidade',
        'jornalcruzeiro',
        'jornaldebrasilia',
        'jornaldezminutos',
        'jornaldocomercio',
        'jornaldopovo',
        'jornaldotocantins',
        'jornaldr1',
        'jornalnh',
        'jornalopoder',
        'lance.com',
        'oliberal',
        'meionorte',
        'moneytimes',
        'monitormercantil',
        'ndonline',
        'nfnoticias',
        'oestadoonline',
        'oglobo',
        'globo',
        'opopular',
        'opovo',
        'orm.com',
        'otempo',
        'pioneiro.clicrbs/rs',
        'portalarauto',
        'portalcorreio',
        'propmark',
        'rac.com',
        'romanews',
        'santa.com',
        'seucreditodigital',
        'seudinheiro',
        'tnonline',
        'todahora.com',
        'tribunadosertao',
        'tribunahoje',
        'tribunaonline',
        'tribunapr',
        'uol',
        'valor.globo',
        'vozdosmunicipios',
        'zmnoticias',
        'cnn',
        'time.com',
        'bbc.com',
        'reuters',
        'intercept'
        'cnnbrasil',
        'cnnportugal.iol'

    ]
    return trusted_domains


def get_news_domains():
    news_domains = ["globo",
                    "uol",
                    "estadao",
                    "gazetadopovo",
                    "otempo",
                    "jornaldebrasilia",
                    "folha",
                    "opovo",
                    "correiodopovo",
                    "brasil247",
                    "terrabrasilnoticias",
                    "revistaoeste",
                    "abril",
                    "diariodocentrodomundo",
                    "jornaldacidadeonline",
                    "metropoles",
                    "correiobraziliense",
                    "r7",
                    "intercept",
                    "cnnbrasil",
                    "brasilsemmedo",
                    "gazetabrasil",
                    "revistaforum",
                    "jovempan",
                    "clicrbs",
                    "dunapress",
                    "yahoo",
                    "reuters",
                    "terra",
                    "atrombetanews",
                    "cartacapital",
                    "poder360",
                    "apublica",
                    "agoranoticiasbrasil",
                    "msn",
                    "exame",
                    "contrafatos",
                    "pleno",
                    "portaltocanews",
                    "caldeiraopolitico",
                    "tvi.iol",
                    "brasildefato",
                    "aliadosbrasiloficial",
                    "sbtnews",
                    "wordpress",
                    "apostagem",
                    "istoe",
                    "dw.com",
                    "conexaopolitica"
                    "vistapatria",
                    "noticiasaominuto",
                    "jornalggn",
                    "redebrasilatual",
                    "nsctotal",
                    "sputniknewsbrasil",
                    "horabrasilia",
                    "plantaobrasil",
                    "saibamais",
                    "diariodopoder",
                    "antenapoliticabr",
                    "sapo",
                    "conjur",
                    "change",
                    "aosfatos",
                    "ebc",
                    "expresso",
                    "folhadestra",
                    "atarde"
                    "bbc.com"
                    ]
    return news_domains


def not_certified_news():
    uncertified = ['jornaldacidadeonline',
                   'folhadestra',
                   'revistaoeste',
                   'pleno',
                   'sapo',
                   'expresso',
                   'change',
                   'diariodocentrodomundo',
                   'sputniknewsbrasil',
                   'dw.com',
                   'caldeiraopolitico',
                   'apostagem',
                   'saibamais',
                   'horabrasilia',
                   'nsctotal',
                   'diariodopoder',
                   'aliadosbrasiloficial',
                   'contrafatos',
                   'r7',
                   'sbtnews',
                   'terra',
                   'noticiasaominuto',
                   'apublica',
                   'istoe',
                   'plantaobrasil',
                   'redebrasilatual',
                   'cartacapital',
                   'conjur',
                   'clicrbs',
                   'revistaforum',
                   'metropoles',
                   'antenapoliticabr',
                   'portaltocanews',
                   'yahoo',
                   'atrombetanews',
                   'brasilsemmedo',
                   'jornalggn',
                   'tvi.iol',
                   'brasil247',
                   'msn',
                   'terrabrasilnoticias',
                   'agoranoticiasbrasil',
                   'conexaopoliticavistapatria',
                   'dunapress',
                   'exame',
                   'atardeacidadeon',
                   'correiobraziliense',
                   'jovempan',
                   'poder360',
                   'abril',
                   'ebc',
                   'wordpress',
                   'gazetabrasil',
                   'brasildefato',
                   'aosfatos'
                   ]
    return uncertified


def classify_url(url):
    anj_domains = get_trusted_domains()
    uncertified_news = not_certified_news()

    if isinstance(url, str):
        cleaned_url = url.strip("[]'").replace('"', '')
        if cleaned_url:
            extracted_domain = tldextract.extract(cleaned_url)
            domain = extracted_domain.domain.lower()
            if any(domain in anj_domain for anj_domain in anj_domains):
                return 'Certified'
            elif any(domain in uncertified_domains for uncertified_domains in uncertified_news):
                return 'Uncertified'
        return
    return


df = pd.read_csv('main-file.csv')
df['class'] = df['urls'].apply(lambda x: classify_url(x))
df.to_csv('df_classificado.csv', index=False, encoding='utf-8')


# COMO FOI FEITO PLOT EM BARRA DO INDICE DE SENTIMENTO COMPOUND

def extract_sentiment_attributes(sentiment_score, attribute):
    sentiment_dict = eval(sentiment_score)
    x = sentiment_dict.get(attribute, -2.0)
    return x


scrap_classified_sentiment = pd.read_csv(
    'scrap_classified_sentiment.csv', sep='|', encoding='utf-8')
scrap_unclassified_sentiment = pd.read_csv(
    'scrap_unclassified_sentiment.csv',  sep='|', encoding='utf-8')
# scrap_classified_sentiment = pd.read_csv('teste.csv',  sep='|', encoding='utf-8')
# scrap_unclassified_sentiment = pd.read_csv('teste2.csv',  sep='|', encoding='utf-8')


# filtragem de toxicidade se necessária
# idattack_val = scrap_classified_sentiment['perspective'].apply(lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
# threat_val = scrap_classified_sentiment['perspective'].apply(lambda x: extract_attribute(x, 'THREAT'))
# idattack_val2 = scrap_unclassified_sentiment['perspective'].apply(lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
# threat_val2 = scrap_unclassified_sentiment['perspective'].apply(lambda x: extract_attribute(x, 'THREAT'))

# # filtragem por media de atributos
# scrap_classified_sentiment['media'] = (idattack_val + threat_val) / 2
# scrap_unclassified_sentiment['media'] = (idattack_val2 + threat_val2) / 2


# scrap_classified_sentiment = scrap_classified_sentiment[scrap_classified_sentiment['media'] > 0.8]
# scrap_unclassified_sentiment = scrap_unclassified_sentiment[scrap_unclassified_sentiment['media'] > 0.8]


scrap_unclassified_sentiment['compound'] = scrap_unclassified_sentiment['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_unclassified_sentiment_neg = scrap_unclassified_sentiment[
    scrap_unclassified_sentiment['compound'] < -0.05]
scrap_unclassified_sentiment_pos = scrap_unclassified_sentiment[
    scrap_unclassified_sentiment['compound'] > 0.05]
scrap_unclassified_sentiment_neu = scrap_unclassified_sentiment[(
    scrap_unclassified_sentiment['compound'] >= -0.05) & (scrap_unclassified_sentiment['compound'] <= 0.05)]

scrap_classified_sentiment['compound'] = scrap_classified_sentiment['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_classified_sentiment_neg = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] < -0.05]
scrap_classified_sentiment_pos = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] > 0.05]
scrap_classified_sentiment_neu = scrap_classified_sentiment[(
    scrap_classified_sentiment['compound'] >= -0.05) & (scrap_classified_sentiment['compound'] <= 0.05)]


rotulos = ['Certificadas', 'Não Certificadas']
categoria = ['Neg', 'Neu', 'Pos']
largura_barra = 0.3

posicoes = np.arange(len(rotulos))

pos_neg = posicoes - largura_barra
pos_neu = posicoes
pos_pos = posicoes + largura_barra

len_class_pos = len(scrap_classified_sentiment_pos)
len_class_neu = len(scrap_classified_sentiment_neu)
len_class_neg = len(scrap_classified_sentiment_neg)

len_unc_pos = len(scrap_unclassified_sentiment_pos)
len_unc_neu = len(scrap_unclassified_sentiment_neu)
len_unc_neg = len(scrap_unclassified_sentiment_neg)

neg_values = [len_class_neg, len_unc_neg]
neu_values = [len_class_neu, len_unc_neu]
pos_values = [len_class_pos, len_unc_pos]

plt.figure(figsize=(4, 3))

plt.bar(pos_neg, neg_values, largura_barra, color='#FF6603', label='Neg')
plt.bar(pos_neu, neu_values, largura_barra, color='#454545', label='Neu')
plt.bar(pos_pos, pos_values, largura_barra, color='b', label='Pos')


plt.xlabel('Classificação')
plt.ylabel('# Compound')
plt.xticks(posicoes, rotulos)
plt.legend()
plt.grid(True)
plt.show()


# COMO FOI FEITO CDF DO COMPOUND

scrap_classified_sentiment = pd.read_csv(
    'scrap_classified_sentiment.csv', sep='|', encoding='utf-8')
scrap_unclassified_sentiment = pd.read_csv(
    'scrap_unclassified_sentiment.csv',  sep='|', encoding='utf-8')
# df = pd.read_csv('./Dados/Scrap-Result/scrap_sentiment_score.csv', sep='|', encoding='utf-8')
# scrap_classified_sentiment = pd.read_csv('teste.csv', sep='|', encoding='utf-8')
# scrap_unclassified_sentiment = pd.read_csv('teste2.csv', sep='|', encoding='utf-8')

# dataframes filtrados
idattack_val = scrap_classified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = scrap_classified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val2 = scrap_unclassified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val2 = scrap_unclassified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# filtragem por media de atributos
scrap_classified_sentiment['media'] = (idattack_val + threat_val) / 2
scrap_unclassified_sentiment['media'] = (idattack_val2 + threat_val2) / 2

scrap_classified_sentiment_filtrado = scrap_classified_sentiment[
    scrap_classified_sentiment['media'] > 0.8]
scrap_unclassified_sentiment_filtrado = scrap_unclassified_sentiment[
    scrap_unclassified_sentiment['media'] > 0.8]

print("N Certificadas - ", len(scrap_unclassified_sentiment))
print("N Certificadas Filtrada - ", len(scrap_unclassified_sentiment_filtrado))
print("Certificadas - ", len(scrap_classified_sentiment))
print("Certificadas Filtrada - ", len(scrap_classified_sentiment_filtrado))

# definindo tamanho de figura
plt.figure(figsize=(4, 3))

# nao certificadas com filtro / plotagem
scrap_unclassified_sentiment_filtrado['compound'] = scrap_unclassified_sentiment_filtrado['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_unclassified_sentiment_filtrado = scrap_unclassified_sentiment_filtrado['compound'].sort_values(
)
cdf_nc80 = np.arange(1, len(scrap_unclassified_sentiment_filtrado) +
                     1) / len(scrap_unclassified_sentiment_filtrado)
plt.plot(scrap_unclassified_sentiment_filtrado, cdf_nc80,
         label='> 0.8', color='#FF6603', linestyle='dashed')

# nao certificadas sem filtro / plotagem
scrap_unclassified_sentiment['compound'] = scrap_unclassified_sentiment['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_unclassified_sentiment = scrap_unclassified_sentiment['compound'].sort_values(
)
cdf_nc = np.arange(1, len(scrap_unclassified_sentiment) +
                   1) / len(scrap_unclassified_sentiment)
plt.plot(scrap_unclassified_sentiment, cdf_nc,
         label='Não Certificadas', color='#FF6603')

# certificadas com filtro / plotagem
scrap_classified_sentiment_filtrado['compound'] = scrap_classified_sentiment_filtrado['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment_filtrado = scrap_classified_sentiment_filtrado['compound'].sort_values(
)
cdf_c80 = np.arange(1, len(scrap_classified_sentiment_filtrado) +
                    1) / len(scrap_classified_sentiment_filtrado)
plt.plot(scrap_classified_sentiment_filtrado, cdf_c80,
         label='> 0.8', color='b', linestyle='dashed')

# certificadas sem filtro
scrap_classified_sentiment['compound'] = scrap_classified_sentiment['sentiment_score'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment = scrap_classified_sentiment['compound'].sort_values(
)
cdf = np.arange(1, len(scrap_classified_sentiment) + 1) / \
    len(scrap_classified_sentiment)
plt.plot(scrap_classified_sentiment, cdf, label='Certificadas', color='b')

# parametros de plot adicionais
plt.xlabel('# Compound')
plt.ylabel('CDF')
plt.grid(True)
plt.legend(fontsize=7)
plt.show()


# COMO FOI FEITO PLOT CDF DE ATRIBUTOS SENTIMENT SEPARADAMENTE:

scrap_classified_sentiment = pd.read_csv(
    'scrap_classified_sentiment.csv', sep='|', encoding='utf-8')
scrap_unclassified_sentiment = pd.read_csv(
    'scrap_unclassified_sentiment.csv',  sep='|', encoding='utf-8')
# df = pd.read_csv('./Dados/Scrap-Result/scrap_sentiment_score.csv', sep='|', encoding='utf-8')
# scrap_classified_sentiment = pd.read_csv('teste.csv', sep='|', encoding='utf-8')
# scrap_unclassified_sentiment = pd.read_csv('teste2.csv', sep='|', encoding='utf-8')

# dataframes filtrados
idattack_val = scrap_classified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = scrap_classified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val2 = scrap_unclassified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val2 = scrap_unclassified_sentiment['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# filtragem por media de atributos
scrap_classified_sentiment['media'] = (idattack_val + threat_val) / 2
scrap_unclassified_sentiment['media'] = (idattack_val2 + threat_val2) / 2

scrap_classified_sentiment_filtrado = scrap_classified_sentiment[
    scrap_classified_sentiment['media'] > 0.8]
scrap_unclassified_sentiment_filtrado = scrap_unclassified_sentiment[
    scrap_unclassified_sentiment['media'] > 0.8]

legend_labels_certified = ['Certificadas - Neg',
                           'Certificadas - Neu', 'Certificadas - Pos']
legend_labels_unclassified = ['Não Certificadas - Neg',
                              'Não Certificadas - Neu', 'Não Certificadas - Pos']
attributes = ['neg', 'neu', 'pos']
colors = ['#FF6603', '#454545', 'b']
line_styles = ['-', '--']

plt.figure(figsize=(4, 3))

# Plotagem das distribuições
for i, attribute in enumerate(attributes):
    df_sorted = scrap_classified_sentiment['sentiment_score'].apply(
        extract_sentiment_attributes, attribute=attribute).sort_values()
    cdf = np.arange(1, len(df_sorted) + 1) / len(df_sorted)
    plt.plot(df_sorted, cdf, label=legend_labels_certified[i], color=colors[i])

for i, attribute in enumerate(attributes):
    df_sorted_unc = scrap_unclassified_sentiment['sentiment_score'].apply(
        extract_sentiment_attributes, attribute=attribute).sort_values()
    cdf_unc = np.arange(1, len(df_sorted_unc) + 1) / len(df_sorted_unc)
    plt.plot(df_sorted_unc, cdf_unc,
             label=legend_labels_unclassified[i], color=colors[i], linestyle='dashdot')

# Plotagem das distribuições com filtro de 0.8
for i, attribute in enumerate(attributes):
    df_sorted_filtrado = scrap_classified_sentiment_filtrado['sentiment_score'].apply(
        extract_sentiment_attributes, attribute=attribute).sort_values()
    cdf_filtrado = np.arange(
        1, len(df_sorted_filtrado) + 1) / len(df_sorted_filtrado)
    plt.plot(df_sorted_filtrado, cdf_filtrado,
             label=legend_labels_certified[i] + "> 0.8", color=colors[i], linestyle='dashed')


for i, attribute in enumerate(attributes):
    df_sorted_unc_filtrado = scrap_unclassified_sentiment_filtrado['sentiment_score'].apply(
        extract_sentiment_attributes, attribute=attribute).sort_values()
    cdf_unc_filtrado = np.arange(
        1, len(df_sorted_unc_filtrado) + 1) / len(df_sorted_unc_filtrado)
    plt.plot(df_sorted_unc_filtrado, cdf_unc_filtrado,
             label=legend_labels_unclassified[i] + " > 0.8", color=colors[i], linestyle='dotted')

plt.xlabel("Atributo")
plt.ylabel("CDF")
plt.grid(True)
plt.legend(fontsize=8)
plt.show()

# COMO TITULO FOI COLETADO DO SCRAP


def extrair_titulos(input_string):
    if not input_string or str(input_string) == 'nan':
        return []

    regex_pattern = r'"Título": \["(.*?)"\]'
    input_string = input_string.replace("'", '"')

    # Encontrar todas as correspondências na string
    matches = re.findall(regex_pattern, input_string)

    # Retorna a lista de títulos extraídos
    return matches


df = pd.read_csv('df.csv')

df['titulo'] = df['scrap'].apply(lambda x: extrair_titulos(x))

df.to_csv('nome_qualquer.csv', index=False)


# COMO PERSPECTIVE FOI ATRIBUIDA AO TITULO
def analyze_comment(comment_text):
    api_key = 'AIzaSyB65GkrlS0s2Rc04lCZ0vuURiYfuWgZWfQ'
    time.sleep(1)
    print(comment_text)
    url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={api_key}'

    data = {
        'comment': {
            'text': comment_text
        },
        'requestedAttributes': {
            'TOXICITY': {},
            'SEVERE_TOXICITY': {},
            'PROFANITY': {},
            'INSULT': {},
            'THREAT': {},
            'IDENTITY_ATTACK': {}
        }
    }
    try:
        response = requests.post(url, data=json.dumps(data))
        response_json = response.json()
        if response.status_code == 429:
            time.sleep(60)
            print("Requests per minute exceeded")
        return response_json
    except:
        print(f"A requisição falhou.")
        return 1.0


df = pd.read_csv('uncertified-w-title.csv', chunksize=700)
i = 1
for chunk in df:
    file = open('control2')
    flag = int(file.read())
    if i > flag:
        chunk['perspective_title'] = chunk['titulos'].apply(
            lambda x: analyze_comment(x))
        chunk.to_csv('uncertified-perspective.csv', mode='a',
                     index=False, encoding='utf-8')
        file = open("control2", 'w')
        file.write(str(i))
        file.close()
        print(f"Chunk {i} salvo com sucesso.")
    i += 1

print(f"Chunks salvos.")


# COMO BARPLOT DO SENTIMNETO FOI FEITO

df_certified = pd.read_csv('df_certified.csv')
df_uncertified = pd.read_csv('df_uncertified.csv')
df_others = pd.read_csv('df_others.csv')
# filtragem de toxicidade se necessária
idattack_val = df_certified['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = df_certified['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val2 = df_uncertified['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val2 = df_uncertified['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# filtragem por media de atributos
df_certified['media'] = (idattack_val + threat_val) / 2
df_uncertified['media'] = (idattack_val2 + threat_val2) / 2
df_others['media'] = (idattack_val3 + threat_val3) / 2


# df_certified = df_certified[df_certified['media'] > 0.8]
# df_uncertified = df_uncertified[
#     df_uncertified['media'] > 0.8]
# df_others = df_others[df_others['media'] > 0.8]


df_uncertified['compound'] = df_uncertified['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_unclassified_sentiment_neg = df_uncertified[
    df_uncertified['compound'] < -0.05]
scrap_unclassified_sentiment_pos = df_uncertified[
    df_uncertified['compound'] > 0.05]
scrap_unclassified_sentiment_neu = df_uncertified[(
    df_uncertified['compound'] >= -0.05) & (df_uncertified['compound'] <= 0.05)]

df_certified['compound'] = df_certified['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_classified_sentiment_neg = df_certified[
    df_certified['compound'] < -0.05]
scrap_classified_sentiment_pos = df_certified[
    df_certified['compound'] > 0.05]
scrap_classified_sentiment_neu = df_certified[(
    df_certified['compound'] >= -0.05) & (df_certified['compound'] <= 0.05)]

df_others['compound'] = df_others['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_others_sentiment_neg = df_others[
    df_others['compound'] < -0.05]
scrap_others_sentiment_pos = df_others[
    df_others['compound'] > 0.05]
scrap_others_sentiment_neu = df_others[(
    df_others['compound'] >= -0.05) & (df_others['compound'] <= 0.05)]


rotulos = ['Certificadas', 'Não Certificadas', 'Outras']
categoria = ['Neg.', 'Neu.', 'Pos.']
largura_barra = 0.3

posicoes = np.arange(len(rotulos))

pos_neg = posicoes - largura_barra
pos_neu = posicoes
pos_pos = posicoes + largura_barra

len_class_pos = len(scrap_classified_sentiment_pos)
len_class_neu = len(scrap_classified_sentiment_neu)
len_class_neg = len(scrap_classified_sentiment_neg)

total_class = (len_class_neg + len_class_neu + len_class_pos)

len_unc_pos = len(scrap_unclassified_sentiment_pos)
len_unc_neu = len(scrap_unclassified_sentiment_neu)
len_unc_neg = len(scrap_unclassified_sentiment_neg)

total_unc = (len_unc_neg + len_unc_neu + len_unc_pos)

len_others_pos = len(scrap_others_sentiment_pos)
len_others_neu = len(scrap_others_sentiment_neu)
len_others_neg = len(scrap_others_sentiment_neg)

total_others = (len_others_neg + len_others_neu + len_others_pos)

neg_values = [(len_class_neg / total_class), (len_unc_neg /
                                              total_unc), (len_others_neg / total_others)]
neu_values = [(len_class_neu / total_class), (len_unc_neu /
                                              total_unc), (len_others_neu / total_others)]
pos_values = [(len_class_pos / total_class), (len_unc_pos /
                                              total_unc), (len_others_pos / total_others)]


plt.figure(figsize=(4, 3))

plt.bar(pos_neg, neg_values, largura_barra, color='r', label='Neg.')
plt.bar(pos_neu, neu_values, largura_barra, color='#ffff00', label='Neu.')
plt.bar(pos_pos, pos_values, largura_barra, color='g', label='Pos.')


plt.ylabel('# Frac. Tweets')
plt.xticks(posicoes, rotulos)
plt.legend(fontsize=8)
plt.grid(True)
plt.show()

plt.show()


# COMO ATRIBUTOS DE ENGAJAMENTO FORAM CALCULADOS:

def classify_all_urls(url):
    anj_domains = get_trusted_domains()
    uncertified_news = not_certified_news()

    if isinstance(url, str):
        cleaned_url = url.strip("[]'").replace('"', '')
        if cleaned_url:
            extracted_domain = tldextract.extract(cleaned_url)
            domain = extracted_domain.domain.lower()
            if any(domain in anj_domain for anj_domain in anj_domains):
                return 'Certified'
            elif any(domain in uncertified_domains for uncertified_domains in uncertified_news):
                return 'Uncertified'
        return 'Others'
    return 'Others'


df = pd.read_csv('main-file-scrap.csv')
df['Class'] = df['urls'].apply(lambda x: classify_all_urls(x))
df_certified = df[df['Class'] == 'Certified']
df_uncertified = df[df['Class'] == 'Uncertified']
df_others = df[df['Class'] == 'Others']

# df = pd.read_csv('df_certified.csv')
# df = pd.read_csv('df_uncertified.csv')
# df_others = pd.read_csv('df_others.csv')

attributes = ['THREAT', 'TOXICITY', 'SEVERE_TOXICITY',
              'PROFANITY', 'INSULT', 'IDENTITY_ATTACK']

attribute_colors = {
    'THREAT': '#5898c5',
    'TOXICITY': '#a179c5',
    'SEVERE_TOXICITY': '#d93435',
    'IDENTITY_ATTACK': '#fc8419',
    'INSULT': '#52b152',
    'PROFANITY': '#a57b72'
}

plt.figure(figsize=(4, 3))

for attribute in attributes:
    df[attribute] = df['perspective'].apply(
        lambda x: extract_attribute(x, attribute))
    df_filtered = df.dropna(subset=[attribute])
    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)
    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    # Use o dicionário de cores para obter a cor associada ao atributo
    color = attribute_colors.get(attribute, 'black')

    plt.plot(sorted(values), cumulative_values, label=attribute, color=color)

plt.xlabel('Atributo')
plt.ylabel('CDF')
plt.legend(fontsize=6)
# plt.grid()
plt.show()


# COMO SENTIMENTO FOI COMPUTADO
# from leia import SentimentIntensityAnalyzer

s = SentimentIntensityAnalyzer()


df_cert = pd.read_csv('./LeIA/certified-perspective.csv')
df_uncert = pd.read_csv('./LeIA/uncertified-perspective.csv')


df_cert['sentiment_headline'] = df_cert['titulos'].apply(
    lambda x: s.polarity_scores(x))

df_uncert['sentiment_headline'] = df_uncert['titulos'].apply(
    lambda x: s.polarity_scores(x))

df_cert.to_csv('df_certified_completo.csv', index=False)
df_uncert.to_csv('df_uncertified_completo.csv', index=False)


# COMO BARPLOT DO SENTIMENTO FOI RELACIONADO COM O SENTIMENTO DAS HEADLINES


scrap_classified_sentiment = pd.read_csv('df_certified_completo.csv')
# scrap_classified_sentiment = pd.read_csv('df_uncertified_completo.csv')
# scrap_classified_sentiment = pd.read_csv('teste.csv')
# scrap_unclassified_sentiment = pd.read_csv('df_uncertified_completo.csv')


total_neg = len(scrap_classified_sentiment)
total_neu = len(scrap_classified_sentiment)
total_pos = len(scrap_classified_sentiment)
scrap_classified_sentiment['compound'] = scrap_classified_sentiment['sentiment_headline'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))


scrap_classified_sentiment_neg = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] < -0.05]
scrap_classified_sentiment_pos = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] > 0.05]
scrap_classified_sentiment_neu = scrap_classified_sentiment[(
    scrap_classified_sentiment['compound'] >= -0.05) & (scrap_classified_sentiment['compound'] <= 0.05)]

scrap_classified_sentiment_neg['compound_text'] = scrap_classified_sentiment_neg['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment_neu['compound_text'] = scrap_classified_sentiment_neu['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment_pos['compound_text'] = scrap_classified_sentiment_pos['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

qtd_sentiment_neg_neg = len(scrap_classified_sentiment_neg[
    scrap_classified_sentiment_neg['compound_text'] < -0.05])
qtd_sentiment_neu_neg = len(
    scrap_classified_sentiment_neg[(scrap_classified_sentiment_neg['compound_text'] >= -0.05) & (scrap_classified_sentiment_neg['compound_text'] <= 0.05)])
qtd_sentiment_pos_neg = len(scrap_classified_sentiment_neg[
    scrap_classified_sentiment_neg['compound_text'] > 0.05])

qtd_sentiment_neu_neu = len(
    scrap_classified_sentiment_neu[(scrap_classified_sentiment_neu['compound_text'] >= -0.05) & (scrap_classified_sentiment_neu['compound_text'] <= 0.05)])
qtd_sentiment_neg_neu = len(scrap_classified_sentiment_neu[
    scrap_classified_sentiment_neu['compound_text'] < -0.05])
qtd_sentiment_pos_neu = len(scrap_classified_sentiment_neu[
    scrap_classified_sentiment_neu['compound_text'] > 0.05])

qtd_sentiment_neu_pos = len(
    scrap_classified_sentiment_pos[(scrap_classified_sentiment_pos['compound_text'] >= -0.05) & (scrap_classified_sentiment_pos['compound_text'] <= 0.05)])
qtd_sentiment_neg_pos = len(scrap_classified_sentiment_pos[
    scrap_classified_sentiment_pos['compound_text'] < -0.05])
qtd_sentiment_pos_pos = len(scrap_classified_sentiment_pos[
    scrap_classified_sentiment_pos['compound_text'] > 0.05])

# total_neg = qtd_sentiment_neg_neg + qtd_sentiment_neu_neg + qtd_sentiment_pos_neg
# total_neu = qtd_sentiment_neg_neu + qtd_sentiment_neu_neu + qtd_sentiment_pos_neu
# total_pos = qtd_sentiment_neg_pos + qtd_sentiment_neu_pos + qtd_sentiment_pos_pos

# rotulos = ['Certificadas', 'Não Certificadas']
rotulos = ['Neg.', 'Neu.', 'Pos.']
largura_barra = 0.3

posicoes = np.arange(len(rotulos))

pos_neg = posicoes - largura_barra
pos_neu = posicoes
pos_pos = posicoes + largura_barra

neg_values = [(qtd_sentiment_neg_neg / total_neg),
              (qtd_sentiment_neu_neg / total_neg), (qtd_sentiment_pos_neg / total_neg)]


neu_values = [(qtd_sentiment_neg_neu / total_neu),
              (qtd_sentiment_neu_neu / total_neu), (qtd_sentiment_pos_neu / total_neu)]


pos_values = [(qtd_sentiment_neg_pos / total_pos),
              (qtd_sentiment_neu_pos / total_pos), (qtd_sentiment_pos_pos / total_pos)]


plt.figure(figsize=(4, 3))

plt.bar(pos_neg, neg_values, largura_barra, color='r', label='Neg.')
plt.bar(pos_neu, neu_values, largura_barra, color='#ffff00', label='Neu.')
plt.bar(pos_pos, pos_values, largura_barra, color='g', label='Pos.')


plt.ylabel('Prob.')
plt.xticks(posicoes, rotulos)
title = plt.title('Certificadas')
title.set_position([.5, 0.02])
plt.legend(fontsize=8)
plt.grid(True)
plt.show()


# COMO CDFS DE ENGAJAMENTO FORAM PLOTADAS COM ADIÇÃO DOS OUTROS


df_confiaveis = pd.read_csv("df_certified.csv", encoding='utf-8')
df_nao_confiaveis = pd.read_csv("df_uncertified.csv", encoding='utf-8')
df_others = pd.read_csv("df_others.csv", encoding='utf-8')


idattack_val = df_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
idattack_val2 = df_nao_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = df_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
threat_val2 = df_nao_confiaveis['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# filtragem por media de atributos
df_confiaveis['media'] = (idattack_val + threat_val) / 2
df_nao_confiaveis['media'] = (idattack_val2 + threat_val2) / 2
df_others['media'] = (idattack_val3 + threat_val3) / 2


df_confiaveis_filtrado = df_confiaveis[df_confiaveis['media'] > 0.8]
df_nao_confiaveis_filtrado = df_nao_confiaveis[df_nao_confiaveis['media'] > 0.8]
df_others_filtrado = df_others[df_others['media'] > 0.8]
atributo = 'public_metrics.quote_count'

cores = ['b', '#fc6603', '#2b3437']

# confiaveis
df_confiaveis = df_confiaveis[df_confiaveis[atributo] > 0]
sorted_confiaveis = df_confiaveis[atributo].sort_values()
sorted_confiaveis_filtrado = df_confiaveis_filtrado[atributo].sort_values()

# nao confiaveis
df_nao_confiaveis = df_nao_confiaveis[df_nao_confiaveis[atributo] > 0]
sorted_nao_confiaveis_filtrado = df_nao_confiaveis_filtrado[atributo].sort_values(
)
sorted_nao_confiaveis = df_nao_confiaveis[atributo].sort_values()

# outros
df_others = df_others[df_others[atributo] > 0]
df_other_filtrado = df_others_filtrado[atributo].sort_values()
sorted_others = df_others[atributo].sort_values()

n_confiaveis = len(sorted_confiaveis)
n_confiaveis_filtrado = len(sorted_confiaveis_filtrado)
n_nao_confiaveis = len(sorted_nao_confiaveis)
n_nao_confiaveis_filtrado = len(sorted_nao_confiaveis_filtrado)
others = len(sorted_others)
others_filtrado = len(df_others_filtrado)

# confiaveis
cdf_confiaveis = np.arange(1, n_confiaveis + 1) / n_confiaveis
cdf_confiaveis_filtrado = np.arange(
    1, n_confiaveis_filtrado + 1) / n_confiaveis_filtrado

# nao confiaveis
cdf_nao_confiaveis = np.arange(1, n_nao_confiaveis + 1) / n_nao_confiaveis
cdf_nao_confiaveis_filtrado = np.arange(
    1, n_nao_confiaveis_filtrado + 1) / n_nao_confiaveis_filtrado

# outros
cdf_outros = np.arange(1, others + 1) / others
cdf_outros_filtrado = np.arange(1, others_filtrado + 1) / others_filtrado

plt.figure(figsize=(4, 3))
plt.semilogx(sorted_confiaveis, cdf_confiaveis,
             label='Certificada', color=cores[0])
plt.semilogx(sorted_confiaveis_filtrado, cdf_confiaveis_filtrado,
             label='> 0.8', linestyle='dashed', color=cores[0])
plt.semilogx(sorted_nao_confiaveis, cdf_nao_confiaveis,
             label='Não Certificada', color=cores[1])
plt.semilogx(sorted_nao_confiaveis_filtrado, cdf_nao_confiaveis_filtrado,
             linestyle='dashed', label='> 0.8', color=cores[1])

plt.semilogx(sorted_others, cdf_outros, label='Outros', color=cores[2])
plt.semilogx(df_other_filtrado, cdf_outros_filtrado,
             label='> 0.8', color=cores[2], linestyle='dashed')

plt.xlabel("# Quotes")
plt.ylabel("CDF")
plt.grid(True)
plt.legend(fontsize=7)
plt.show()


# COMO CDF DOS ATRIBUTOS DE TOXICIDADE (MEDIA ENTRE ID_ATTACK E THREAT) FORAM CALCULADOS COM ADIÇÃO DOS OUTROS


df_confiaveis = pd.read_csv("df_certified.csv", encoding='utf-8')
df_nao_confiaveis = pd.read_csv("df_uncertified.csv", encoding='utf-8')
df_others = pd.read_csv("df_others.csv", encoding='utf-8')


df_confiaveis['perspective'] = df_confiaveis['perspective'].astype(str)
df_nao_confiaveis['perspective'] = df_nao_confiaveis['perspective'].astype(str)
df_others['perspective'] = df_others['perspective'].astype(str)

attributes = ['THREAT', 'IDENTITY_ATTACK']

plt.figure(figsize=(4, 3))

colors_certificadas = {'THREAT': 'b', 'IDENTITY_ATTACK': '#FF6603'}

for attribute in attributes:
    df_confiaveis[attribute] = df_confiaveis['perspective'].apply(
        lambda x: extract_attribute(x, attribute))

    df_filtered = df_confiaveis.dropna(subset=[attribute])

    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)

    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    plt.plot(sorted(values), cumulative_values,
             label=f'Certificadas - {attribute}', color=colors_certificadas[attribute])

colors_nao_certificadas = {'THREAT': 'b', 'IDENTITY_ATTACK': '#FF6603'}

for attribute in attributes:
    df_nao_confiaveis[attribute] = df_nao_confiaveis['perspective'].apply(
        lambda x: extract_attribute(x, attribute))

    df_filtered = df_nao_confiaveis.dropna(subset=[attribute])

    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)

    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    plt.plot(sorted(values), cumulative_values,
             label=f'Não Certificadas - {attribute}', linestyle='dashed', color=colors_nao_certificadas[attribute])


for attribute in attributes:
    df_others[attribute] = df_others['perspective'].apply(
        lambda x: extract_attribute(x, attribute))

    df_filtered = df_others.dropna(subset=[attribute])

    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)

    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    plt.plot(sorted(values), cumulative_values,
             label=f'Outros - {attribute}', linestyle='dotted', color=colors_nao_certificadas[attribute])

plt.xlabel(f'Atributo')
plt.ylabel('CDF')
plt.legend(fontsize=6)
plt.grid()
plt.show()


# COMO CONTAGEM DOS ATRIBUTOS DE ENGAJAMENTO FOI FEITA
df_cert = pd.read_csv('df_certified.csv')
df_uncert = pd.read_csv('df_uncertified.csv')
df_others = pd.read_csv('df_others.csv')

df_others = df_others[(df_others['public_metrics.impression_count'] == 0)]
df_cert = df_cert[(df_cert['public_metrics.impression_count'] == 0)]
df_uncert = df_uncert[(df_uncert['public_metrics.impression_count'] == 0)]
# df_uncert = df_uncert[(df_uncert['public_metrics.impression_count'] > 0) & (
#     df_uncert['public_metrics.like_count'] > 0)]
# df_others = df_others[(df_others['public_metrics.impression_count'] > 0) & (
#     df_others['public_metrics.like_count'] > 0)]

# print(df_cert['text'], df_cert['public_metrics.like_count'])
# print(df_uncert['text'], df_uncert['public_metrics.like_count'])
# print(df_others['text'], df_others['public_metrics.like_count'])

# print(len(df_cert[df_cert['public_metrics.like_count'] > 0]), (len(
#     df_cert[df_cert['public_metrics.like_count'] > 0])/len(df_cert)))
# print(len(df_uncert[df_uncert['public_metrics.like_count'] > 0]), (len(
#     df_uncert[df_uncert['public_metrics.like_count'] > 0])/len(df_uncert)))
# print(len(df_others[df_others['public_metrics.like_count'] > 0]), (len(
#     df_others[df_others['public_metrics.like_count'] > 0])/len(df_others)))

print('Certificadas: ', len(df_cert), 'N Certificadas: ',
      len(df_uncert), 'Outras: ', len(df_others))


##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
# plot rebuttal (GUARDA DIREITO CARAI)

# barplot condicional certificado e nao certificado
# df = pd.read_csv('df_uncertified_completo.csv')
# df = pd.read_csv('teste.csv')
df = pd.read_csv('df_uncertified_completo.csv')

df['filtro'] = df['perspective_title'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
df['filtro2'] = df['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))

df['filtro'] = df['perspective_title'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
df['filtro2'] = df['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))

df['filtro'].dropna(inplace=True)
df['filtro2'].dropna(inplace=True)

df = df[(df['filtro'] > 0) & (df['filtro2'] > 0)]

# total = len(df)
# print(total)

df['threat'] = df['perspective_title'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
df['id_attack'] = df['perspective_title'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))

df['media_toxidade_manchete'] = (df['threat'] + df['id_attack']) / 2


df_tox = df[df['media_toxidade_manchete'] < 0.8]
total_tox = len(df_tox)
print(total_tox)
df_nao_tox = df[df['media_toxidade_manchete'] >= 0.8]
total_nao_tox = len(df_nao_tox)
print(total_nao_tox)

# nao toxicos
df_nao_tox['threat_text'] = df_nao_tox['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
df_nao_tox['id_attack_text'] = df_nao_tox['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))

df_nao_tox['media_toxicidade_text_dado_tox'] = (
    df_nao_tox['id_attack_text'] + df_nao_tox['threat_text']) / 2

qtd_tweets_tox_cert_dado_nao_tox = len(
    df_nao_tox[df_nao_tox['media_toxicidade_text_dado_tox'] < 0.8])


qtd_tweets_nao_tox_cert_dado_nao_tox = len(
    df_nao_tox[df_nao_tox['media_toxicidade_text_dado_tox'] >= 0.8])

print('Não toxicos (< 0.8): ', total_nao_tox, 'Toxicos dado que manchete não é tóxica: ',
      qtd_tweets_tox_cert_dado_nao_tox,  'Não toxicos dado que manchete não é tóxica: ', qtd_tweets_nao_tox_cert_dado_nao_tox)
# toxicos
df_tox['threat_text'] = df_tox['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
df_tox['id_attack_text'] = df_tox['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))

df_tox['media_toxicidade_text_dado_tox'] = (
    df_tox['id_attack_text'] + df_tox['threat_text']) / 2

qtd_tweets_tox_cert_dado_tox = len(
    df_tox[df_tox['media_toxicidade_text_dado_tox'] < 0.8])

qtd_tweets_nao_tox_cert_dado_tox = len(
    df_tox[df_tox['media_toxicidade_text_dado_tox'] >= 0.8])

print('Não toxicos (>= 0.8): ', total_tox, 'Toxicos dado que manchete é tóxica: ',
      qtd_tweets_tox_cert_dado_tox,  'Não toxicos dado que manchete é tóxica: ', qtd_tweets_nao_tox_cert_dado_tox)

total_tox = qtd_tweets_tox_cert_dado_tox + qtd_tweets_nao_tox_cert_dado_tox

total_nao_tox = qtd_tweets_tox_cert_dado_nao_tox + \
    qtd_tweets_nao_tox_cert_dado_nao_tox

# total_neg = qtd_sentiment_neg_neg + qtd_sentiment_neu_neg + qtd_sentiment_pos_neg
# total_neu = qtd_sentiment_neg_neu + qtd_sentiment_neu_neu + qtd_sentiment_pos_neu
# total_pos = qtd_sentiment_neg_pos + qtd_sentiment_neu_pos + qtd_sentiment_pos_pos

# rotulos = ['Certificadas', 'Não Certificadas']
rotulos = ['< 0.8', '≥ 0.8']
largura_barra = 0.3

posicoes = np.arange(len(rotulos))

pos_tox = posicoes
pos_nao_tox = posicoes - largura_barra


nao_tox_values = [(qtd_tweets_tox_cert_dado_tox / total_tox),
                  (qtd_tweets_tox_cert_dado_nao_tox / total_nao_tox)]

tox_values = [(qtd_tweets_nao_tox_cert_dado_tox / total_tox),
              (qtd_tweets_nao_tox_cert_dado_nao_tox / total_nao_tox)]

plt.figure(figsize=(4, 3))

plt.bar(pos_nao_tox, nao_tox_values, largura_barra,
        color='b', label='Tweets < 0.8', hatch='//')
plt.bar(pos_tox, tox_values, largura_barra,
        color='#fc6603', label='Tweets ≥ 0.8', hatch='xx')


plt.ylabel('Prob.')
plt.xticks(posicoes, rotulos)
plt.xlabel('Manchete - Não Certificadas')
plt.legend(fontsize=8)
# plt.grid(True)
plt.show()


##############################################
# impacto do sentimento da manchete nos tweets
def obter_texto_apos_url(texto):
    try:
        # print(re.sub(r'https:\/\/t\.co\/[a-zA-Z0-9]+', '', texto))
        return (re.sub(r'https:\/\/t\.co\/[a-zA-Z0-9]+', '', texto))
    except Exception as error:
        print(error)
        return texto


def checar_titulo(x):
    # print(x)
    if x == '[]' or x == "['']" or x == '[""]':
        return 0
    return 1


# scrap_classified_sentiment = pd.read_csv('df_certified_completo.csv')
scrap_classified_sentiment = pd.read_csv('df_uncertified_completo.csv')
# scrap_classified_sentiment = pd.read_csv('teste.csv')

scrap_classified_sentiment['text'] = scrap_classified_sentiment['text'].apply(
    lambda x: obter_texto_apos_url(x))
print(len(scrap_classified_sentiment))
scrap_classified_sentiment.loc[scrap_classified_sentiment['text'].str.len(
) <= 30, 'text'] = ''
scrap_classified_sentiment = scrap_classified_sentiment[scrap_classified_sentiment['text'] != '']
print(len(scrap_classified_sentiment))
scrap_classified_sentiment['titulo_checker'] = scrap_classified_sentiment['titulos'].apply(
    lambda x: checar_titulo(x))
scrap_classified_sentiment = scrap_classified_sentiment[
    scrap_classified_sentiment['titulo_checker'] == 1]
# total = len(scrap_classified_sentiment)
print(len(scrap_classified_sentiment))


# scrap_classified_sentiment = pd.read_csv('df_certified_completo.csv')
# scrap_classified_sentiment = pd.read_csv('df_uncertified_completo.csv')
# scrap_unclassified_sentiment = pd.read_csv('df_uncertified_completo.csv')


print(len(scrap_classified_sentiment))
total = len(scrap_classified_sentiment)

total_neg = len(scrap_classified_sentiment)
total_neu = len(scrap_classified_sentiment)
total_pos = len(scrap_classified_sentiment)
scrap_classified_sentiment['compound'] = scrap_classified_sentiment['sentiment_headline'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))


scrap_classified_sentiment_neg = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] < -0.05]
scrap_classified_sentiment_pos = scrap_classified_sentiment[
    scrap_classified_sentiment['compound'] > 0.05]
scrap_classified_sentiment_neu = scrap_classified_sentiment[(
    scrap_classified_sentiment['compound'] >= -0.05) & (scrap_classified_sentiment['compound'] <= 0.05)]

total_neg = len(scrap_classified_sentiment_neg)
total_pos = len(scrap_classified_sentiment_pos)
total_neu = len(scrap_classified_sentiment_neu)

scrap_classified_sentiment_neg['compound_text'] = scrap_classified_sentiment_neg['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment_neu['compound_text'] = scrap_classified_sentiment_neu['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))
scrap_classified_sentiment_pos['compound_text'] = scrap_classified_sentiment_pos['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

qtd_sentiment_neg_neg = len(scrap_classified_sentiment_neg[
    scrap_classified_sentiment_neg['compound_text'] < -0.05])
qtd_sentiment_neu_neg = len(
    scrap_classified_sentiment_neg[(scrap_classified_sentiment_neg['compound_text'] >= -0.05) & (scrap_classified_sentiment_neg['compound_text'] <= 0.05)])
qtd_sentiment_pos_neg = len(scrap_classified_sentiment_neg[
    scrap_classified_sentiment_neg['compound_text'] > 0.05])

qtd_sentiment_neu_neu = len(
    scrap_classified_sentiment_neu[(scrap_classified_sentiment_neu['compound_text'] >= -0.05) & (scrap_classified_sentiment_neu['compound_text'] <= 0.05)])
qtd_sentiment_neg_neu = len(scrap_classified_sentiment_neu[
    scrap_classified_sentiment_neu['compound_text'] < -0.05])
qtd_sentiment_pos_neu = len(scrap_classified_sentiment_neu[
    scrap_classified_sentiment_neu['compound_text'] > 0.05])

qtd_sentiment_neu_pos = len(
    scrap_classified_sentiment_pos[(scrap_classified_sentiment_pos['compound_text'] >= -0.05) & (scrap_classified_sentiment_pos['compound_text'] <= 0.05)])
qtd_sentiment_neg_pos = len(scrap_classified_sentiment_pos[
    scrap_classified_sentiment_pos['compound_text'] < -0.05])
qtd_sentiment_pos_pos = len(scrap_classified_sentiment_pos[
    scrap_classified_sentiment_pos['compound_text'] > 0.05])

# total_neg = qtd_sentiment_neg_neg + qtd_sentiment_neu_neg + qtd_sentiment_pos_neg
# total_neu = qtd_sentiment_neg_neu + qtd_sentiment_neu_neu + qtd_sentiment_pos_neu
# total_pos = qtd_sentiment_neg_pos + qtd_sentiment_neu_pos + qtd_sentiment_pos_pos

# rotulos = ['Certificadas', 'Não Certificadas']
rotulos = ['Neg.', 'Neu.', 'Pos.']
largura_barra = 0.3
#
posicoes = np.arange(len(rotulos))

pos_neg = posicoes - largura_barra
pos_neu = posicoes
pos_pos = posicoes + largura_barra

neg_values = [(qtd_sentiment_neg_neg / total_neg),
              (qtd_sentiment_neg_neu / total_neu), (qtd_sentiment_neg_pos / total_pos)]


neu_values = [(qtd_sentiment_neu_neg / total_neg),
              (qtd_sentiment_neu_neu / total_neu), (qtd_sentiment_neu_pos / total_pos)]


pos_values = [(qtd_sentiment_pos_neg / total_neg),
              (qtd_sentiment_pos_neu / total_neu), (qtd_sentiment_pos_pos / total_pos)]


plt.figure(figsize=(4, 3))

plt.bar(pos_neg, neg_values, largura_barra,
        color='r', label='Tweet Neg.', hatch='//')
plt.bar(pos_neu, neu_values, largura_barra,
        color='#ffff00', label='Tweet Neu.', hatch='xx')
plt.bar(pos_pos, pos_values, largura_barra,
        color='g', label='Tweet Pos.', hatch='oo')


plt.ylabel('Prob.')
plt.xticks(posicoes, rotulos)
plt.xlabel('Manchete - Certificadas')
plt.legend(fontsize=8)
# plt.grid(True)
plt.show()


# plot sentiment text rebuttal

df_certified = pd.read_csv('./Data_Nova/df_certified.csv')
df_uncertified = pd.read_csv('./Data_Nova/df_uncertified.csv')
df_others = pd.read_csv('./Data_Nova/df_others.csv')
# filtragem de toxicidade se necessária
idattack_val = df_certified['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val = df_certified['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val2 = df_uncertified['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val2 = df_uncertified['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))
idattack_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'IDENTITY_ATTACK'))
threat_val3 = df_others['perspective'].apply(
    lambda x: extract_attribute(x, 'THREAT'))

# filtragem por media de atributos
df_certified['media'] = (idattack_val + threat_val) / 2
df_uncertified['media'] = (idattack_val2 + threat_val2) / 2
df_others['media'] = (idattack_val3 + threat_val3) / 2


# df_certified = df_certified[df_certified['media'] > 0.8]
# df_uncertified = df_uncertified[
#     df_uncertified['media'] > 0.8]
# df_others = df_others[df_others['media'] > 0.8]


df_uncertified['compound'] = df_uncertified['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_unclassified_sentiment_neg = df_uncertified[
    df_uncertified['compound'] < -0.05]
scrap_unclassified_sentiment_pos = df_uncertified[
    df_uncertified['compound'] > 0.05]
scrap_unclassified_sentiment_neu = df_uncertified[(
    df_uncertified['compound'] >= -0.05) & (df_uncertified['compound'] <= 0.05)]

df_certified['compound'] = df_certified['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_classified_sentiment_neg = df_certified[
    df_certified['compound'] < -0.05]
scrap_classified_sentiment_pos = df_certified[
    df_certified['compound'] > 0.05]
scrap_classified_sentiment_neu = df_certified[(
    df_certified['compound'] >= -0.05) & (df_certified['compound'] <= 0.05)]

df_others['compound'] = df_others['sentiment'].apply(
    lambda x: extract_sentiment_attributes(x, 'compound'))

scrap_others_sentiment_neg = df_others[
    df_others['compound'] < -0.05]
scrap_others_sentiment_pos = df_others[
    df_others['compound'] > 0.05]
scrap_others_sentiment_neu = df_others[(
    df_others['compound'] >= -0.05) & (df_others['compound'] <= 0.05)]


rotulos = ['Certificadas', 'Não Certificadas', 'Outras']
categoria = ['Neg.', 'Neu.', 'Pos.']
largura_barra = 0.3

posicoes = np.arange(len(rotulos))

pos_neg = posicoes - largura_barra
pos_neu = posicoes
pos_pos = posicoes + largura_barra

len_class_pos = len(scrap_classified_sentiment_pos)
len_class_neu = len(scrap_classified_sentiment_neu)
len_class_neg = len(scrap_classified_sentiment_neg)

total_class = (len_class_neg + len_class_neu + len_class_pos)

len_unc_pos = len(scrap_unclassified_sentiment_pos)
len_unc_neu = len(scrap_unclassified_sentiment_neu)
len_unc_neg = len(scrap_unclassified_sentiment_neg)

total_unc = (len_unc_neg + len_unc_neu + len_unc_pos)

len_others_pos = len(scrap_others_sentiment_pos)
len_others_neu = len(scrap_others_sentiment_neu)
len_others_neg = len(scrap_others_sentiment_neg)

total_others = (len_others_neg + len_others_neu + len_others_pos)

neg_values = [(len_class_neg / total_class), (len_unc_neg /
                                              total_unc), (len_others_neg / total_others)]
neu_values = [(len_class_neu / total_class), (len_unc_neu /
                                              total_unc), (len_others_neu / total_others)]
pos_values = [(len_class_pos / total_class), (len_unc_pos /
                                              total_unc), (len_others_pos / total_others)]


plt.figure(figsize=(4, 3))

plt.bar(pos_neg, neg_values, largura_barra,
        color='r', label='Neg.', hatch='//')
plt.bar(pos_neu, neu_values, largura_barra,
        color='#ffff00', label='Neu.', hatch='xx')
plt.bar(pos_pos, pos_values, largura_barra,
        color='g', label='Pos.', hatch='oo')


plt.ylabel('# Frac. Tweets')
plt.xticks(posicoes, rotulos)
plt.legend(fontsize=8)
# plt.grid(True)
plt.show()


# cdf rebuttal

df = pd.read_csv('./Data_Nova/main-file-scrap.csv')

attributes = ['THREAT', 'TOXICITY', 'SEVERE_TOXICITY',
              'PROFANITY', 'INSULT', 'IDENTITY_ATTACK']

attribute_colors = {
    'THREAT': '#5898c5',
    'TOXICITY': '#a179c5',
    'SEVERE_TOXICITY': '#d93435',
    'IDENTITY_ATTACK': '#fc8419',
    'INSULT': '#52b152',
    'PROFANITY': '#a57b72'
}


linestyle_str = [
    ('solid', 'solid'),
    ('dotted', 'dotted'),
    ('dashed', 'dashed'),
    ('dashdot', 'dashdot'),
    ('densely_dotted', (0, (1, 1))),
    ('densely dashed', (0, (5, 1)))
]

plt.figure(figsize=(4, 3))

for attribute, (label, linestyle) in zip(attributes, linestyle_str):
    df[attribute] = df['perspective'].apply(
        lambda x: extract_attribute(x, attribute))
    df_filtered = df.dropna(subset=[attribute])
    df_sorted = df_filtered.sort_values(by=attribute, ascending=False)
    values = df_sorted[attribute]
    cumulative_values = np.arange(1, len(values) + 1) / len(values)

    color = attribute_colors.get(attribute, 'black')

    plt.plot(sorted(values), cumulative_values,
             label=attribute, color=color, linestyle=linestyle)

plt.xlabel('Atributo')
plt.ylabel('CDF')
plt.legend(fontsize=7)
# plt.grid(True)
plt.show()
