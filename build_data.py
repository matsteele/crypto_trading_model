import pandas as pd
import numpy as np


class BuildCryptoData:
    def __init__(self, data, initialAmmount=1000, aggBin=3, window=4):
        self.initialAmmount = initialAmmount
        self.data = data
        self.mergedCrypto = self.mergeCrypto()
        self.AggData = self.buildAggData(aggBin)
        self.buildRollingAverages(window)
        self.buildLabel()

    def mergeCrypto(self):
        mergedCrypto = self.data['BTC'].merge(
            self.data['ETH'], how='outer', on='trade_date', suffixes=('_BTC', '_ETH'))

        self.data['LTC'].columns = ['uuid_LTC', 'symbol_LTC', 'open_LTC', 'high_LTC', 'low_LTC', 'close_LTC', 'volume_btc_LTC',
                                    'volume_usd', 'trade_date']
        mergedCrypto = mergedCrypto.merge(
            self.data['LTC'], how='outer', on='trade_date')
        
        mergedCrypto['date'] = mergedCrypto['trade_date']
        mergedCrypto['volume_BTC'] = mergedCrypto['volume_btc_BTC']
        mergedCrypto['volume_ETH'] = mergedCrypto['volume_btc_ETH']
        mergedCrypto['volume_LTC'] = mergedCrypto['volume_btc_LTC']

        dropcolumns = [x for x in mergedCrypto.columns if x.startswith(
            ('symbol', 'uuid', 'trade_date', 'volume_btc_'))]
        mergedCrypto.drop(dropcolumns, axis=1, inplace=True)
        return mergedCrypto

    def buildAggData(self, aggBin):
        self.mergedCrypto = self.mergedCrypto.reindex(
            index=self.mergedCrypto.index[::-1])
        self.mergedCrypto.reset_index(inplace=True, drop=True)

        def collapseWithGrowth(cryptoData):
            # group by id/3
            # get first day
            columns = [x for x in cryptoData.columns]
            groupByObject = cryptoData.groupby(
                cryptoData.index//aggBin)[columns]
            crypto_Agg_first = groupByObject.first()
            crypto_Agg_first.columns = [x + '_fstd' for x in columns]
            crypto_Agg_first.reset_index(inplace=True)

            crypto_Agg_last = groupByObject.last()
            crypto_Agg_last.columns = [x + '_lstd' for x in columns]
            crypto_Agg_last.reset_index(inplace=True)
            crypto_Agg = crypto_Agg_first.merge(
                crypto_Agg_last, how='outer', on='index')

        # findGrowth
            for eachCrypto in self.data:

                # get price growth
                crypto_Agg['growth_'+eachCrypto] = (crypto_Agg['price_'+eachCrypto+'_lstd'] 
                                                    - crypto_Agg['price_'+eachCrypto+'_fstd']) / crypto_Agg['price_'+eachCrypto+'_fstd']
                # get volume change volume LTC_lstd
                crypto_Agg['volu_growth_'+eachCrypto] = (crypto_Agg['volume_'+eachCrypto+'_lstd'] 
                                                        - crypto_Agg['volume_'+eachCrypto+'_fstd']) / crypto_Agg['volume_'+eachCrypto+'_fstd']
                # get price volatility
                crypto_Vol = cryptoData.groupby(
                    cryptoData.index//aggBin)['price_'+eachCrypto].agg(np.std)
                crypto_Agg['volat_'+eachCrypto] = crypto_Vol.values

            dropcolumns = [x for x in crypto_Agg.columns if x.startswith(
                ('Open', 'high', 'close', 'low'))]
            crypto_Agg.drop(dropcolumns, axis=1, inplace=True)
            return crypto_Agg

        # get average price per day
        for eachCrypto in self.data:
            self.mergedCrypto['price_'+eachCrypto] = (
                self.mergedCrypto['high_'+eachCrypto] + self.mergedCrypto['low_'+eachCrypto])/2
            self.mergedCrypto['range_'+eachCrypto] = self.mergedCrypto['high_' +
                                                                       eachCrypto] - self.mergedCrypto['low_'+eachCrypto]

        return collapseWithGrowth(self.mergedCrypto)

    def buildLabel(self):
        def whichCrypto(row, direction):
            b = row['growth_BTC']
            e = row['growth_ETH']
            l = row['growth_LTC']

            maxGrowthForThatDay = np.nanmax([b, e, l])
            minGrowthForThatDAy = np.nanmin([b, e, l])

            if direction == 'up':
                comp = maxGrowthForThatDay  # what will gain you the most money
            elif direction == 'dwn':
                comp = minGrowthForThatDAy  # what will lose you the most money

            if comp == b:
                return 'BTC'
            elif comp == e:
                return 'ETH'
            elif comp == l:
                return 'LTC'

        self.AggData['WhichCryptoUp'] = self.AggData.apply(
            whichCrypto, direction='up', axis=1)
        self.AggData['WhichCryptoDwn'] = self.AggData.apply(
            whichCrypto, direction='dwn', axis=1)
        self.AggData['upORdwn'] = self.AggData[[
            'growth_BTC', 'growth_ETH', 'growth_LTC']].mean(axis=1)
        self.AggData['upORdwn'] = self.AggData['upORdwn'].apply(
            lambda x: 1 if x > 0 else 0)

    def buildRollingAverages(self, window):
        self.AggData.sort_index(inplace=True)
        for i in range(len(self.AggData.columns)):
            name = self.AggData.columns[i]
            dtype = self.AggData[name].dtype
            if dtype == 'float':
                self.AggData['rol_' + name] = self.AggData.iloc[:,
                                                                i].rolling(window=window).mean()
