import json
import pandas as pd
import tldextract
from newspaper import Article
from decouple import config
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


def extract_attribute(json_str, attribute):
    json_str = json_str.replace("'", "\"").replace("\n", "").replace("\r", "")
    try:
        data = json.loads(json_str)
        if isinstance(data, dict):
            return data.get('attributeScores', {}).get(attribute, {}).get('summaryScore', {}).get('value')
    except json.JSONDecodeError:
        return None
    return None


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


def get_scrap(urls):
    print(urls)
    try:
        urls = ast.literal_eval(urls)
    except (SyntaxError, ValueError):
        print("Erro ao avaliar as URLs:", urls)
        return None

    df_list = []

    for url in urls:
        if "twitter.com" in url or "t.co" in url or "youtube" in url or "instagram" in url:
            print("Scrap not required for the url:", url)
            continue
        try:
            url = url.strip("[]").replace("'", "")
            artigo = Article(url)

            artigo.download()
            artigo.parse()
            artigo.nlp()

            palavras_chave = artigo.keywords
            resumo = artigo.summary.replace("\n", "").replace("|", "")
            titulo = artigo.title.replace("\n", "").replace("|", "")
            autor = artigo.authors
            data_publicacao = artigo.publish_date
            conteudo = artigo.text.replace("\n", "").replace("|", "")
            videos = artigo.movies

            df_list.append({
                'Título': [titulo],
                'Autor': [autor],
                'Palavras-chave': [palavras_chave],
                'Videos': [videos],
                'Resumo': [resumo],
                'Data de Publicação': [data_publicacao],
                'Conteúdo': [conteudo]
            })

        except Exception as e:
            print(f"Ocorreu um erro: {e}")

    if df_list:
        return df_list
    else:
        return None


def get_webpage(urls):

    urls = ast.literal_eval(urls)
    for url in urls:
        if not url:
            continue
    # df_list = []
    for url in urls:
        print(url)
        if "twitter.com" in url or "t.co" in url or "youtube" in url or "instagram" in url:
            print("Scrap not required for the url: ", url)
            continue
        try:
            url = url.strip("[]").replace("'", "")

            parsed_url = urlparse(url)
            base_dir = parsed_url.netloc

            target_dir = f"./webcopy/"
            save_webpage(url, target_dir)
        except:
            print("Couldnt save webpage!")
            continue


def analyze_comment(comment_text):
    api_key = config('API_PERSPECTIVE')
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


def extract_domain(url):
    extracted = tldextract.extract(url)
    return extracted.domain + '.' + extracted.suffix


def extract_sentiment_attributes(sentiment_score, attribute):
    sentiment_dict = eval(sentiment_score)
    x = sentiment_dict.get(attribute, -2.0)
    return x
