import html
from twilio.rest import Client
import requests
import os


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_apikey = os.environ["STOCK_API_KEY"]

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_endpoint = "https://www.alphavantage.co/query"
stock_param = {
    "function" : "TIME_SERIES_DAILY_ADJUSTED",
    "symbol" : "TSLA",
    "apikey" : stock_apikey
}

response = requests.get(url=stock_endpoint, params=stock_param)
response.raise_for_status()
stock_data = response.json()

keys= []
daily_stock_Data = stock_data["Time Series (Daily)"]
n = 0
for key, value in daily_stock_Data.items():
    pair = (key, value)
    keys.append(pair)
    n += 1
    if n > 1:
        break

# print(keys)  #Testing

# To get the percentage increase and decrease formula is ((value/total value)-1)*100
# -ve value = get decreases from previous day
# +ve value = Value get increases as compare to day before yesterday

yesterday_open_value = keys[0][1]["1. open"]
before_yesterday_close_value = keys[1][1]["4. close"]

percentage = round((((float(yesterday_open_value))/(float(before_yesterday_close_value)))-1)*100)
# print(percentage)


## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
news_api_key = os.environ["NEWS_API_KEY"]
news_end_point = "https://newsapi.org/v2/top-headlines"
# Working API string: https://newsapi.org/v2/top-headlines?q=tesla&apiKey

news_param = {
    "q": "tesla",
    "apiKey": news_api_key
}

news_response = requests.get(url=news_end_point, params=news_param)
news_response.raise_for_status()

news_data = news_response.json()

# Printing the top headlines for tesla from new API
# print(news_data)
headline = news_data["articles"][0]["title"]
brief = html.unescape(news_data["articles"][0]["description"])
# print(headline)
# print(brief)


#Optional: Format the SMS message like this:
if percentage >= 0:
    changes = f'TSLA: 🔺{percentage}%'
elif percentage < 0:
    changes = f'TSLA: 🔻{abs(percentage)}%'

"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages.create(
                     body=f"{changes}\nHeadline: {headline}\nBrief: {brief}",
                     from_=os.environ["MY_TWILIO_NUMBER"],
                     to=os.environ["MY_NUMBER"]
                 )

print(message.status)
