import datetime
from pytrends.request import TrendReq
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt


def get_trends(keyword, days, end_date):
    """Specify start and end date as well es the required keyword for your query"""
    print("Trend keyword: ", keyword)

    """Calculating start date from end date, based on given interval"""
    end_date += datetime.timedelta(days=1)
    print("Today's date: ", end_date)
    start_date = end_date - datetime.timedelta(days=days)
    print(start_date, end_date)

    """Since we want weekly data for our query, we will create lists which include
    the weekly start and end date."""

    weekly_date_list = []

    # Adds the start date as first entry in our weekly_date_list
    start_date_temp = start_date
    weekly_date_list.append(start_date_temp)

    # This will return in list of weekly datetime.date objects - except the end date
    while start_date_temp + datetime.timedelta(days=7) <= end_date:
        start_date_temp += datetime.timedelta(days=7)
        weekly_date_list.append(start_date_temp)

    # This will add the end date to the weekly_date list. We now have a complete list in the specified time frame
    if start_date_temp + datetime.timedelta(days=7) > end_date:
        weekly_date_list.append(end_date)

    print(weekly_date_list)

    """Now we can start to downloading the data via Google Trends API
    therefore we have to specify a key which includes the start date
    and the end-date with T00 as string for hourly data request"""

    """This list will contain pandas Dataframes of weekly data with the features "date",
    "keyword"(which contains weekly scaling between 0 and 100), "isPartial".
    Up to this point, the scaling is not correct."""

    interest_list = []

    # Here we download the data and print the current status of the process
    i = 0
    waiting_time = 60
    while i < len(weekly_date_list) - 1:
        key = str(weekly_date_list[i]) + "T00 " + str(weekly_date_list[i+1]) + "T00"
        try:
            p = TrendReq()
            p.build_payload(kw_list=[keyword], timeframe=key)
            interest = p.interest_over_time()
            interest_list.append(interest)
            print(i)
            print(interest)
            print("GoogleTrends Call {} of {} : Timeframe: {} ".format(i + 1, len(weekly_date_list) - 1, key))
        except:
            print("Timed out. Retrying in {} secs...".format(waiting_time))
            time.sleep(waiting_time)
            i -= 1
        i += 1

    # print(interest_list)

    """Now we have to rescale our weekly data. We can do this
    by overlapping the weekly timeframes by one data point."""

    """We define a ratio list, which includes the correction parameters
    = (scaling last hour of week i / scaling first hour of week i+1)"""
    ratio_list = []

    # here we apply the correction parameter to all dfs in the interest list except interest_list[0]
    for i in range(len(interest_list) - 1):
        # Check - To prevent zero division error and not eliminate data on rescaling (zero multiplication)
        interest_list[i + 1][keyword] = interest_list[i + 1][keyword].apply(lambda x: x + 1)
        ratio = float(interest_list[i][keyword].iloc[-1])/float(interest_list[i+1][keyword].iloc[0])
        ratio_list.append(ratio)

        # print("{} of {}: Ratio = {}, Scale 1st hour of week {} = {}, scale last hour of week {} = {}"
        #       .format(i+1, len(interest_list)-1, ratio_list[i],
        #               i+1, float(interest_list[i+1][keyword].iloc[0]),
        #               i, float(interest_list[i][keyword].iloc[-1]),))

        """Multiply the ratio with the scales of week i+1
        Therefore we add the column "Scale" and multiply times the value in ratio_list[i]
        The make the calculations work for round i+1, we overwrite the values column of the df[keyword]
        with df["Scale"] in the interest list"""

        interest_list[0]["Scale_{}".format(keyword)] = interest_list[0][keyword]
        interest_list[i+1]["Scale_{}".format(keyword)] = interest_list[i+1][keyword].apply(lambda x: x * ratio_list[i])
        interest_list[i+1][keyword] = interest_list[i+1]["Scale_{}".format(keyword)]

    """We now combine the dataframes in the interest list to a Pandas dataframe.
    The data has the correct scaling now. But not yet in the range of 0 and 100."""

    df = pd.concat(interest_list)
    df.drop(labels=keyword, axis=1, inplace=True)
    df.drop(labels="isPartial", axis=1, inplace=True)
    # print(df.head(5))

    """As last step we scale the data back like google to a range between 0 and 100."""
    max_interest = np.max(df["Scale_{}".format(keyword)])
    df["Scale_{}".format(keyword)] = df["Scale_{}".format(keyword)]/max_interest * 100

    # print(df.describe())
    df.to_csv(r'C:\Users\Niv\PycharmProjects\ReinforcementLearning\{}_Trend.csv'.format(keyword))

    # plt.plot(df)
    # plt.xlabel('Time')
    # plt.ylabel('Number of Hits')
    # plt.title(keyword)
    # plt.show()


if __name__ == '__main__':
    # (12/31/2019 and 02/20/2020)

    # keywords1 = 'S&P500 stock' 2019, 'Stockmarket crash' 2019, 'S&P500 stock' 2020, 'Coronavirus' 2020
    # keywords2 = 'Netflix stock' 2019, 'Stockmarket crash' 2019, 'Netflix stock' 2020, 'Coronavirus' 2020

    # # specific trends(2019):
    # trend = 'S&P500 stock'
    # days = 365
    # date_of_prediction = datetime.date(2019, 12, 31)  # Y-M-D
    # get_trends(trend, days, date_of_prediction)
    #
    # trend = 'Netflix stock'
    # days = 365
    # date_of_prediction = datetime.date(2019, 12, 31)  # Y-M-D
    # get_trends(trend, days, date_of_prediction)

    # # specific trends(2020):
    # trend = 'S&P500 stock'
    # days = 365
    # date_of_prediction = datetime.date(2020, 2, 20)  # Y-M-D
    # get_trends(trend, days, date_of_prediction)

    # trend = 'Netflix stock'
    # days = 365
    # date_of_prediction = datetime.date(2020, 2, 20)  # Y-M-D
    # get_trends(trend, days, date_of_prediction)

    # common trends:
    trend = 'Stockmarket crash'
    days = 365
    date_of_prediction = datetime.date(2020, 2, 20)  # Y-M-D
    get_trends(trend, days, date_of_prediction)

    # trend = 'Coronavirus'
    # days = 365
    # date_of_prediction = datetime.date(2020, 2, 20)  # Y-M-D
    # get_trends(trend, days, date_of_prediction)