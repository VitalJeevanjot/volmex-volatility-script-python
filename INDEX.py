from math import sqrt, exp, log, pi
from scipy.stats import norm

print("Start of new script...")


# import asyncio
# import websockets
import json
import time
import traceback
from datetime import datetime, timedelta
import schedule

# firebase imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# connection requests
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# web3 call
import os
print(os.getenv("INFURA_NODE"))

from web3 import Web3, HTTPProvider

# load environment variables
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
env_path = Path('/root/monit/volmex') / '.env'
load_dotenv(dotenv_path=env_path)

contract_address     = '0xc74F9B12b972547817843322004Bd789d74f935e'
wallet_private_key   = os.getenv("PRIVATE_KEY")
wallet_address       = os.getenv("ETH_ADDRESS")

chainid = 3 #'testnet' CHANGE In future for different net

w3 = Web3(HTTPProvider(os.getenv("INFURA_NODE")))

print(os.getenv("INFURA_NODE"))
# w3.eth.enable_unaudited_features()
print(w3.isConnected())
print(w3.eth.blockNumber)
def publish_evix_on_chain():
    nonce = w3.eth.getTransactionCount(wallet_address, 'pending')
    with open('contract_abi.json') as f:
        abi = json.load(f)

    evix_contract = w3.eth.contract(
        address=contract_address,
        abi=abi
    )
    # print(wallet_address)
    # print(os.getenv("INFURA_NODE"))
    # acct = w3.eth.account.privateKeyToAccount(wallet_private_key)
    # evix_contract.functions.requestEVIX("https://volmex-labs.firebaseio.com/current_evix/evix.json").estimateGas({'from': acct.address})
    transaction = evix_contract.functions.requestEVIX("https://volmex-labs.firebaseio.com/current_evix/evix.json").buildTransaction({
         'chainId': chainid,
         'gas': 1600000,
         'gasPrice': w3.toWei('50', 'gwei'),
         'nonce': nonce,
     })
    # transaction.update({ 'gas' : 8000000 })
    # transaction.update({ 'gasPrice': w3.toWei('50', 'gwei') })
    # transaction.update({ 'nonce' : nonce })

    #signed_tx = w3.eth.account.sign_transaction(transaction, private_key=wallet_private_key)
    #print(signed_tx.hash)
    #print(signed_tx.rawTransaction)
    #print(signed_tx.r)
    #print(signed_tx.s)
    #print(signed_tx.v)
    #w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    

# web3 call end
session = requests.Session()
retry = Retry(connect=100, backoff_factor=0.1)
adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_block=False)
session.mount('http://', adapter)
session.mount('https://', adapter)

# firebase initializations
cred = credentials.Certificate('./test-volmex-ethv-firebase-adminsdk-6uqqs-1aa7eea52a.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://test-volmex-ethv-default-rtdb.firebaseio.com'
})


# other initializations

currency = 'ETH'

thirty_days = 2592000000 # 30 days in milli
current_time = None

EVIXC = None
EVIXP = None
_res_price = None
_r_c_in_usd = 0
_r_p_in_usd = 0


def runScript(mS, sK, et, c0, _K, p0):
    def d(sigma, S, K, r, t):
        d1 = 1 / (sigma * sqrt(t)) * (log(S/K) + (r + sigma**2/2) * t)
        d2 = d1 - sigma * sqrt(t)
        return d1, d2


    def call_price(sigma, S, K, r, t, d1, d2):
        C = norm.cdf(d1) * S - norm.cdf(d2) * K * exp(-r * t)
        return C
    print('mS ' + str(mS))
    print('sK ' + str(sK))
    print('et ' + str(round(et/365,2)))
    print('c0 ' + str(c0))
    print('_K ' + str(_K))
    print('p0 ' + str(p0))
    S = mS
    K = sK
    t = round(et/365,2)
    r = 0.01
    c0 = c0
    # S = 285.22
    # K = 280
    # t = 34.5 / 365.0
    # r = 0.00
    # c0 = 26.24484

    #  Tolerances
    tol = 1e-3
    epsilon = 1

    count = 0
    max_iter = 1000

    vol = 0.50

    while epsilon > tol:
        count += 1
        if count >= max_iter:
            print('Breaking on count')
            break

        orig_vol = vol

        d1, d2 = d(vol, S, K, r, t)
        # print(vol)
        function_value = call_price(vol, S, K, r, t, d1, d2) - c0
        vega = S * norm.pdf(d1) * sqrt(t)
        vol = -function_value / vega + vol

        epsilon = abs((vol - orig_vol) / orig_vol)

    x = t * 365

    Y = x / 30 
    global EVIXC 
    EVIXC = ((vol / Y))*100

    #  Print out the results
    print('\nFor Call')
    print('Sigma = ', vol)
    print('EVIXC = ', EVIXC)
    print('Code took ', count, ' iterations')


    # put 'CODE'

    #   Function to calculate the values of 21 and d2 as well as the call
    #   price.  To extend to puts, one could just add a function that
    #   calculates the put price, or combine calls and puts into a single
    #   function that takes an argument specifying which type of contract one
    #   is dealing with.

    def put_price(sigma, S, K, r, t, d1, d2):
        P = -norm.cdf(-d1) * S + norm.cdf(-d2) * K * exp(-r * t)
        return P


    #  Option parameters
    S = mS
    K = _K
    t = round(et/365,2)
    r = 0.01
    P0 = p0



    #  Tolerances
    tol = 1e-3
    epsilon = 1

    #  Variables to log and manage number of iterations
    count = 0
    max_iter = 1000

    #  We need to provide an initial guess for the root of our function
    vol = 0.50

    while epsilon > tol:
        #  Count how many iterations and make sure while loop doesn't run away
        count += 1
        if count >= max_iter:
            print('Breaking on count')
            break;

        #  Log the value previously calculated to computer percent change
        #  between iterations
        orig_vol = vol

        #  Calculate the vale of the call price
        d1, d2 = d(vol, S, K, r, t)
        function_value = put_price(vol, S, K, r, t, d1, d2) - P0

        #  Calculate vega, the derivative of the price with respect to
        #  volatility
        vega = S * norm.pdf(d1) * sqrt(t)

        #  Update for value of the volatility
        vol = -function_value / vega + vol

        #  Check the percent change between current and last iteration
        epsilon = abs( (vol - orig_vol) / orig_vol )

        
    x = t * 365

    Y = x / 30 

    global EVIXP 
    EVIXP = ((vol / Y))*100

    #  Print out the results
    print('\nFor Put')
    print('Sigma = ', vol)
    print('EVIXP = ', EVIXP)
    print('CODE took ', count, ' iterations')


    # --

    # FINAL CALC

    # EVIX = (EVIXP + EVIXC)/2


# calling api
def get_current_index ():
    r_price = None
    try:
        r_price = session.get('https://www.deribit.com/api/v2/public/get_index', params = {"currency": currency})
    except:
        print('Request #2 error')
    global _res_price
    _res_price = r_price.json()["result"]

def call_api():
    global current_time
    current_time = int(time.time()) * 1000 # in milli
    can_expire_in = current_time + thirty_days
    r = None # declared outside variables so if try body not works still the variable should be considered declared and below did same... (which might not be necessary with good fixes)
    try:
        r = session.get('https://www.deribit.com/api/v2/public/get_instruments', params = {"currency": currency, "kind": "option", "expired": 'false'})
    except:
        print('Request #1 error')
    res = r.json()
    _res = res["result"]
    sort = sorted(_res, key=lambda x: x["expiration_timestamp"]) # sorted by expiration date
    
    related_obj = min(sort, key=lambda x:abs(x["expiration_timestamp"]-can_expire_in)) # nearest object on 30 day option contract from now
    # print(related_obj["expiration_timestamp"]) # timestamp found
    required_objects = list(filter(lambda x: x["expiration_timestamp"] == related_obj["expiration_timestamp"], sort)) # all objects from array with required expiration date
    # print(json.dumps(required_objects, indent=4, sort_keys=True))

    # get current price
    get_current_index()
    print('Current Market Price of ' + currency + ' is ' + str(_res_price[currency]))
    
    highest_call = max(filter(lambda el: el["strike"] < _res_price[currency], required_objects), key = lambda el: el["strike"])
    lowest_put = min(filter(lambda el: el["strike"] > _res_price[currency], required_objects), key = lambda el: el["strike"])
    print(json.dumps(highest_call, indent=4, sort_keys=True))
    # print(json.dumps(lowest_put, indent=4, sort_keys=True))
    expires_in = round((highest_call["expiration_timestamp"] - current_time)/(1000*60*60*24), 2)
    # expires_in_p = round((lowest_put["expiration_timestamp"] - current_time)/(1000*60*60*24), 2) Expiry date will be same
    
    get_last_value_call = None
    get_last_value_call_2 = None
    try:
        get_last_value_call = session.get('https://www.deribit.com/api/v2/public/get_book_summary_by_instrument', params = {"instrument_name": highest_call["instrument_name"][:-1]+'C'})
        get_last_value_call_2 = session.get('https://www.deribit.com/api/v2/public/get_book_summary_by_instrument', params = {"instrument_name": lowest_put["instrument_name"][:-1]+'C'})
    except:
        print('Request #3 error')
    
    get_last_value_put = None
    get_last_value_put_2 = None
    try:
        get_last_value_put = session.get('https://www.deribit.com/api/v2/public/get_book_summary_by_instrument', params = {"instrument_name": lowest_put["instrument_name"][:-1]+'P'})
        get_last_value_put_2 = session.get('https://www.deribit.com/api/v2/public/get_book_summary_by_instrument', params = {"instrument_name": highest_call["instrument_name"][:-1]+'P'})
    except:
        print('Request #4 error')
    _r_c = get_last_value_call.json()["result"]
    _r_c_2 = get_last_value_call_2.json()["result"]
    _r_p = get_last_value_put.json()["result"]
    _r_p_2 = get_last_value_put_2.json()["result"]
    print("All calls and puts on deribit, Firs call, 2nd call, First put, 2nd put")
    print(_r_c)
    print(_r_c_2)
    print(_r_p)
    print(_r_p_2)
    # print(_r_c[0])
    # print(_r_p[0])
    if _r_c[0]["mark_price"] != None and _r_c_2[0]["mark_price"] != None:
        global _r_c_in_usd
        _r_c_in_usd = round((((_r_c[0]["mark_price"] * _res_price[currency]) + (_r_c_2[0]["mark_price"] * _res_price[currency])) / 2), 2)
        print("Calls Average of two data points C0")
        print(_r_c_in_usd)
        print(_r_c[0]["mark_price"] )
        print(_r_c_2[0]["mark_price"])

    if _r_p[0]["mark_price"] != None and _r_p_2[0]["mark_price"] != None:
        global _r_p_in_usd
        _r_p_in_usd = round((((_r_p[0]["mark_price"] * _res_price[currency]) + (_r_p_2[0]["mark_price"] * _res_price[currency])) / 2), 2)
        print("Puts Average of two data points P0")
        print(_r_p_in_usd)
        print(_r_p[0]["mark_price"] )
        print(_r_p_2[0]["mark_price"])
    # print(json.dumps(round(_r_c[0]["last"] * _res_price[currency], 2), indent=4, sort_keys=True))
    # print(json.dumps(round(_r_p[0]["last"] * _res_price[currency], 2), indent=4, sort_keys=True))
    runScript(_res_price[currency], highest_call["strike"], expires_in, _r_c_in_usd, lowest_put["strike"], _r_p_in_usd)
    # print(res["result"])
    # print(json.dumps(sort, indent=4, sort_keys=True))



def init_point_evix_24():
        
    # firebase logic
    call_api()
    ref_e = db.reference('/evix/24h')
    
    db_push_evix = ref_e.child(str(current_time)).set({
                'evix': (EVIXC + EVIXP)/2,
                'evixc': EVIXC,
                'evixp': EVIXP,
                'timeStamp': str(current_time)
            })
    
    ref_e = db.reference('/evix/24h/' + str(current_time))
    
    # ref.push()
    # print(ref_e.get())

def init_point_evix_1w():
        
    # firebase logic
    call_api()
    ref_e = db.reference('/evix/1w')
    
    db_push_evix = ref_e.child(str(current_time)).set({
                'evix': (EVIXC + EVIXP)/2,
                'evixc': EVIXC,
                'evixp': EVIXP,
                'timeStamp': str(current_time)
    })
    
    # data_key_i = db_push_index.key
    ref_e = db.reference('/evix/1w/' + str(current_time))
    
    # ref.push()
    # print(ref_e.get())

def init_point_evix_1m():
        
    # firebase logic
    call_api()
    ref_e = db.reference('/evix/1mon')
    
    db_push_evix = ref_e.child(str(current_time)).set({
                'evix': (EVIXC + EVIXP)/2,
                'evixc': EVIXC,
                'evixp': EVIXP,
                'timeStamp': str(current_time)
           
    })
    
    # data_key_i = db_push_index.key
    ref_e = db.reference('/evix/1mon/' + str(current_time))
    
    # ref.push()
    # print(ref_e.get())

def current_evix_Price():
        
    # firebase logic
    call_api()
    ref_e = db.reference('/current_evix')
    
    print("------------------------------------------------")
    print(EVIXC)
    print(EVIXP)
    db_push_evix = ref_e.set({                 
                'evix': (EVIXC + EVIXP)/2,
                'evixc': EVIXC,
                'evixp': EVIXP,
                'timeStamp': str(current_time)
    })
    
    # data_key_i = db_push_index.key
    ref_e = db.reference('/current_evix/')
    
    # ref.push()
    # print(ref_e.get())



def init_point_index():
    get_current_index()
    ref_i = db.reference('/index_price')
    db_push_index = ref_i.set({
                'current_index_price': _res_price[currency],
                'timeStamp': str(current_time)
            })
    ref_i = db.reference('/index_price/')
    # print(ref_i.get())


# init_point_evix_24()
# init_point_evix_1w()
# init_point_evix_1m()
# publish_evix_on_chain()
# schedule.every(30).minutes.do(publish_evix_on_chain)
schedule.every(30).minutes.do(init_point_evix_24)
schedule.every(3.5).hours.do(init_point_evix_1w)
schedule.every(15).hours.do(init_point_evix_1m)
schedule.every(3).seconds.do(init_point_index)
schedule.every(20).seconds.do(current_evix_Price)

while True:
    schedule.run_pending()
    time.sleep(1)
