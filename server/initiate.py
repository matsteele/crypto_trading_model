from pandas import DataFrame
import sqlite3
from psycopg2 import connect
import pandas as pd
from datetime import datetime as dt
from build_data import BuildCryptoData
from model import CryptoModel

conn = connect(
    database="blockfi",
    user="datascience",
    port="5432",
    host="localhost",
    password="data"
)

def pullDataForChart(aggBin, window):
    tablename = 'data4vis_per_'+str(aggBin) + "_win_" + str(window)
    sql = "SELECT * FROM " + tablename

    df = pd.read_sql_query(sql, conn)
    print('sum', pd.Series.sum(df.error)/df.shape[0])
    
    return pd.read_sql_query(sql, conn)

def initiate():
    def connectAndBuild():
        sql_b = "SELECT * FROM crypto WHERE symbol='BTCUSD'"
        sql_e = "SELECT * FROM crypto WHERE symbol='ETHUSD'"
        sql_l = "SELECT * FROM crypto WHERE symbol='LTCUSD'"
        btcusd = pd.read_sql_query(sql_b, conn)
        ethusd = pd.read_sql_query(sql_e, conn)
        ltcusd = pd.read_sql_query(sql_l, conn)

        return BuildCryptoData({'BTC': btcusd, 'ETH': ethusd, 'LTC': ltcusd})
    startDate = '2018-01-01'
    CryptoData = connectAndBuild()
    first_day = setup(initial_amount=1000, startDate=startDate,
                      AggData=CryptoData.AggData)
    return buildDataForDashboard(CryptoData.AggData, startDate, first_day)


def setup(initial_amount, AggData, startDate,):
    startdate_DT = dt.strptime(startDate, '%Y-%m-%d').date()
    AggData['date'] = pd.to_datetime(AggData['date_fstd'])
    AggData.set_index('date', inplace=True, drop=False)
    dataBefore = AggData[
        AggData['date_fstd'] < startdate_DT]

    def find_intial_holdings(startDate):
        b_mean = dataBefore['growth_BTC'].mean()
        e_mean = dataBefore['growth_ETH'].mean()
        b_share = b_mean/(b_mean+e_mean)
        e_share = e_mean/(b_mean+e_mean)

        b_price = AggData.loc[startDate]['price_BTC_fstd']
        e_price = AggData.loc[startDate]['price_ETH_fstd']

        initial_holdings = {
            'BTC': ((initial_amount*b_share)/b_price),
            'ETH': ((initial_amount*e_share)/e_price),
            'LTC': 0
        }

        return initial_holdings

    initial_holdings = find_intial_holdings(startdate_DT)

    return CryptoModel(date=startDate, prev_holdings=initial_holdings,
                       ifusd_crypto_prev=initial_holdings, ifusd_USD_prev_val=0,
                 past_data=dataBefore, curr_data=AggData.loc[startdate_DT])


def buildDataForDashboard(AggData, startdate, first_day):
    # startdate = dt.strptime(startDate, '%Y-%m-%d').date()
    modelsByDate = {startdate: first_day}
    dateArray = [first_day.date]
    holdings_rel = [first_day.new_holdings_rel]
    account_value = [int(first_day.new_holdings_val)]
    valueof_intial_holding = [int(first_day.init_holdings_val)]
    BTCArr = [first_day.new_holdings_rel['BTC']]
    ETHArr = [first_day.new_holdings_rel['ETH']]
    LTCArr = [first_day.new_holdings_rel['LTC']]

    error=[1]

    #ifusd vars
    BTCArr_ifusd = [first_day.ifusd_crypto_new_rel['BTC']]
    ETHArr_ifusd = [first_day.ifusd_crypto_new_rel['ETH']]
    LTCArr_ifusd = [first_day.ifusd_crypto_new_rel['LTC']]
    ifusd_crypto_new_val = [(int(first_day.ifusd_crypto_new_val))]
    ifusd_USD_new_val = [(int(first_day.ifusd_USD_new_val))]
    ifusd_total_bal_new = [(int(first_day.ifusd_total_bal_new))]


    for i in range(AggData[AggData['date'] < startdate].shape[0]+1, AggData.shape[0]):
        date = AggData.iloc[i]['date'].strftime("%Y-%m-%d")

        dataBefore = AggData[AggData['date'] < pd.Timestamp(date)]
        dataCurr=AggData.loc[date]
        # print(date)
        dateBefore = AggData.iloc[i-1]['date'].strftime("%Y-%m-%d")
        prevModel = modelsByDate[dateBefore]
        prev_holdings = prevModel.new_holdings
        ifusd_crypto_prev = prevModel.ifusd_crypto_new
        ifusd_USD_prev_val = prevModel.ifusd_USD_new_val

        model = CryptoModel(date=date, past_data=dataBefore,
                            ifusd_crypto_prev=ifusd_crypto_prev, ifusd_USD_prev_val=ifusd_USD_prev_val,
                            prev_holdings=prev_holdings, curr_data=dataCurr)

        modelsByDate[date] = model

        dateArray.append(date)
        holdings_rel.append(model.new_holdings_rel)
        BTCArr.append(model.new_holdings_rel['BTC'])
        ETHArr.append(model.new_holdings_rel['ETH'])
        LTCArr.append(model.new_holdings_rel['LTC'])
        account_value.append(int(model.new_holdings_val))
        valueof_intial_holding.append(int(model.init_holdings_val))

        error.append(int(prevModel.predictedupORdwn == dataCurr.upORdwn))

        #if usd vars
        BTCArr_ifusd.append(model.ifusd_crypto_new_rel['BTC'])
        ETHArr_ifusd.append(model.ifusd_crypto_new_rel['ETH'])
        LTCArr_ifusd.append(model.ifusd_crypto_new_rel['LTC'])
        ifusd_crypto_new_val.append(int(model.ifusd_crypto_new_val))
        ifusd_USD_new_val.append(int(model.ifusd_USD_new_val))
        ifusd_total_bal_new.append(int(model.ifusd_total_bal_new))
        
    data = {'dates': dateArray,
            'BTC': BTCArr,
            'ETH':  ETHArr,
            'LTC': LTCArr,
            'account_val': account_value,
            'valueof_intial_holding': valueof_intial_holding,
            'error': error,
            'ifusd_BTC': BTCArr_ifusd,
            'ifusd_ETH':  ETHArr_ifusd,
            'ifusd_LTC': LTCArr_ifusd,
            'ifusd_account_val': ifusd_total_bal_new,
            'ifusd_cash_val': ifusd_USD_new_val,
            'ifusd_crypto_val':   ifusd_crypto_new_val
            }  # also build errors

    df = pd.DataFrame(data)

    return df


def logToSqL(startDate='2018-01-01'):
    sql_b = "SELECT * FROM crypto WHERE symbol='BTCUSD'"
    sql_e = "SELECT * FROM crypto WHERE symbol='ETHUSD'"
    sql_l = "SELECT * FROM crypto WHERE symbol='LTCUSD'"

    btcusd = pd.read_sql_query(sql_b, conn)
    ethusd = pd.read_sql_query(sql_e, conn)
    ltcusd = pd.read_sql_query(sql_l, conn)

    for eachPeriod in [2,3,4]:
        for eachWindow in range(1,5):

            CryptoData = BuildCryptoData(
                {'BTC': btcusd, 'ETH': ethusd, 'LTC': ltcusd}, aggBin=eachPeriod, window=eachWindow)

            first_day = setup(initial_amount=1000, startDate=startDate,
                              AggData=CryptoData.AggData)

            df = buildDataForDashboard(
                CryptoData.AggData, startDate, first_day)
            print('logged', eachPeriod, eachWindow)
            from sqlalchemy import create_engine
            engine = create_engine(
                "postgresql://datascience:data@localhost:5432/blockfi")
            df.to_sql('data4vis_per_'+str(eachPeriod) + "_win_" + str(eachWindow), con=engine,
                      if_exists='replace', index=False)


if __name__ == "__main__":
    logToSqL()
