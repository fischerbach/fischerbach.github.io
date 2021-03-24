import streamlit as st
import pandas as pd
import numpy as np

import datetime
import urllib
import json

import requests
import cachetools

st.title("Website stats and Fraud Detection")

class IPQS(object):
    def __init__(self, key='', base='https://ipqualityscore.com/api/json/ip'):
        self.key = key
        self.base = f"{base}/{key}"


    @cachetools.cached(cachetools.TTLCache(1000, 600))
    def check(self, ip, options={}):
        default_options = {
            "allow_public_access_points":True,
            "mobile":True,
            "fast":False,
            "strictness":0,
            "lighter_penalties":True
        }

        for option in default_options.keys():
            if(option in options.keys()):
                default_options[option] = options[option]

        url = f'{self.base}/{ip}?{urllib.parse.urlencode(default_options)}'
        def req(url):
            return requests.get(url)
        response = req(url)
        return response.json()

ipscore = IPQS(key='KEY')

ip = st.text_input('Enter IP to check:')

if(ip != ''):
    st.write(ipscore.check(ip))

st.header('Website statistics')
logs = pd.read_csv('logs.txt', sep='\t', names=['timestamp', 'url', 'referer', 'ip', 'useragent'])
logs['datetime'] = pd.to_datetime(logs['timestamp'], unit='s')
daily_data = logs.groupby(by=logs['datetime'].dt.date).agg(
        {
            'url':'count',
            'ip': 'nunique',
            'useragent': 'nunique'
        }
    ).rename(columns={'url':'visits', 'ip': 'unique ip addresses', 'useragent':'unique useragents'})
st.write(daily_data)

logs_with_source = logs.loc[logs['url'].str.contains("utm_source=")]

def attribution(row):
    log_before = logs_with_source.set_index('datetime').query(f'ip == \'{row["ip"]}\' and index <= \'{row["datetime"]}\'').sort_values(by='datetime', ascending=False)
    try:
        return log_before.iloc[0]['url'].split("utm_source=")[1]
    except:
        return "organic"

logs['source'] = logs.apply(attribution, axis=1)

st.header('Campaign Monitoring')
source = st.selectbox('Select source of traffic', options=logs['source'].unique())
daily_data = logs.loc[logs['source'] == source].groupby(by=logs['datetime'].dt.date).agg(
        {
            'url':'count',
            'ip': 'nunique',
            'useragent': 'nunique'
        }
    ).rename(columns={'url':'visits', 'ip': 'unique ip addresses', 'useragent':'unique useragents'})
st.write(daily_data)
hourly_data = logs.loc[logs['source'] == source].resample('H', on='datetime').agg(
        {
            'url':'count',
            'ip': 'nunique',
            'useragent': 'nunique'
        }
    ).rename(columns={'url':'visits', 'ip': 'unique ip addresses', 'useragent':'unique useragents'})

st.line_chart(hourly_data)

ip_db = pd.read_csv('ip_db.csv')
def get_score(ip):
    try:
        return eval(ip_db.query(f'ip=="{ip}"')['result'].iloc[0]) #Don't use eval() unless you can absolutely trust input string!
    except:
        print("!")
        return ipscore.check(ip)

check_frauds = st.button('Check frauds')
if(check_frauds):
    logs['result'] = logs.loc[logs['source'] == source]['ip'].apply(get_score)
    results = logs.loc[logs['source'] == source].copy()
    results = pd.concat([results, results['result'].apply(pd.Series)], axis=1)

    st.header(f"FRAUD SCORE: {results['fraud_score'].mean()}")
    st.write(results.tail())
    if(results['fraud_score'].mean() <= 75):
        st.balloons()

    ip_db = pd.concat([ip_db, logs[['ip','result']]])
    ip_db.to_csv('ip_db.csv', index=False)


