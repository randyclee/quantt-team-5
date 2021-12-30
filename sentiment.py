from QuantConnect.Data.Custom.Benzinga import *
import nltk
from vaderSentiment import SentimentIntensityAnalyzer, pairwise
from datetime import datetime, timedelta
import numpy as np

class SentimentModel:

    def __init__(self, vaderData):
        self.day = -1
        self.custom = []
        self.vaderData = vaderData

    def Update(self, algorithm, data):
        insights = []

        if algorithm.Time.day == self.day:
            return insights

        self.day = algorithm.Time.day

        weights = {}

        for security in self.custom:

            if not data.ContainsKey(security):
                continue

            news = data[security]

            sid = SentimentIntensityAnalyzer(lexicon_file=self.vaderData)

            sentiment = sid.polarity_scores(news.Description.lower())
            if sentiment["compound"] > 0:
                weights[security.Underlying] = sentiment["compound"]

        count = min(10, len(weights))
        if count == 0:
            return insights

        sortedbyValue = sorted(weights.items(), key = lambda x:x[1], reverse=True)
        selected = {kv[0]:kv[1] for kv in sortedbyValue[:count]}

        closeTimeLocal = Expiry.EndOfDay(algorithm.Time)
        for symbol, weight in selected.items():
            insights.append(Insight.Price(symbol, closeTimeLocal, InsightDirection.Up, None, None, None, abs(weight)))

        return insights


    def OnSecuritiesChanged(self, algorithm, changes):
        for security in changes.AddedSecurities:
            if security.Type == SecurityType.Equity:
                self.custom.append(algorithm.AddData(benzingaNews, security.Symbol).Symbol)
