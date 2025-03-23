from ipaddress import ip_address
import logging,datetime
import os,re,base64
import subprocess,time
import json
from benedict import benedict
import requests,platform
import time 
from utils.legacy_util_functions.crud_ops_client import HTTPBasicAuth
import datetime
import shortuuid
import string
from lensesio.lenses import main
import redis
import datetime
from time import time
from dotenv import load_dotenv
import dotenv
import socket ,random
from dateutil import tz
from datetime import datetime,date
from more_itertools import locate
from utils.legacy_util_functions.logger import Logger
from datetime import timedelta
from collections.abc import MutableMapping as mm
from collections.abc import Sequence as sq
import jsonpath_ng.ext as jp
import urllib.parse
import time
from kafka import KafkaConsumer
import json
from utils.legacy_util_functions.legacy_validation_checker import TestBaseClass as tb
from utils.legacy_util_functions.constants import card_details as card
from utils.legacy_util_functions.constants import addOnsData as addOnsData
import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)
current_dir_path = os.path.dirname(os.path.abspath(__file__))
parent_dir_path = os.path.abspath(os.path.join(current_dir_path, os.pardir))

def is_a_list(m):
    return isinstance(m, list)

def decorate_test(test_function):
    def wrapper():
        Logger.log_test_start(test_function)
        time_delta, _ = measure_time(test_function)
        Logger.log_test_finish(test_function, timedelta(seconds=time_delta))
    return wrapper

def measure_time(function):
    start = time()
    result = function()
    end = time()
    return end - start, result


def get_data_from_json_file(file_path, data_key=None):
    with open(file_path) as f:
        try:
            json_obj = json.load(f)
            f.close()
            if data_key is None:
                return json_obj
            else:
                return json_obj.get(data_key)
        except FileNotFoundError:
            print(f"File {file_path} not found.  Aborting")


def read_json_file(file_name):
    with open(file_name, "rb") as file_:
        try:
            contents = json.load(file_)
            return contents
        except FileNotFoundError:
            print(f"File {file_name} not found.  Aborting")
        
def read_file(file_name):
    with open(file_name) as file_:
        try: 
            contents = file_.read()
            return contents
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))

def backup_test_exec_response():
    if os.path.exists('/tmp/op/cmfs.json'):
        with open('/tmp/op/cmfs.json','r+') as firstfile, open('/tmp/op/cmfs_bkp.json','a+') as secondfile:
            try:
                for line in firstfile:
                    secondfile.write(line)
                secondfile.flush()
                secondfile.seek(0)
                firstfile.truncate(0)
            except ValueError():
                print("JSON decoding failed")

def log_command(command_list):
    return ' '.join(command_list)
#API Functions

def del_key(data, key):
    try:
        del data[key]
    except KeyError:
        pass
    return data

def call_with_retry(url, headers,max_tries=3):
    for i in range(max_tries):
        try:
            time.sleep(0.3) 
            resp=requests.get(url, headers=headers)
            return resp
        except Exception as e:
            print(str(e)+"retrying "+url+" "+str(i+1)+" time")
            continue

def get_ip_address():   
    ip = requests.get('https://api.ipify.org').content.decode('utf8') 
    return ip

def log_to_file(file_path,mode,data):
    file = open(file_path,mode)
    file.write(data)
    file.write("\n")
    file.close()

def find_word(text, search):
   result = re.findall('\\b'+search+'\\b', text, flags=re.IGNORECASE)
   if len(result)>0:
      return True
   else:
      return False

def decode_base_64_string(str_to_decode:str):
    decoded_str=base64.b64decode(str_to_decode)
    output_str = str(decoded_str, 'UTF-8')
    return output_str

def get_sec(time_str):
    """Get seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def day_today():
    today=str(date.today())
    spilted_data=today.split("-")
    final_format="".join(spilted_data)
    return final_format

def find_indices(list_to_check, item_to_find):
    indices = locate(list_to_check, lambda x: x == item_to_find)
    return list(indices)

def convert_to_list(string:str):
    converted=string.split("[")[1].split("]")[0].split(",")
    return converted

def get_microservices_uniqueName(l:list):
    uniqueList=[]
    for items in l:
        sublist=items.split("_")
        for i in sublist:
            uniqueList.append(i)
    return sorted(set(uniqueList), key=uniqueList.index)


def get_paths(source):
    paths = []
    if isinstance(source, mm):
        for k, v in source.items():  
            paths.append([k])  
            paths += [[k] + x for x in get_paths(v)]  
    elif isinstance(source, sq) and not isinstance(source, str):
        for i, v in enumerate(source):
            paths.append([i])
            paths += [[i] + x for x in get_paths(v)]
    return paths

def getCombinations(myList:list):
    combinationList=[]
    for i in  range(0,len(myList)-1):
        concatstr=(str(myList[i]),str(myList[i+1]))
        combinationList.append(concatstr)
    return combinationList

def transcodeStringIntoMap(string:str):
    alter_1=string.split("->")
    mapping={}
    for i in alter_1:
        l=i.split(":")
        key=l[0]
        value=l[1]
        if key not in mapping:
            mapping[key]=[value]
        else:
            mapping[key].append(value)
    return mapping

def convertlistitemstolower(itemlist:list):
    stringlist=[str(i).lower() for i in itemlist]
    return stringlist

def deleteFilesFromList(deleteList:list):
    for delpaths in deleteList:
        if os.path.exists(delpaths):
            os.remove(delpaths)
            logger.info("Successfully Deleted file ->"+str(delpaths))
        else:
            logger.error("File Not Found in the Given Path ->"+str(delpaths))
def evalExp(jsondata:dict,expression:str):
    results=[]
    query = jp.parse(expression)
    for match in query.find(jsondata):
        results.append(match.value)
    return results

def getDataFromFieldPathJsonPath(path:str,jsonMap:dict):
    try:
        data = benedict(jsonMap)
        value=data.get(path)
        return value
    except (Exception ,TypeError,ValueError) as error:
        logger.error("Json/Pydantic Path is Invalid, Error occured ->",error)
        return None

def find_indices(list_to_check, item_to_find):
    indices = locate(list_to_check, lambda x: x == item_to_find)
    return list(indices)

def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def fetchRouteIds(csvData,jsonresponse):
        print("csvData123",csvData)
        csvData["routeIds"] = {}
        print("csvData123",csvData)
        for route_id in jsonresponse:
            csvData["routeIds"][route_id] = jsonresponse[route_id]["BestOfferId"]
        print("csvData12",csvData) 

def fetchRedDealsFromCps(csvData,jsonresponse):
        csvData["redDealsData"] = {}
        print("len1",type(jsonresponse))
        for index,value in enumerate(jsonresponse):
            print("jsonresponse12",jsonresponse[index]['ID'])
            for key in csvData["routeIds"]:
                if csvData["routeIds"][key] == jsonresponse[index]['ID']:
                    csvData["redDealsData"][key] = {}
                    print("keysucess")
                    csvData["redDealsData"][key]['CampaignCode'] = jsonresponse[index]['campaignCode']
                    csvData["redDealsData"][key]['opID'] = jsonresponse[index]['opID']
                    csvData["redDealsData"][key]['CampaignType'] = jsonresponse[index]['campaignType']
                    csvData["redDealsData"][key]['countryName'] = jsonresponse[index]['countryName']
                    csvData["redDealsData"][key]['CampaignDesc'] = jsonresponse[index]['campaignDesc']
                    csvData["redDealsData"][key]['DiscountUnit'] = float(jsonresponse[index]['discountPercent'])
                    csvData["redDealsData"][key]['ID'] = jsonresponse[index]['ID']

def redDealValidationsSRP(responsedata,csvData,csvtestData,routeId,i):
        if csvData in ('CampaignCode','CampaignDesc','CampaignType','DiscountUnit'):
            #logger.info("csvData ->",csvtestData[1]["redDealsData"][str(routeId)][csvData])
            #logger.info("responsedata ->",responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0][csvData])
            if csvtestData[1]["redDealsData"][str(routeId)][csvData] == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0][csvData]:
                return True
            else:
                return False
        else:
            discount = csvtestData[1]["redDealsData"][str(routeId)]['DiscountUnit']
            for j in range(len(responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['OriginalPrices'])):
                originalPrice = responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['OriginalPrices'][j]
                discountedPrice = responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['DiscountedPrices'][j]
                discountAmount = float(f"{originalPrice * discount / 100:.2f}")
                onwardFare = responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['DiscountedPrices'][0]
                returnFare = responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['DiscountedPrices'][1]
                match csvData:
                    case 'Discount':
                        if discountAmount == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['Discount']:
                            return True
                        else: 
                            return False
                    case 'DiscountedPrices':
                        if (float(f"{originalPrice - discountAmount:.2f}")) == discountedPrice:
                            return True
                        else:
                            return False
                    case 'adultFee':
                        if onwardFare == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['ferryDiscFareLst'][0]['adultFee']:
                            csvtestData[1]["redDealsData"][str(routeId)]['adultFee'] = onwardFare
                            return True
                        else:
                            return False
                    case 'childFee':
                        if onwardFare == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['ferryDiscFareLst'][0]['childFee']:
                            csvtestData[1]["redDealsData"][str(routeId)]['childFee'] = onwardFare
                            return True
                        else:
                            return False
                    case 'rTripAdultFee':
                        if returnFare == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['ferryDiscFareLst'][0]['rTripAdultFee']:
                            csvtestData[1]["redDealsData"][str(routeId)]['rTripAdultFee'] = returnFare
                            return True
                        else:
                            return False
                    case 'rTripChildFee':
                        print("returnFare12",returnFare)
                        print("returnFare12",responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['ferryDiscFareLst'][0]['rTripChildFee'])
                        if returnFare == responsedata["inventories"][i]["operatorOfferCampaign"]["CmpgList"][0]['ferryDiscFareLst'][0]['rTripChildFee']:
                            csvtestData[1]["redDealsData"][str(routeId)]['rTripChildFee'] = returnFare
                            return True
                        else:
                            return False
def evalExp(jsondata:dict,expression:str):
    results=[]
    query = jp.parse(expression)
    for match in query.find(jsondata):
        results.append(match.value)
    return results

def update_token(headers, env):
    load_dotenv() 
    if ("os" in headers) or ("OS" in headers) or ("Os" in headers):
        key_name = str(headers['Country']).upper()+"_"+str(headers["Channel_Name"]).upper()+"_"+str(env).upper()+"_"+str(headers["os"]).upper()
    else:
        key_name = str(headers['Country']).upper()+"_"+str(headers["Channel_Name"]).upper()+"_"+str(env).upper()
    print("key_name12",key_name)
    return(os.getenv(key_name))

def queryParser(url:str,queryParams:dict):
        url_parts = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(url_parts.query,keep_blank_values=True))
        updated_query_params={**query, **queryParams}
        query.update(updated_query_params)
        url_parts = url_parts._replace(query=urllib.parse.urlencode(query))
        updated_url = urllib.parse.urlunparse(url_parts)
        updated_url = urllib.parse.unquote(updated_url)
        return updated_url

def generate_newNumber():
        random_number = random.randint(1, 10000)
        newNumber = "9999"+str(random_number)+"99"
        return newNumber

def convertDateFormat(value):
        dt = date.today()
        td = timedelta(days=int(value))
        doj=dt + td
        d = datetime.strptime(str(doj), '%Y-%m-%d')
        formatteddate=d.strftime('%d %B %Y')
        return str(formatteddate)


def generatemrisessionID():
    mrisessionID = "qatest-" + shortuuid.ShortUUID().random(length=29) + "_qatest-" + shortuuid.ShortUUID().random(length=29)
    return mrisessionID

def get_kafka_event_details(mrisessionID):
    # lenses_lib = main(
    #     auth_type="basic",
    #     url="####",
    #     username="####",
    #     password="#####"
    # )
    query = (
        '''USE kafka;
        SELECT * FROM lmb_ltr_logs_pp
        where _value.sessionId = '{mrisessionid}'
        and _meta.timestamp > NOW()-"5m"'''
    ).format(mrisessionid= mrisessionID)
    # result = lenses_lib.ExecSQL(query)
    # return result

def get_kafka_bat(mrisessionID):
    consumer = KafkaConsumer('global_non_transactional_prod',
                         bootstrap_servers=['mrilatamkafka4.redbus.com','mrilatamkafka5.redbus.com','mrilatamkafka6.redbus.com'],
                         auto_offset_reset='latest',
                         enable_auto_commit=True,
                         group_id='capi-automation')
    index = 0
    for message in consumer:
        index += 1
        logger.info(str(index))
        response = message.value.decode('utf-8')
        jsonResponse = json.loads(response)
        print("hello",jsonResponse)
        print(f"Offset: {message.offset}, Partition: {message.partition}, Key: {message.key},Timestamp:{message.timestamp}")
        print(jsonResponse)
        timestamp_s = message.timestamp / 1000
        # Convert to datetime
        readable_date = datetime.utcfromtimestamp(timestamp_s)
        print("readable_date",readable_date)
        MriSessionId = jsonResponse['requestHeaders'].get('MriSessionId') if not jsonResponse['requestHeaders'].get('MriSessionId') == None else jsonResponse['requestHeaders'].get('MRISessionId')
        logger.info(str(MriSessionId))
        if jsonResponse['requestHeaders'].get('MriSessionId') == mrisessionID or jsonResponse['requestHeaders'].get('MRISessionId') == mrisessionID:
            id = jsonResponse
            break
        if index == 100:
            break
    #print("count12",index)
    
    if id != None:
        return id
    return None

def get_kafka_event(mrisessionID):
    auth = HTTPBasicAuth('sudesh.shetty@redbus.com', 'shetty5993@#')
    baseUrl = 'http://kafka-ui-mum.redbus.com:8080/api/clusters/mrilatamkafka/topics/'
    topicName = 'glbl_non_transactional_prod'
    pathParams = 'messages'
    version = 'v2'
    queryParams = 'limit=100&mode=FROM_TIMESTAMP&timestamp=1722425280765'
  
    url = baseUrl + topicName +"/"+ pathParams +"/" +version +"?"+queryParams
    headers = {
        'cookie': 'SESSION=a8cc9f26-7afc-4325-bbcd-80240eaa26dd',
        'Accept': 'text/event-stream'  # Replace with actual authentication method
    }
    response = requests.get(url, headers=headers,stream=True)
    if response.encoding is None:
        response.encoding = "utf-8"
    text1 = ""     
    for line in response.iter_lines(decode_unicode=True):
        if not line == '':
            text1+=str(line)
            text1 = text1.split("data:")[1]
            res = json.loads(text1)
            if res['type'] == 'MESSAGE':
                kafkaResponse = res
                kafkaResponse = kafkaResponse['message']['content'].replace('/', '')
                kafkaResponse = json.loads(kafkaResponse)
    print("kafka-ui->",kafkaResponse)
    if kafkaResponse['requestHeaders']['MRISessionId']  == mrisessionID:
        return kafkaResponse
    else:
        logger.error("Mismatched!!")
    
def get_kafka_event_details_ltr(mrisessionID):
    time.sleep(5)
    lenses_lib = main(
         auth_type="basic",
         url="http://stream1.redbus.com:9991",
         username="dev1",
         password="redbusD3v123"
     )
    query = (
        '''USE kafka;
        SELECT * FROM lmb_ltr_logs
        where mriSessionId = '{mrisessionid}'
        and _meta.timestamp > NOW()-"30s" order by TIMESTAMP DESC LIMIT 1'''
    ).format(mrisessionid= mrisessionID)
    result = lenses_lib.ExecSQL(query)
    print("query ->",query)
    return result


def get_mri_event_details(mrisessionID):
    time.sleep(15)
    lenses_lib = main(
         auth_type="basic",
         url="http://stream1.redbus.com:9991",
         username="dev1",
         password="redbusD3v123"
     )
    query = (
        '''USE kafka;
          SELECT * FROM global_non_transactional_prod where _meta.timestamp > NOW()-"30s" AND requestHeaders.MriSessionId = '{mrisessionid}' '''
    ).format(mrisessionid= mrisessionID)
    result = lenses_lib.ExecSQL(query)
    result1 = result['data']
    # if len(result1)==0:
    #     result = get_mri_event_details1(mrisessionID)
    return result

def get_mri_event_details_latam(mrisessionID):
    print("consumer12")
    consumer = KafkaConsumer('glbal_non_transactional_prod',
                         bootstrap_servers=['stream1.redbus.com:9092'],
                         auto_offset_reset='latest',
                         enable_auto_commit=True,
                         group_id='capi-automation')
    cnt = 0
    for message in consumer:
        logger.info(message,"message12")
        cnt = cnt + 1
        response = message.value.decode('utf-8')
        jsonResponse = json.loads(response)
        if jsonResponse['requestHeaders']['MRISessionId'] == mrisessionID:
            return jsonResponse
        logger.info("count123",cnt)
        if cnt >5:
            break
    return jsonResponse

def get_mri_event_details_core(mrisessionID):
    time.sleep(5)
    lenses_lib = main(
         auth_type="basic",
         url="http://stream1.redbus.com:9991",
         username="dev1",
         password="redbusD3v123"
     )
    query = (
        '''USE kafka;
          SELECT * FROM glbl_non_transactional_prod where _meta.timestamp > NOW()-"30s" AND requestHeaders.MRISessionId = '{mrisessionid}' '''
    ).format(mrisessionid= mrisessionID)
    result = lenses_lib.ExecSQL(query)
    result1 = result['data']
    if len(result1)==0:
        result = get_mri_event_details1(mrisessionID)
    return result

def get_mri_event_details1(mrisessionID):
    time.sleep(5)
    lenses_lib = main(
         auth_type="basic",
         url="http://stream1.redbus.com:9991",
         username="dev1",
         password="redbusD3v123"
     )
    query = (
        '''USE kafka;
          SELECT * FROM glbl_non_transactional_prod where _meta.timestamp > NOW()-"30s" AND requestHeaders.MRISessionId = '{mrisessionid}' '''
    ).format(mrisessionid= mrisessionID)
    print("hello87",query)
    result = lenses_lib.ExecSQL(query)
   
    return result


def calculate_epoch_time():
    current_time = datetime.now()
    ten_minutes_ago = current_time - timedelta(minutes=10)
    current_time = int(current_time.timestamp())*1000000
    ten_minutes_ago_epoch_ts = int(ten_minutes_ago.timestamp() * 1000000)
    return ten_minutes_ago_epoch_ts, current_time

def get_redis_entry_AVS(key,dbid):
    connect = redis.StrictRedis(host="capi-lmb-ltr-ro.uuvkiu.ng.0001.aps1.cache.amazonaws.com", port=6379, db=dbid)
    start,end = calculate_epoch_time()
    redis_avs = connect.zrangebyscore(key,start,end)
    return redis_avs

def get_redis_entry_VC(key,dbid,mrisessionID):
    updated_sessionID = mrisessionID.split("_")[1]
    connect = redis.StrictRedis(host='capi-lmb-ltr-ro.uuvkiu.ng.0001.aps1.cache.amazonaws.com', port=6379, db=dbid)
    start,end = calculate_epoch_time()
    key = connect.zrangebyscore(key,start,end)
    for ids in key:
        optimized_key= str(ids).split("'")
        if str(optimized_key[1]) == updated_sessionID:
            return True
    return False

def get_redis_entry_LTR(key,dbid):
    connect = redis.StrictRedis(host="capi-lmb-ltr-ro.uuvkiu.ng.0001.aps1.cache.amazonaws.com", port=6379, db=dbid)
    start,end = calculate_epoch_time()
    count = 0
    for key1 in connect.scan_iter():
        if key1.decode("utf-8") == key:
            count = 1
            break
    if count == 0:
        return False
    else:
        return True

def getEnvBasedOnCountry(headers,scenarioName): 
    country = headers.get("Country")
    if scenarioName == 'profileRevampSocial':
        if country == "Malaysia":
            return (os.getenv("SOCIAL_SIGNIN_AUTH_MY"))
        elif country == "India":
            return (os.getenv("SOCIAL_SIGNIN_AUTH_IND"))
        elif country == "Cambodia":
            return (os.getenv("SOCIAL_SIGNIN_AUTH_KHM"))
        elif country == "Colombia":
            return (os.getenv("SOCIAL_SIGNIN_AUTH_COL"))
        elif country == "Peru":
            return (os.getenv("SOCIAL_SIGNIN_AUTH_PER"))
    else:
        if country == "Malaysia":
            return (os.getenv("SIGNIN_AUTH_MYS"))
        elif country == "India":
            return (os.getenv("SIGNIN_AUTH_IND"))
        elif country == "Cambodia":
            return (os.getenv("SIGNIN_AUTH_KHM"))
        elif country == "Colombia":
            return (os.getenv("SIGNIN_AUTH_COL"))
        elif country == "Peru":
            return (os.getenv("SIGNIN_AUTH_PER"))
    return (os.getenv("SIGNIN_AUTH_SGMY"))
def get_auth_token(Channel_Name,mobile_number):
    key = Channel_Name+"_"+mobile_number
    print("hey12",key)
    return os.getenv(key)
def set_auth_token(Channel_Name,csvtestData,response):
    dotenv_file = ".env"
    dotenv.load_dotenv(dotenv_file)
    keyname = Channel_Name+"_"+csvtestData['mobileNumber']
    os.environ[keyname] = dict(response.headers).get('AuthToken')
    dotenv.set_key(dotenv_file, keyname, os.environ[keyname])
def get_csv_data(apiData={}):
    csvData = {}
    for key,value in apiData.items():
        if not(key.startswith('env') or key.lower() in('modelname','responsestatus','readrow')):
            csvData[key] = value
    return csvData
def get_geo(Country_Name):
    if Country_Name in ('MYS','SGP','KHM','VNM','IDN'):
        GEO  = 'SEA'
    elif Country_Name in ('PE','CO'):
        GEO = 'LATAM'
    else:
        GEO = 'INDIA'
    return GEO
def do_form_post():
    #service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
    ) 
    try:
        # Open the local HTML form page
        form_post_path = 'Automation_Form_Post.html' 
        driver.get("file:///"+os.getcwd() +"/" +form_post_path)
        driver.maximize_window()  
        time.sleep(5)      
        # Click the payment button
        driver.find_element("name", "make_payment").click()
        time.sleep(20)
        current_url = driver.current_url
        print("current_url",current_url)
        modified_url = current_url.replace('m.redbus.my','www.redbus.my')
        print("modified_url12",modified_url)
        driver.get(modified_url)
        tin = '' if "activities" in modified_url else modified_url.split("tin=")[1].split("&")[0]
        return tin
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the browser
        driver.close()
    return "null"
def getHTMLFIle(data):
    try:
        # Writing to the file
        with open(data['file_path'], 'w') as bw:
            bw.write("<!DOCTYPE html>\n")
            bw.write("<html>\n")
            bw.write("<head>\n</head>\n")
            bw.write("<body>\n")
            bw.write(f"<form id='redbus_payment_form' action='{data['PaymentUrl']}' method='POST'>\n")
            bw.write(f"<input type='hidden' name='token' value='{data['token']}'>\n")
            bw.write(f"<input type='hidden' name='order_id' value='{data['orderUUid']}'>\n")
            bw.write(f"<input type='hidden' name='amount' value='{data['PIAmt']}'>\n")
            bw.write(f"<input type='hidden' name='currency' value='{data['PICurr']}'>\n")
            bw.write(f"<input type='hidden' name='PgTypeId' value='{data['PgTypeId']}'>\n")
            bw.write(f"<input type='hidden' name='card_number' value='{card.card_number.value}'>\n")
            bw.write(f"<input type='hidden' name='name_on_card' value='{card.name.value}'>\n")
            bw.write(f"<input type='hidden' name='card_exp_month' value='{card.card_exp_month.value}'>\n")
            bw.write(f"<input type='hidden' name='card_exp_year' value='{card.card_exp_year.value}'>\n")
            bw.write(f"<input type='hidden' name='security_code' value='{card.security_code.value}'>\n")
            bw.write(f"<input type='hidden' name='first_name' value='{card.first_name.value}'>\n")
            bw.write(f"<input type='hidden' name='last_name' value='{card.last_name.value}'>\n")
            bw.write(f"<input type='hidden' name='email' value='{card.email.value}'>\n")
            bw.write(f"<input type='hidden' name='phone' value='{card.phone.value}'>\n")
            bw.write(f"<input type='hidden' name='bank_id' value='{card.bank_id.value}'>\n")
            bw.write(f"<input type='hidden' name='bank_code' value='{card.bank_code.value}'>\n")
            bw.write(f"<input type='hidden' name='offer_key' value='{card.offer_key.value}'>\n")
            bw.write(f"<input type='hidden' name='DeviceSessionId' value='{card.DeviceSessionId.value}'>\n")
            bw.write(f"<input type='hidden' name='Cookie' value='{card.Cookie.value}'>\n")
            bw.write(f"<input type='hidden' name='PaymentMethod' value='{card.PaymentMethod.value}'>\n")
            bw.write(f"<input type='hidden' name='UserAgent' value='Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'>\n")
            bw.write(f"<input type='hidden' name='Language' value='{card.Language.value}'>\n")
            bw.write("<button type='submit' name='make_payment'>Pay</button>\n")
            bw.write("</form>\n")
            bw.write("</body>\n")
            bw.write("</html>\n")
        print("Form generated...")
    except IOError as e:
        print(f"Error writing to file: {e}")
def getOStype():
    return platform.system()
def open_browser():
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # For Mac
    url = "/Users/ashton.c/Documents/LTR/rb-capi-api-automation/Automation_Form_Post.html"
    subprocess.run([chrome_path, url])
    time.sleep(20)
    return "tin"


def doConfirmBooking(Response,csvData,payload):
    data = {}
    #PaymentUrl = "https://origin-payment.redbus.in/payment/ProcessPayment/co/MYS?token=3ecefae4306ab0bc88f1ab1b137fe7e3"
    data['PaymentUrl'] = Response['PaymentUrl'].split("?")[0]
    data['token'] = Response['PaymentUrl'].split("token=")[1]
    data['PaymentUrl'] = data['PaymentUrl']+"?token="+data['token']
    data['PICurr'] = Response['PICurr']
    data['PIAmt'] = Response['PIAmt']
    data['orderUUid'] = csvData['OrderUUId']
    data['PgTypeId'] = payload['PgType']
    data['file_path'] = os.getcwd()+ "/Automation_Form_Post.html"
    getHTMLFIle(data)
    if getOStype().lower() not in ['darwin','linux']:
        tin = do_form_post()
    else:
        tin = open_browser()
    return tin      
if __name__ =='__main__':
    v='routes:sheet_1->seatLayout:sheet_1->routes:sheet_1'
    transcodeStringIntoMap(v)