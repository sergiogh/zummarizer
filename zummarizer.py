## Magazine summarizer for Zinio api
# Usage: python3 zummarizer.py 479606
# Where 479606 is the issue id. A 2nd parameter can be the API token if you want to cache it.

import bs4 as bs
import urllib.request
import json, requests
import sys
import re
import heapq
import ssl
import nltk

nltk.download('punkt')
nltk.download('stopwords')


def parse_article(article):
    parsed_article = bs.BeautifulSoup(article, "html.parser")

    paragraphs = parsed_article.find_all('p')

    article_text = ""

    for p in paragraphs:
        article_text += p.text

    # Removing Square Brackets and Extra Spaces
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)

    # Removing special characters and digits
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

    sentence_list = nltk.sent_tokenize(article_text)

    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1


    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    return summary


issue_id = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2]:
    access_token = sys.argv[2]
else:
    token_url = "https://api-sec.ziniopro.com/oauth/v2/tokens"
    client_id = ''          # Paste your client id here, contact Zinio for one!
    client_secret = ''      # Paste your client secret here, contact Zinio for one!
    data = {'grant_type': 'client_credentials'}
    access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False, auth=(client_id, client_secret))
    tokens = json.loads(access_token_response.text)
    access_token = tokens['access_token']

print("Access Token used: " + access_token)

url_issue = 'https://api-sec.ziniopro.com/newsstand/v2/newsstands/101/issues/'+issue_id
url = 'https://api-sec.ziniopro.com/catalog/v2/issues/'+issue_id+'/stories?css_content=true'

headers = { 'Authorization' : 'Bearer '+access_token }

issue_data_request = urllib.request.Request(url_issue, headers = headers)
response_issue = urllib.request.urlopen(issue_data_request)
issue_data = json.loads(response_issue.read().decode(response_issue.info().get_param('charset') or 'utf-8'))

story_data_request = urllib.request.Request(url, headers = headers)
response_stories = urllib.request.urlopen(story_data_request)
stories_data = json.loads(response_stories.read().decode(response_stories.info().get_param('charset') or 'utf-8'))

print(url)
print("Your Full Issue abridged - Very short very short!!")
print("Magazine: " + issue_data['data']['publication']['name'] + ' - ' + issue_data['data']['name'])

articles = stories_data['data']

for article_json in articles:
    article = article_json['content']
    summary = parse_article(article)

    print("Title: "+article_json['title'])
    print(article_json['feature_image'])
    print(summary)
    print("-------------------")
