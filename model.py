from sklearn.ensemble import GradientBoostingClassifier
import math
import numpy as np

class CryptoModel:

    initial_breakdown = {'BTC': 0.030638125273752783,
                         'ETH': 0.80073259360567473, 'LTC': 0}

    def __init__(self, date, prev_holdings, ifusd_crypto_prev, ifusd_USD_prev_val, past_data, curr_data):
        self.date = date
        self.b_price = curr_data['price_BTC_fstd']
        self.e_price = curr_data['price_ETH_fstd'] if not math.isnan(
            curr_data['price_ETH_fstd']) else 0
        self.l_price = curr_data['price_LTC_fstd'] if not math.isnan(
            curr_data['price_LTC_fstd']) else 0
        #crypto holdings
        self.prev_holdings = prev_holdings
        self.prev_holdings_val = self.convertHoldingsToUSD(self.prev_holdings)
        self.init_holdings_val = self.convertHoldingsToUSD(
            self.initial_breakdown)
        # ifusd vars
        self.ifusd_crypto_prev = ifusd_crypto_prev
        self.ifusd_crypto_prev_val = self.convertHoldingsToUSD(
            ifusd_crypto_prev)
        self.ifusd_USD_prev_val = ifusd_USD_prev_val
        
        self.past_data = past_data
        self.curr_data = curr_data

        self.model_up = self.buildCoinModel('WhichCryptoUp')
        self.model_dwn = self.buildCoinModel('WhichCryptoDwn')
        self.model_dir = self.buildDirModel()
        self.predictedupORdwn = self.predictDir()
        self.predictions_Up = self.setPredictions(self.model_up)
        self.predictions_Dwn = self.setPredictions(self.model_dwn)
        self.find_holdingChanges()

    def buildDirModel(self):
        #label
        y = self.past_data['upORdwn']
        # features
        X = self.past_data.filter(regex='^rol', axis=1).fillna(-99999999)
        X['date'] = X.index
        X['date'] = X['date'].apply(lambda x: x.toordinal())
        #fit
        dir_model = GradientBoostingClassifier(n_estimators=10)
        dir_model.fit(X, y)
        #score
        self.dir_R2 = np.round(dir_model.score(X, y), 4)
#         print(f'dir model R^2 Score: {np.round(dir_model.score(X, y), 4)}')

        return dir_model

    def buildCoinModel(self, which_crypto_upORdwn):
        # label
        cleanup_nums = {'BTC': 0, "ETH": 1, 'LTC': 2}
        y = self.past_data[which_crypto_upORdwn].replace(
            cleanup_nums).astype(int)
        # features
        X = self.past_data.filter(regex='^rol', axis=1).fillna(-99999999)
        X['date'] = X.index
        X['date'] = X['date'].apply(lambda x: x.toordinal())
        #fit
        coin_model = GradientBoostingClassifier(n_estimators=10)
        coin_model.fit(X, y)
        #score
        self.coin_R2 = np.round(coin_model.score(X, y), 4)

        return coin_model

    def predictDir(self):
        date = self.curr_data['date'].toordinal()
        X = self.curr_data.filter(regex='^rol').fillna(-99999999)
        X['date'] = date
        self.dir_probs_soft = self.model_dir.predict_proba(
            X.values.reshape(1, -1))
        return self.model_dir.predict(X.values.reshape(1, -1))

    def setPredictions(self, model):
        date = self.curr_data['date'].toordinal()
        X = self.curr_data.filter(regex='^rol').fillna(-99999999)
        X['date'] = date
        probs_ = model.predict_proba(X.values.reshape(1, -1))
        probs = {}

        probs['BTC'] = probs_[0][0]
        if len(probs_[0]) > 1:
            probs['ETH'] = probs_[0][1]
        if len(probs_[0]) > 2:
            probs['LTC'] = probs_[0][0]
        return probs

    def convertHoldingsToUSD(self, holdings):
        return holdings['BTC'] * self.b_price + holdings['ETH'] * self.e_price + holdings['LTC'] * self.l_price

    def find_holdingChanges(self):
        dwn_inverse = {x: 1-self.predictions_Dwn[x]
                       for x in self.predictions_Dwn}
        predictions = self.predictions_Up if self.predictedupORdwn == 1 else dwn_inverse
        prob_upORdwn = self.dir_probs_soft[0][1] if self.predictions_Up else self.dir_probs_soft[0][0]

        relative_predictions = {}
        total_confidence = math.fsum(predictions.values())  # sum up all
        relative_predictions['BTC'] = predictions['BTC'] / total_confidence
        if len(predictions) > 1:
            relative_predictions['ETH'] = predictions['ETH'] / total_confidence
        if len(predictions) > 2:
            relative_predictions['LTC'] = predictions['LTC'] / total_confidence

        amountToChange_portion = total_confidence * self.dir_R2 * prob_upORdwn
        amountToChange = self.prev_holdings_val * amountToChange_portion
        amountRemains = self.prev_holdings_val - amountToChange

        def determinHoldover(amountRemains, prev_holdings, prev_holdings_val):
            BTCShare = (prev_holdings['BTC' ] * self.b_price) / prev_holdings_val
            ETHShare = (prev_holdings['ETH' ] * self.e_price) / prev_holdings_val 
            LTCShare = (prev_holdings['LTC' ] * self.l_price) / prev_holdings_val
            
            holdOver_BTC = (amountRemains * BTCShare)/ self.b_price
            holdOver_ETH = (amountRemains * ETHShare)/ self.e_price
            holdOver_ETH = holdOver_ETH if not math.isnan(holdOver_ETH) else 0.0

            if self.l_price == 0 or math.isnan(self.l_price):
                holdOver_LTC = 0
            else:
                holdOver_LTC = (amountRemains * LTCShare )/ self.l_price
                
            return [holdOver_BTC,  holdOver_ETH,holdOver_LTC]
                        
        def findChanges(relative_predictions,amountToChange):
            changes_BTC = amountToChange*relative_predictions['BTC'] / self.b_price
            changes_ETH = amountToChange*relative_predictions['ETH'] / self.e_price if 'ETH' in predictions else 0
            changes_LTC = amountToChange*relative_predictions['LTC'] / self.l_price if 'LTC' in predictions else 0
            return [changes_BTC, changes_ETH, changes_LTC]
        
        h = determinHoldover(amountRemains, self.prev_holdings, self.prev_holdings_val)
        c = findChanges(relative_predictions, amountToChange)
        
        def setHoldings(h, c):
            new_holdings = {}
            new_holdings['BTC'] = h[0] + c[0]
            new_holdings['ETH'] = h[1] + c[1]
            new_holdings['LTC'] = h[2] + c[2]
            
            new_holdings_val = self.convertHoldingsToUSD(new_holdings)
            
            new_holdings_rel = {}    
            new_holdings_rel['BTC'] = round(((h[0] + c[0])*self.b_price)/new_holdings_val, 3)
            new_holdings_rel['ETH'] = round(((h[1] + c[1])*self.e_price)/new_holdings_val, 3)
            new_holdings_rel['LTC'] = round(((h[2] + c[2])*self.l_price)/new_holdings_val, 3)
        
            return new_holdings, new_holdings_rel, new_holdings_val
        
        self.new_holdings, self.new_holdings_rel, self.new_holdings_val = setHoldings(h, c)

        def determine_earnings_ifyoucantradeintoUSD(predictedupORdwn, relative_predictions, findChanges):

            if predictedupORdwn == 1:  # buy into crypto
                cryptoToBuy = self.ifusd_USD_prev_val * amountToChange_portion
                cryptoToChange = (self.ifusd_crypto_prev_val -
                                  cryptoToBuy) * amountToChange_portion
                cryptoChanges = cryptoToChange + cryptoToBuy
                cryptoRemains = self.ifusd_crypto_prev_val - cryptoToChange

                self.ifusd_USD_new_val = self.ifusd_USD_prev_val - cryptoToBuy

                h = determinHoldover(
                    cryptoRemains, self.ifusd_crypto_prev, self.ifusd_crypto_prev_val)
                c = findChanges(relative_predictions, cryptoChanges)

                self.ifusd_crypto_new, self.ifusd_crypto_new_rel, self.ifusd_crypto_new_val = setHoldings(
                    h, c)

            else:  # sell out of crypto
                amountToSell = self.ifusd_crypto_prev_val * amountToChange_portion
                amountRemains = self.ifusd_crypto_prev_val - amountToSell
                amountToChange = amountRemains * amountToChange_portion
                amountNotToChange = amountRemains - amountToChange
                self.ifusd_USD_new_val = self.ifusd_USD_prev_val + amountToSell
                h = determinHoldover(
                    amountNotToChange, self.ifusd_crypto_prev, self.ifusd_crypto_prev_val)
                c = findChanges(relative_predictions, amountToChange)

                self.ifusd_crypto_new, self.ifusd_crypto_new_rel, self.ifusd_crypto_new_val = setHoldings(
                    h, c)

            self.ifusd_total_bal_new = self.ifusd_crypto_new_val + self.ifusd_USD_new_val

        determine_earnings_ifyoucantradeintoUSD(
            self.predictedupORdwn, relative_predictions, findChanges)
