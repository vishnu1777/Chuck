import utils.legacy_util_functions.commons as cmn
import time,re,math,pygsheets
from utils.legacy_util_functions.legacy_validation_checker import logging as log
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from utils.legacy_util_functions.dbConnectionUtils import dbUtils as dbU
from utils.legacy_util_functions.legacy_validation_checker import TestBaseClass as tb
import pytest_check as check
from utils.legacy_util_functions.crud_ops_client import requestClient as rq
import json
from utils.legacy_util_functions.request_builder import RequestBuilder as apicall
from utils.legacy_util_functions.constants import addOnsData as addOnsData
import utils.legacy_util_functions.customFunctions   as customFunction

load_dotenv()
objdbU = dbU()
def getsuffix(days):
    if days in (3,23):
        suffix = "rd"
    elif days in (2,22):
        suffix = "nd"
    elif days in(1,21,31):
        suffix = "st"
    else:
        suffix = "th"
    return suffix
def formatAmount(walletCoreUsable):
    if walletCoreUsable % 1 == 0:
        return int(walletCoreUsable)
    else:
        return walletCoreUsable
def convert_month_str(month):
    match month:
        case '01':
            month = 'Jan'
        case '02':
            month = 'Feb'
        case '03':
            month = 'Mar'
        case '04':
            month = 'Apr'
        case '05':
            month = 'May'
        case '06':
            month = 'Jun'
        case '07':
            month = 'Jul'
        case '08':
            month = 'Aug'
        case '09':
            month = 'Sep'
        case '10':
            month = 'Oct'
        case '11':
            month = 'Nov'
        case '12':
            month = 'Dec'
    return month
def authValidations(dbResult,FLAG,csvData):
    dbResult = list(dbResult)
    for index,value in enumerate(dbResult):
        dbResult[index] = 'None' if value == None else value
    dbResult = None if dbResult == 'None' else dbResult
    if not dbResult[4] == csvData['ChannelName']:
        FLAG = False
        tb.logError(tb,"Channel->",dbResult[4]) 
        tb.logError(tb,"Channel->",csvData['ChannelName']) 
    if not dbResult[5] == csvData['DeviceOS']:
        FLAG = False
        tb.logError(tb,"DeviceOS->",dbResult[5])
        tb.logError(tb,"DeviceOS->",csvData['DeviceOS']) 
    if not str(dbResult[11]) == csvData['userId']:
        FLAG = False
        tb.logError(tb,"UserID->",dbResult[11]) 
        tb.logError(tb,"DeviceOS->",csvData['userId'])
    if not dbResult[12] == csvData['deviceId']:
        FLAG = False
        tb.logError(tb,"DeviceID->",dbResult[12])
        tb.logError(tb,"DeviceID->",csvData['deviceId'])
    return FLAG
def checkPeakDOJ(jsonResponse):
    baording_date =  jsonResponse['data'][0]['date']
    baording_date = datetime.strptime(baording_date, "%Y-%m-%d").date()
    flag = False
    for period in jsonResponse['data'][0]['dojDynamicPremium']:
        start_date = datetime.strptime(period["startDate"], "%Y-%m-%d").date()
        end_date = datetime.strptime(period["endDate"], "%Y-%m-%d").date()
        if start_date < baording_date < end_date:
            flag = True
    if flag:
        return True
    else:
        return False
def getDiscountPercentage(time_difference,country,jsonResponse):
    match country:
        case 'sgmy_addons':
            if checkPeakDOJ(jsonResponse):
                discountPercentage = addOnsData.discount_Percentage_rg_168_0.value
            else:
                if time_difference <= timedelta(hours=72):
                    discountPercentage = addOnsData.discount_Percentage_rg_2_48.value
                elif time_difference <= timedelta(hours=168):
                    discountPercentage = addOnsData.discount_Percentage_rg_48_168.value
                else:
                    discountPercentage = addOnsData.discount_Percentage_rg_168_0.value
            return discountPercentage
        case 'india':
            if time_difference <= timedelta(hours=24):
                discountPercentage = addOnsData.discount_Percentage_rg_india_0_24.value
            elif time_difference <= timedelta(hours=48):
                discountPercentage = addOnsData.discount_Percentage_rg_india_24_48.value
            elif time_difference <= timedelta(hours=72):
                discountPercentage = addOnsData.discount_Percentage_rg_india_48_72.value
            else:
                discountPercentage = addOnsData.discount_Percentage_rg_india_72_0.value
            return discountPercentage
        case 'idn':
            discountPercentage = addOnsData.discount_Percentage_rg_idn.value
            return discountPercentage
def getPrice(seatPrice,discountPercentage,country):
    match country:
        case 'sgmy_addons':
            mrp = float(seatPrice) * float(discountPercentage) / 100
            return mrp
        case 'india':
            mrp = float(seatPrice) * float(discountPercentage)
            if len(str(int(float(seatPrice)))) <3:
                mrp = mrp/100
            elif len(str(int(float(seatPrice)))) <5:
                mrp = mrp/1000
            elif len(str(int(float(seatPrice)))) == 4:
                mrp = mrp/10000
            if math.modf(mrp)[0] < 0.5:
                mrp = math.floor(mrp)*10
            else:
                mrp = math.ceil(mrp)*10
            return mrp
        case 'idn':
            mrp = float(seatPrice) * float(discountPercentage) / 100
            mrp = math.ceil(mrp / 1000) * 1000
            return mrp      
def convert_time_zone(date_str, dep_offset_str, arr_offset_str):
    naive_datetime = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    dep_sign = 1 if dep_offset_str[3] == '+' else -1
    arr_sign = 1 if arr_offset_str[3] == '+' else -1
    dep_hours_offset = dep_sign * int(dep_offset_str[4:6])
    dep_minutes_offset = dep_sign * int(dep_offset_str[7:9])
    arr_hours_offset = arr_sign * int(arr_offset_str[4:6])
    arr_minutes_offset = arr_sign * int(arr_offset_str[7:9])
    dep_offset = timedelta(hours=dep_hours_offset, minutes=dep_minutes_offset)
    arr_offset = timedelta(hours=arr_hours_offset, minutes=arr_minutes_offset)
    dep_tz = timezone(dep_offset)
    dep_datetime = naive_datetime.replace(tzinfo=dep_tz)
    arr_tz = timezone(arr_offset)
    arr_datetime = dep_datetime.astimezone(arr_tz)
    return arr_datetime.strftime('%Y-%m-%d %H:%M:%S')
def getRealTimeUpdate(RouteId,doj,country=''):
    endpoint = 'http://omega-latam-public.redbus.com:8001/' if country == 'latam' else "http://10.5.30.215:8001/"
    pathparams = 'IASPublic/getRouteDetailsObject/'+RouteId+'/'+doj
    requestURL = endpoint + pathparams
    try:
        response,resp_time = rq.request(rq,request_type="get",url=requestURL,headers={},payload_data={})
    except Exception as e:
        tb.logInfo(tb,"omega requestURL->",requestURL)
        tb.logInfo(tb,"omega api timeout->",e)
                
    response = json.loads(response.text)
    tb.logInfo(tb,"omega requestURL->",requestURL)
    tb.logInfo(tb,"omega response->",response)
    return response
def getRouteDetailsObject(RouteId,doj):
    endpoint = 'http://10.5.30.215:8001/'
    pathparams = 'IASPublic/getRouteDetailsObject/'+RouteId+'/'+doj
    requestURL = endpoint + pathparams
    try:
        response,resp_time = rq.request(rq,request_type="get",url=requestURL,headers={},payload_data={})
    except Exception as e:
        tb.logInfo(tb,"omega requestURL->",requestURL)
        tb.logInfo(tb,"omega api timeout->",e)
                
    response = json.loads(response.text)
    tb.logInfo(tb,"omega requestURL->",requestURL)
    tb.logInfo(tb,"omega response->",response)
    return response
def getcheckCancelPolicyError(res1,res2):
    if not res1[0]['startDateTime'] == res2[0]['startDateTime']:
        time_format = '%d-%m-%Y %H:%M:%S'
        dt1 = datetime.strptime(res1[0]['startDateTime'], time_format)
        dt2 = datetime.strptime(res2[0]['startDateTime'], time_format)
        time_difference = abs((dt1 - dt2).total_seconds())
        if time_difference == 1:
            return True
        else:
            tb.logError(tb,res1[0]['startDateTime'], res2[0]['startDateTime'])
    for i in range(0,len(res1)):
        if not res1[i]['cancellationString'] == res2[i]['cancellationString']:
            tb.logError(tb,res1[i]['cancellationString'],res2[i]['cancellationString'])
        if not res1[i]['chargeExact'] == res2[i]['chargeExact']:
            tb.logError(tb,res1[i]['chargeExact'],res2[i]['chargeExact'])
        if not res1[i]['chargePerc'] == res2[i]['chargePerc']:
            tb.logError(tb,res1[i]['chargePerc'],res2[i]['chargePerc'])
        if not res1[i]['refundableAmount'] == res2[i]['refundableAmount']:
            tb.logError(tb,res1[i]['refundableAmount'],res2[i]['refundableAmount'])
        if not res1[i]['currentSlot'] == res2[i]['currentSlot']:
            tb.logError(tb,res1[i]['currentSlot'], res2[i]['currentSlot'])
        if not res1[i]['endDateTime'] == res2[i]['endDateTime']:
            tb.logError(tb,res1[i]['endDateTime'], res2[i]['endDateTime'])
        if not res1[i]['startDateTime'] == res2[i]['startDateTime']:
            tb.logError(tb,res1[i]['startDateTime'], res2[i]['startDateTime'])
def getcheckCancelPolicyErrorTTD(res1,res2):
    for i in range(0,len(res1)):
        if not res1[i]['type'] == res2[i]['type']:
            tb.logError(tb,res1[i]['type'],res2[i]['type'])
        if not res1[i]['timeString'] == res2[i]['timeString']:
            tb.logError(tb,res1[i]['timeString'],res2[i]['timeString'])
        if not res1[i]['chargePerc'] == res2[i]['chargePerc']:
            tb.logError(tb,res1[i]['hours'],res2[i]['hours'])
        if not res1[i]['hours'] == res2[i]['hours']:
            tb.logError(tb,res1[i]['hours'],res2[i]['hours'])
        if not res1[i]['charges'] == res2[i]['charges']:
            tb.logError(tb,res1[i]['charges'], res2[i]['charges'])
        if not res1[i]['chargeString'] == res2[i]['chargeString']:
            tb.logError(tb,res1[i]['chargeString'], res2[i]['chargeString'])
def getCancelPolicyJson(policy):
    cancelPolicy = []
    for i in range(0,len(policy)):
        timeString = str(policy[i].split(":")[0]) + " hours"
        hours = str(policy[i].split(":")[0])
        charges = str(policy[i].split(":")[2])
        chargeString = str(policy[i].split(":")[2]) + "%"
        dict = {
            "type" : 1,
            "timeString": timeString,
            "hours": hours,
            "charges": charges,
            "chargeString": chargeString
        }
        cancelPolicy.append(dict)
    return cancelPolicy
def check_time_difference(given_time_str):
    given_time = datetime.strptime(given_time_str, "%d-%m-%Y %H:%M:%S")    
    current_time = datetime.now()    
    time_difference = abs((given_time - current_time).total_seconds())  
    return time_difference > 1
def get_round_off_price(totalFare):
    totalFare = round(totalFare,2)
    return f"{totalFare:.2f}".rstrip('0').rstrip('.')
def validate(csvData,index,dynamicValidationKey,results):
    tb.logInfo(tb,"csvData->",csvData[index].get(dynamicValidationKey)) 
    if results == 'null':
        results = [str(None)]
    tb.logInfo(tb,"response->",results[0])
    try:
        return float(csvData[index].get(dynamicValidationKey)) == float(results[0])
    except:
        try:
            if csvData[index].get(dynamicValidationKey) in ("True","False"):
                return bool(csvData[index].get(dynamicValidationKey)) == results[0]
            else:
                res = csvData[index].get(dynamicValidationKey) == results[0]
                if res == False:
                    #check if string is not rounded off eg: 2.0 MYR == 2 MYR
                    formatted = re.sub(r'(\d+)\.0', r'\1', csvData[index].get(dynamicValidationKey))
                    formatted = re.sub(r'\s*([A-Z]{3})', r' \1', formatted)
                    formatted.strip()
                    if formatted == results[0]:
                        return True
                    tb.logInfo(tb,"formatted->",formatted)
                return res
        except:
            return False
def getIndiaRGIndex(jsonResponse,csvData,index):
    if csvData[index]['addOnsName'] == "RG": 
        for i in range(0,len(jsonResponse['data'])):
            if jsonResponse['data'][i]['uuid'] == 'fb6c00ce-b096-49b6-82f0-cea366f82d24':
                index = i
                return index
    elif csvData[index]['addOnsName'] == "RAP":
        for i in range(0,len(jsonResponse['data'])):
            if jsonResponse['data'][i]['uuid'] == '8615b412-3d9a-404b-a06c-76d5f508322a':
                index = i
                return index
def getSgmyRGIndex(jsonResponse,csvData,index):
    if csvData[index]['addOnsName'] == "RG":
        for i in range(0,len(jsonResponse['data'])):
            if jsonResponse['data'][i]['uuid'] == '12345-3d9a-404b-a06c-76d5f508322a':
                index = i
                return index
def getIDNRGIndex(jsonResponse,csvData,index):
    if csvData[index]['addOnsName'] == "RG":
        for i in range(0,len(jsonResponse['data'])):
            if jsonResponse['data'][i]['uuid'] == '7829810-3d9a-404b-a06c-76d5f508322a':
                index = i
                return index
def getCancelPolicy(csvData,index,jsonResponse):
    Date = csvData[index]['BpFullTimeDate']
    if csvData[index]['country'] == "india":
        indexToSearch = getIndiaRGIndex(jsonResponse,csvData,index)
    elif csvData[index]['country'] == "sgmy_addons":
        indexToSearch = getSgmyRGIndex(jsonResponse,csvData,index)
    elif csvData[index]['country'] == "idn":
        indexToSearch = getIDNRGIndex(jsonResponse,csvData,index)
    csvData[index]['cancellationPolicy'] = jsonResponse['data'][indexToSearch]['cancellationPolicy']
    csvData[index]['addonUUID'] = jsonResponse['data'][indexToSearch]['uuid']
    csvData[index]['cityID'] = str(jsonResponse['data'][indexToSearch]['cityID'])
    csvData[index]['vendorType'] = jsonResponse['data'][indexToSearch]['vendorType']
    csvData[index]['type'] = jsonResponse['data'][indexToSearch]['type']
    csvData[index]['date'] = jsonResponse['data'][indexToSearch]['date']
    csvData[index]['category'] = jsonResponse['data'][indexToSearch]['extra']['category']
    csvData[index]['configuredFor'] = jsonResponse['data'][indexToSearch]['configuredFor']
    for i in jsonResponse['data'][indexToSearch]['cancellationPolicy']:
        if i==";":
            cancellationPolicy = jsonResponse['data'][indexToSearch]['cancellationPolicy'].split(";")[1]
            break
        else:
            cancellationPolicy = jsonResponse['data'][indexToSearch]['cancellationPolicy']
    cancellationPolicy = cancellationPolicy.split(":")
    Date_split = Date.split("-")
    month = Date_split[1]
    month = convert_month_str(month)
    Date = Date + " 00:00:00"
    midnight = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S")
    new_time = midnight - timedelta(hours=int(cancellationPolicy[0]))
    if cancellationPolicy[0] == "0":
        date = Date_split[2] 
    else:
        date = int(Date_split[2]) - 1
    if csvData[index]['country'] in ('india','idn'):
        time_12hr = new_time.strftime("%#I:%M %p")
    else:
        time_12hr = new_time.strftime("%I:%M %p")
    return new_time,date,month,time_12hr
def neonWalletApi(userId):
    requestUrl = "http://internal-trex-wallet-prod-lb-848382843.ap-southeast-1.elb.amazonaws.com:9090/api/v1/account/"+userId+"/balance"
    headers = {"Authorization":"a5ceb449-b577-491e-9c38-0f8a5eace789,16006c43-e9c0-4418-805b-3f71518dd042,2a397552-debe-41fd-92f6-f127f268ff6d,040b07be-493a-43e7-bf5e-499d44687944","MerchantId":"1","Currency":"MYR","BusinessUnit":"REDBUS_MY"}
    payload = {}
    response,resp_time = rq.request(rq,request_type="get",url=requestUrl,headers=headers,payload_data=payload)
    return response,resp_time 
def getUserId(csvData):
    AuthToken = csvData['AuthToken']
    endpoint = 'https://auth.redbus.in/'
    pathparams = 'AuthApi/v1/Token/GetUserId?token=' + AuthToken
    requestURL = endpoint + pathparams
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response,resp_time = rq.request(rq,request_type="get",url=requestURL,headers=headers,payload_data={})
    except Exception as e:
        tb.logInfo(tb,"auth timeout->",e)
                
    response = json.loads(response.text)
    tb.logInfo(tb,"auth requestURL->",requestURL)
    tb.logInfo(tb,"auth response->",response)
    return response
def getCSVData(sheetName):
    #a = C:/Users/ashton.c/Documents/REDBUS-AUTOMATION/rb-new-api-automation/tests/redbus-addons-00c37759fcfe.json"
    client = pygsheets.authorize(service_account_file="/var/lib/jenkins/workspace/redbus-addons-sheet.json") 
    name = client.spreadsheet_titles()
    for name1 in name:
        if name1 == 'addOns - Data':
            time.sleep(3)
            spreadsheet = client.open(name1)
            break
    worksheet = spreadsheet.worksheet_by_title(sheetName)
    return worksheet
def getUpdatedText(worksheet,cellValue):
    cell_value = worksheet.cell(cellValue).value
    lines = cell_value.splitlines()
    updatedText=[]
    if len(lines)>1:
        for i in lines:
            modified_text = i.replace('* ', '')
            try:
                text = int(modified_text)
            except:
                text = modified_text
            updatedText.append(text)
        return updatedText
    else:
        lines = lines[0]
        if lines in ('TRUE','FALSE'):
            lines = bool(lines)
        return lines
def getCellValue(worksheet,value,csvData,index):
    title = 'B3'
    subtitle = 'B4'
    iconImage = 'B5'
    howToRedeem = 'B7'
    highlights = 'B6'
    bookingPolicy = 'B9'
    cancellationPolicyString = 'B10'
    reschedulePolicy = 'B11'
    address = 'B12'
    additionalInformation = 'B30'
    isQrCodeRequired = 'B31'
    actuallyAddonBp = 'B32'
    actuallyAddonDp = 'B33'
    inclusions = 'B34'
    serviceProviderId = 'B35'
    serviceProviderName = 'B36'
    categories = 'B37'
    
    getCellDataDict = {
    'title': title,
    'subtitle': subtitle,
    'iconImage': iconImage,
    'howToRedeem': howToRedeem,
    'highlights': highlights,
    'bookingPolicy': bookingPolicy,
    'cancellationPolicyString': cancellationPolicyString,
    'reschedulePolicy': reschedulePolicy,
    'address': address,
    'additionalInformation': additionalInformation,
    'isQrCodeRequired': isQrCodeRequired,
    'actuallyAddonBp': actuallyAddonBp,
    'actuallyAddonDp': actuallyAddonDp,
    'inclusions': inclusions,
    'serviceProviderId': serviceProviderId,
    'serviceProviderName': serviceProviderName,
    'categories': categories
    }

    for key,value in getCellDataDict.items():
        updatedText = getUpdatedText(worksheet,value)
        csvData[index][key] = updatedText
        csvData[index]['isSheetData'] = True
def get_omega_response(csvData):
    RouteId = csvData['RouteId']
    doj = csvData['dojanotherformat1']
    country = csvData['country_name']
    omegaResponse = getRealTimeUpdate(RouteId,doj,country)
    return omegaResponse
def validatedynamicValidation(jsonResponse,feildPath,csvData,dynamicValidationKey,index,subApiName,DBValuematch,getCsvdata=False): 
    tb.logInfo(tb,"feildPath ->",feildPath)
    try: 
        result=cmn.evalExp(jsonResponse,feildPath)
    except:
        result = cmn.getDataFromFieldPathJsonPath(feildPath,jsonResponse)
    #results = []
    if result == []:
        result = str(cmn.getDataFromFieldPathJsonPath(feildPath,jsonResponse))
    result = "null" if len(result) == 0 else result
    results = result
    tb.logInfo(tb,"responseee ->",results)
    if not csvData[index].get(dynamicValidationKey):
        if csvData[int(index)].get('scenarioName'):
            scenarioName = csvData[index]['scenarioName']
        else:
            scenarioName,csvData[index]['scenarioName'] = "NA"
        if csvData[index].get('getCsvdata'):
            getCsvdata = True
        elif scenarioName == "KHM_Refferal":
            match subApiName:
                case "getReferralCode": 
                    match dynamicValidationKey:
                        case "ReferAndEarnTitle":
                            ReferAndEarnTitleText = "Get USD "+str(jsonResponse['CampaignConfigData']['ReferrCampaignAmount'])
                            csvData[index]['ReferAndEarnTitle'] = ReferAndEarnTitleText
                        case "ReferAndEarnTitleKM":
                            ReferAndEarnTitleText = "ទទួលបាន USD "+str(jsonResponse['CampaignConfigData']['ReferrCampaignAmount'])
                            csvData[index]['ReferAndEarnTitle'] = ReferAndEarnTitleText
                        case "ShareContent":
                            ShareContentText = "Hey! I love the redBus app and I think you would too. Download the redBus app and use my referral code red000kl to get USD "+str(jsonResponse['CampaignConfigData']['ReferrCampaignAmount'])+" when you sign-up. Click here to download the app: https://m6pe.app.link/referralKH?referralCode=red000kl&referralAmount=5"
                            csvData[index]['ShareContent'] = ShareContentText
                        case "ShareContentKM":
                            ShareContentText = "ហេ! ខ្ញុំចូលចិត្តកម្មវិធី redBus ហើយខ្ញុំគិតថាអ្នកក៏ចូលចិត្តដូចគ្នាដែរ។ ទាញយកកម្មវិធី redBus ហើយប្រើលេខកូដយោងរបស់ខ្ញុំ <REFCODE> ដើម្បីទទួលបាន USD "+str(jsonResponse['CampaignConfigData']['ReferrCampaignAmount'])+" ហើយចាប់ផ្តើមកក់សំបុត្រជាមួយប្រតិបត្តិកររថយន្តក្រុងដែលអ្នកពេញចិត្ត។ ប្រើលេខកូដ KHNEW ដើម្បីទទួលបានការបញ្ចុះតម្លៃបន្ថែម 20% លើការកក់សំបុត្រលើកដំបូងរបស់អ្នក។ ចុចទីនេះដើម្បីទាញយកកម្មវិធី៖"
                            csvData[index]['ShareContent'] = ShareContentText
                        case "ReferralRewardCount1":
                            ReferralRewardCount1 = int(csvData[index]['ReferralRewardCount']) + 1
                            csvData[index]['ReferralRewardCount1'] = str(ReferralRewardCount1)
                case "GetReferralDetails":
                    match dynamicValidationKey:
                        case "TotalEarnings":
                            TotalEarnings = int(csvData[index]['ReferrCampaignAmount']) * int(csvData[index]['ReferralRewardCount'])
                            if TotalEarnings == 0:
                                TotalEarnings = ""
                            csvData[index]['TotalEarnings'] = str(TotalEarnings) 
                case "walletBalance":
                    match dynamicValidationKey:
                        case "totalBalanceExUser":
                            totalBalance = int(csvData[index]['totalBalance']) + int(csvData[index]['ReferrCampaignAmount'])
                            csvData[index]['totalBalanceExUser'] = str(totalBalance) 
                        case "totalBalanceNewUser":
                            totalBalance = int(csvData[index]['FriendCampaignAmount'])
                            csvData[index]['totalBalanceNewUser'] = str(totalBalance)
        elif scenarioName == "sgmy_Refferal":
            match subApiName:
                case "getReferralCode": 
                    match dynamicValidationKey:
                        case "ReferAndEarnTitle":
                            ReferAndEarnTitleText = "Get RM "+str(jsonResponse['CampaignConfigData']['ReferrCampaignAmount'])
                            csvData[index]['ReferAndEarnTitle'] = ReferAndEarnTitleText
                        case "ShareContent":
                            ShareContentText = "Hey! I love the redBus app and i think so would you. Download the redBus app and use my referral code <REFCODE> to get RM "+str(jsonResponse['CampaignConfigData']['FriendCampaignAmount'])+" and start booking tickets with your favourite bus operator. Use discount code MYNEW to get an extra 10% discount on your first order. Click here to download the app:"
                            csvData[index]['ShareContent'] = ShareContentText
                        case "ReferralRewardCount1":
                            ReferralRewardCount1 = int(csvData[index]['ReferralRewardCount']) + 1
                            csvData[index]['ReferralRewardCount1'] = str(ReferralRewardCount1)
                case "GetReferralDetails":
                    match dynamicValidationKey:
                        case "TotalEarnings":
                            TotalEarnings = int(csvData[index]['ReferrCampaignAmount']) * int(csvData[index]['ReferralRewardCount'])
                            if TotalEarnings == 0:
                                TotalEarnings = ""
                            csvData[index]['TotalEarnings'] = str(TotalEarnings) 
                case "walletBalance":
                    match dynamicValidationKey:
                        case "totalBalanceExUser":
                            totalBalance = float(csvData[index]['totalBalance']) + float(csvData[index]['ReferrCampaignAmount'])
                            csvData[index]['totalBalanceExUser'] = str(totalBalance) 
                        case "totalBalanceNewUser":
                            totalBalance = int(csvData[index]['FriendCampaignAmount'])
                            csvData[index]['totalBalanceNewUser'] = str(totalBalance)
        elif scenarioName in ("signin","signup"):
            if feildPath.startswith("DB_"):
                if DBValuematch == "checkLength":
                    DBColumnName = feildPath.split("_")[1]
                    lengthData=len(csvData[index][DBColumnName])
                    tb.logInfo(tb,"DB Data->",csvData[index][DBColumnName])
                    tb.logInfo(tb,"Actual Data->",str(DBValuematch))
                    validationValue=check.is_true(lengthData>0,"Length is not greater than zero ,feildPath :"+str(feildPath))
                    if validationValue:
                        return True
                    else:
                        return False
                else:
                    DBColumnName = feildPath.split("_")[1]
                    tb.logInfo(tb,"DB Data->",csvData[index][DBColumnName])
                    tb.logInfo(tb,"Actual Data->",str(DBValuematch))
                    validationValue = check.equal(csvData[index][DBColumnName],str(DBValuematch),"Value is not equal"+str(DBValuematch)+":"+csvData[index][DBColumnName])
                    if validationValue:
                        return True
                    else:
                        return False
            if dynamicValidationKey == "WalletBalanceOffers":
                userId = csvData[index]['UserId']
                #response,resp_time = neonWalletApi(userId)
                requestUrl = "http://internal-trex-wallet-prod-lb-848382843.ap-southeast-1.elb.amazonaws.com:9090/api/v1/account/"+userId+"/balance"
                headers = {"Authorization":"a5ceb449-b577-491e-9c38-0f8a5eace789,16006c43-e9c0-4418-805b-3f71518dd042,2a397552-debe-41fd-92f6-f127f268ff6d,040b07be-493a-43e7-bf5e-499d44687944","MerchantId":"1","Currency":"MYR","BusinessUnit":"REDBUS_MY"}
                payload = {}
                response,resp_time = apicall.requestWithRetry(apicall,"get",requestUrl,headers,payload)
                response = json.loads(response.text)
                tb.logInfo(tb,"Neon Api Response->",response)
                if len(response['data']['offers'])>0:
                    for i in range(0,len(response['data']['offers'])):
                        expirationDate = response['data']['offers'][i]['expirationDate']
                        date = expirationDate.split(" ")[0]
                        time = expirationDate.split(" ")[1]
                        input_datetime = datetime(int(date.split("-")[0]), int(date.split("-")[1]), int(date.split("-")[2]), int(time.split(":")[0]), int(time.split(":")[1]), int(time.split(":")[2]))
                        expirationDate = input_datetime + timedelta(hours=8)
                        tb.logInfo(tb,"Neon Api->",response['data']['offers'][i])
                        tb.logInfo(tb,"SignIn Api->",jsonResponse['WalletBalance']['offers'][i])
                        if response['data']['offers'][i]['offerName'] == jsonResponse['WalletBalance']['offers'][i]['offerName'] and response['data']['offers'][i]['amount'] == jsonResponse['WalletBalance']['offers'][i]['amount'] and response['data']['offers'][i]['isRefundable'] == jsonResponse['WalletBalance']['offers'][i]['isRefundable'] and expirationDate == jsonResponse['WalletBalance']['offers'][i]['expirationDate']:
                            return True
                        else:
                            return False      
        elif scenarioName == "signup":
            if feildPath.startswith("DB_"):
                if DBValuematch == "checkLength": 
                    DBColumnName = feildPath.split("_")[1]
                    lengthData=len(csvData[index][DBColumnName])
                    tb.logInfo(tb,"DB Data->",csvData[index][DBColumnName])
                    tb.logInfo(tb,"Actual Data->",str(DBValuematch))
                    validationValue=check.is_true(lengthData>0,"Length is not greater than zero ,feildPath :"+str(feildPath))
                    if validationValue:
                        return True
                    else:
                        return False
                else:
                    DBColumnName = feildPath.split("_")[1]
                    tb.logInfo(tb,"DB Data->",csvData[index][DBColumnName])
                    tb.logInfo(tb,"Actual Data->",str(DBValuematch))
                    if DBValuematch == "mobileWithHash":
                        validationValue = check.equal(csvData[index][DBColumnName],csvData[index][DBValuematch],"Value is not equal"+str(DBValuematch)+":"+csvData[index][DBColumnName])
                    else:
                        validationValue = check.equal(csvData[index][DBColumnName],str(DBValuematch),"Value is not equal"+str(DBValuematch)+":"+csvData[index][DBColumnName])
                    if validationValue:
                        return True
                    else:
                        return False
            if dynamicValidationKey == "coTravellers":
                print("coTravellers12")
                data = jsonResponse['Cotravellers']
                sorted_data = sorted(data, key=lambda x: x["Id"])
                flag = True
                dbData = csvData[index]['coTrevelersDBResult']
                print("Hello1")
                for i in range(0,len(dbData)):
                    print("Hello2")
                    if dbData[i][3] == "Male":
                        gender = 0
                    else:
                        gender = 1
                    if sorted_data[i]['Id'] != dbData[i][0] or sorted_data[i]['Name'] != dbData[i][2] or sorted_data[i]['Age'] != dbData[i][7] or gender!=sorted_data[i]['Gender']:
                        flag = False
                        break
                print("flag12",flag)
                if flag:
                    return True
                else:
                    return False
        elif scenarioName == "addons":
            if dynamicValidationKey == "subtitle" and csvData[index]['country']=='india':
                subtitle = "Secure your travel at just ₹ "+csvData[index]['rapPrice']+" per passenger"
                csvData[index]['subtitle'] = subtitle
            if dynamicValidationKey == "mrp": 
                date = csvData[index]['BpFullTimeDate']
                time = csvData[index]['bptimeInFloat']
                input_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H.%M")
                current_time = datetime.now() + timedelta(hours=2, minutes=30)
                time_difference =  input_datetime - current_time
                seatPrice = csvData[index]['seatPrice']
                country = csvData[index]['country']
                discountPercentage = getDiscountPercentage(time_difference,country,jsonResponse)
                print("disc12",discountPercentage)
                mrp = getPrice(seatPrice,discountPercentage,country)
                csvData[index]['mrp'] = str(mrp)
                print("mrp12",csvData[index]['mrp'])
                csvData[index]['addonsPrice'] = str(mrp)
            if dynamicValidationKey == "rapPrice":
                requestUrl = 'http://internal-rb-addons-25313150.ap-southeast-1.elb.amazonaws.com:9090/v1/bo-cancel-rate/' + csvData[index]['operaterId']
                headers = {}
                payload = {}
                response,resp_time = rq.request(rq,request_type="get",url=requestUrl,headers=headers,payload_data=payload)
                response = json.loads(response.text)
                busCancellationPercentage = float(response['data']['busCancellationPercentage'])
                seatPrice = float(csvData[index]['seatPrice'])
                if (seatPrice>=0 and seatPrice <400) and (busCancellationPercentage>=0.0 and busCancellationPercentage<=1.0):
                    rapPrice = 14
                elif (seatPrice>=0 and seatPrice <400) and (busCancellationPercentage>=1.0 and busCancellationPercentage<=1.5):
                    rapPrice = 18
                elif (seatPrice>=0 and seatPrice <400) and (busCancellationPercentage>=1.5 and busCancellationPercentage<=2.0):
                    rapPrice = 27
                elif (seatPrice>=0 and seatPrice <400) and (busCancellationPercentage>=2.0 and busCancellationPercentage<=2.5):
                    rapPrice = 53
                elif (seatPrice>=400 and seatPrice <800) and (busCancellationPercentage>=0.0 and busCancellationPercentage<=1.0):
                    rapPrice = 19
                elif (seatPrice>=400 and seatPrice <800) and (busCancellationPercentage>=1.0 and busCancellationPercentage<=1.5):
                    rapPrice = 23
                elif (seatPrice>=400 and seatPrice <800) and (busCancellationPercentage>=1.5 and busCancellationPercentage<=2.0):
                    rapPrice = 31
                elif (seatPrice>=400 and seatPrice <800) and (busCancellationPercentage>=2.0 and busCancellationPercentage<=2.5):
                    rapPrice = 57
                elif (seatPrice>=800) and (busCancellationPercentage>=0.0 and busCancellationPercentage<=1.0):
                    rapPrice = 22
                elif (seatPrice>=800) and (busCancellationPercentage>=1.0 and busCancellationPercentage<=1.5):
                    rapPrice = 26
                elif (seatPrice>=800) and (busCancellationPercentage>=1.5 and busCancellationPercentage<=2.0):
                    rapPrice = 34
                elif (seatPrice>=800) and (busCancellationPercentage>=2.0 and busCancellationPercentage<=2.5):
                    rapPrice = 60
                csvData[index]['rapPrice'] = str(rapPrice)
                addonsPrice = float(rapPrice) - float(addOnsData.RAP_INSURANCE_PRICE.value)
                csvData[index]['addonsPrice'] = str(addonsPrice)
            if dynamicValidationKey == "yesMessage":
                if csvData[index]['country'] == 'sgmy_addons':
                    price = "{:.2f}".format(float(csvData[index]['mrp']))
                    yesMessage = "Add Refund Guarantee at just " + csvData[index]['Currency']+" "+price+" "+"per passenger"
                elif csvData[index]['country'] == 'idn':
                    price = f"{int(csvData[index]['mrp']) / 1000:.3f}"
                    yesMessage = "Add refund guarantee at only Rp "+price
                elif csvData[index]['country'] == 'india' and csvData[index]['addOnsName'] == 'RAP':
                    yesMessage = 'Yes, protect my trip at ₹ '+csvData[index]['rapPrice']+" (1 passenger), I agree to the <a href='https://www.redbus.in/info/ins_bcp_terms.html'>Terms and Conditions</a>"
                csvData[index]['yesMessage'] = yesMessage
            if dynamicValidationKey == "yesMessageV2":
                if csvData[index]['country'] == 'india' and csvData[index]['addOnsName'] == 'RAP':
                    yesMessageV2 = ' Yes, protect my trip at ₹ '+csvData[index]['rapPrice']+' (1 passenger)'
                elif csvData[index]['country'] == 'sgmy_addons':
                    price = "{:.2f}".format(float(csvData[index]['mrp']))
                    yesMessageV2 = "Get it at just " + csvData[index]['Currency']+" "+price+" "+"per passenger"
                csvData[index]['yesMessageV2'] = yesMessageV2
            if dynamicValidationKey == "cancellationPolicy_0":
                new_time,date,month,time_12hr = getCancelPolicy(csvData,index,jsonResponse)
                msg = "Before"+" "+str(date)+getsuffix(int(date))+" "+month+" "+str(time_12hr)
                csvData[index]['cancellationPolicy_0'] = msg
            if dynamicValidationKey == "chargesValue_0":
                if csvData[index]['country'] == "india":
                    indexToSearch = getIndiaRGIndex(jsonResponse,csvData,index)
                elif csvData[index]['country'] == "sgmy_addons":
                    indexToSearch = getSgmyRGIndex(jsonResponse,csvData,index)
                elif csvData[index]['country'] == "idn":
                    indexToSearch = getIDNRGIndex(jsonResponse,csvData,index)
                for i in jsonResponse['data'][indexToSearch]['cancellationPolicy']:
                    if i==";":
                        cancellationPolicy = jsonResponse['data'][indexToSearch]['cancellationPolicy'].split(";")[1]
                        break
                    else: 
                        cancellationPolicy = jsonResponse['data'][indexToSearch]['cancellationPolicy']
                cancellationPolicy = cancellationPolicy.split(":")
                if cancellationPolicy[2] == '0':
                    cancellationPolicyText = "Fully refundable"
                else:
                    cancellationPolicyText = cancellationPolicy[2] + "%"
                csvData[index]['chargesValue_0'] = cancellationPolicyText
            if dynamicValidationKey == "chargesValue_1":
                if csvData[index]['country'] == "india":
                    indexToSearch = getIndiaRGIndex(jsonResponse,csvData,index)
                elif csvData[index]['country'] == "sgmy_addons":
                    indexToSearch = getSgmyRGIndex(jsonResponse,csvData,index)
                elif csvData[index]['country'] == "idn":
                    indexToSearch = getIDNRGIndex(jsonResponse,csvData,index)
                cancellationPolicy = jsonResponse['data'][indexToSearch]['cancellationPolicy'].split(";")[0]
                cancellationPolicy = cancellationPolicy.split(":")
                csvData[index]['chargesValue_1'] = cancellationPolicy[2] + "%"
            if dynamicValidationKey == "cancellationPolicy_1":
                new_time,date,month,time_12hr = getCancelPolicy(csvData,index,jsonResponse)
                msg1 = "After"+" "+str(date)+getsuffix(int(date))+" "+month+" "+str(time_12hr)
                msg2 = "Before"+" "+str(date+1) + getsuffix(int(date+1)) + " "+month + " "+ "12:00 AM"
                csvData[index]['cancellationPolicy_1'] = msg1+" & "+msg2
            if dynamicValidationKey == "yesMessagesubText":
                msg = "Only for ₹"+csvData[index]['mrp']+" per passenger"
                csvData[index]['yesMessagesubText'] = msg
            if dynamicValidationKey == "yesMessagesubTextV2":
                msg = "₹"+csvData[index]['mrp']+" for 1 passenger"
                csvData[index]['yesMessagesubTextV2'] = msg
            if dynamicValidationKey == "expiryDate":
                start_date_str = csvData[index]['BpFullTimeDate']
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                if csvData[index]['addOnsName'] == 'Skytropolis':
                    future_date = start_date + timedelta(days=10)
                elif csvData[index]['addOnsName'] in('skyway-oneway','skyway-twoway'):
                    future_date = start_date + timedelta(days=15)
                future_date = future_date.strftime("%Y-%m-%d")
                csvData[index]['expiryDate'] = future_date
            if dynamicValidationKey == 'discount_price':
                csvData[index]['discount_price'] = customFunction.validate_discount_sg_rg_rails(jsonResponse,csvData[index])
            if getCsvdata:
                if csvData[index].get('isSheetData'):
                    pass
                else:
                    worksheet = getCSVData(csvData[index]['addOnsName'])
                    getCellValue(worksheet,dynamicValidationKey,csvData,index)
        elif dynamicValidationKey in('noteOnPayableAmt'):
            walletCoreUsable = float(jsonResponse['walletResponse']['walletCoreUsable'])
            walletCoreUsable = formatAmount(walletCoreUsable)
            s = str(walletCoreUsable)+" "+csvData[index]['Currency']+" core cash can be used for this booking. Any remaining amount will be refunded 7 days from wallet credit"
            res = jsonResponse['walletResponse']['noteOnPayableAmt']
            res = res[::-1].replace('.', '', 1)[::-1]
            if s == res:
                return True
            return False
        elif dynamicValidationKey == 'seatPriceFerry':
            if csvData[index]['scenarioName'] == 'ferry_adult':
                csvData[index]['seatPriceFerry'] = str(float(csvData[index]['adultFee']) * int(csvData[index]['numOfPessangers']))
            elif csvData[index]['scenarioName'] == 'ferry_adult_child':
                csvData[index]['seatPriceFerry'] = str(float(csvData[index]['adultFee']) + float(csvData[index]['childFee']))
            elif csvData[index]['scenarioName'] == 'ferry_radult':
                csvData[index]['seatPriceFerry'] = str(float(csvData[index]['roundTripAdultFee']) * int(csvData[index]['numOfPessangers']))
            elif csvData[index]['scenarioName'] == 'ferry_radult_rchild':
                csvData[index]['seatPriceFerry'] = str(float(csvData[index]['roundTripAdultFee']) + float(csvData[index]['roundTripChildFee'])) 
            if len(csvData[index]['seatPriceFerry'])>4:
                csvData[index]['seatPriceFerry'] =  f"{float(csvData[index]['seatPriceFerry']):.1f}"
                csvData[index]['seatPrice'] = csvData[index]['seatPriceFerry']
        elif subApiName == 'validateAuth':
            match dynamicValidationKey:
                case 'walletId':
                    dbResult = objdbU.getUserDetails(jsonResponse['tokenStatus']['Auth']['UdfParams']['UserId'])[0]
                    csvData[index]['walletId'] = str(dbResult[15])
            if feildPath.startswith("DB_"):
                feildPath = feildPath.split('_')[1]
                FLAG = True
                match feildPath:
                    case 'AUTH':
                        dbResult = objdbU.validateauth(csvData[index]['tokenAuth'])[0]
                        if not dbResult[3] == 'Auth':
                            FLAG = False
                            tb.logError(tb,"Auth:Audience->",dbResult[3]) 
                        result = authValidations(dbResult,FLAG,csvData[index])
                        if result == True:
                            return True 
                        else:
                            return False 
                    case 'PERSONALIZATION':
                        dbResult = objdbU.validateauth(csvData[index]['tokenPersonalization'])[0]
                        if not dbResult[3] == 'Personalisation':
                            FLAG = False
                            tb.logError(tb,"Personalization:Audience->",dbResult[3]) 
                        result = authValidations(dbResult,FLAG,csvData[index])
                        if result == True:
                            return True 
                        else:
                            return False
                    case 'UPDATE':
                        dbResult = objdbU.validateauth(csvData[index]['tokenUpdate'])[0]
                        if not dbResult[3] == 'Personalisation/Update':
                            FLAG = False
                            tb.logError(tb,"Update:Audience->",dbResult[3]) 
                        result = authValidations(dbResult,FLAG,csvData[index])
                        if result == True:
                            return True 
                        else:
                            return False
                    case 'WALLET':
                        dbResult = objdbU.validateauth(csvData[index]['tokenWallet'])[0]
                        if not dbResult[3] == 'Wallet':
                            FLAG = False
                            tb.logError(tb,"Wallet:Audience->",dbResult[3],csvData[index]) 
                        result = authValidations(dbResult,FLAG,csvData[index])
                        if result == True:
                            return True 
                        else:
                            return False            
        elif subApiName == 'ticketV2Info':
            match dynamicValidationKey:
                case 'RTOStartDate':
                    date_str = csvData[index]['dojanotherformat1']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    new_date_obj = date_obj + timedelta(days=1)
                    new_date_str = new_date_obj.strftime('%Y-%m-%d')
                    csvData[index]['RTOStartDate'] = new_date_str
                case 'returnOfferExpiry':
                    date_str = csvData[index]['RTOStartDate']
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    new_date_obj = date_obj + timedelta(days=14)
                    new_date_str = new_date_obj.strftime('%Y-%m-%d')
                    csvData[index]['returnOfferExpiry'] = new_date_str
        elif csvData[index]['scenarioName'] == 'round_trip':
            match subApiName.lower():
                case 'seatlayout':
                    match dynamicValidationKey:
                        case 'bpListLatLong':
                            csvData[index] = customFunction.get_lat_long(csvData[index]) 
                case 'orderinfo':
                    match dynamicValidationKey:
                        case 'totalPayable_reschedule':
                            csvData[index]['totalPayable_reschedule'] = customFunction.get_total_payable_reschedule(jsonResponse)
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalReturn':
                            csvData[index]['totalReturn'],csvData[index]['return_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'RETURN')
                            csvData[index]['return_totalFare_without_rg'] = customFunction.get_total_return_price_without_RG(csvData[index])
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'walletoffer':
                            csvData[index]['walletoffer'] = customFunction.get_total_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_walletoffer'] = customFunction.get_onward_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['return_walletoffer'] = customFunction.get_return_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_amount_paid_without_offer'] = customFunction.get_onward_amount_paid_without_offer(csvData[index])
                            csvData[index]['return_amount_paid_without_offer'] = customFunction.get_return_amount_paid_without_offer(csvData[index])
                            csvData[index]['onward_amount_paid_without_offer_without_rg'] = customFunction.get_onward_amount_paid_without_offer_without_rg(csvData[index])
                            csvData[index]['return_amount_paid_without_offer_without_rg'] = customFunction.get_return_amount_paid_without_offer_without_rg(csvData[index])
                case 'v2iscancellable':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy(csvData[index],jsonResponse)           
                        case 'cancellation_refundAmount':
                            csvData[index]['cancellation_refundAmount'] =  csvData[index]['refundAmount'] = customFunction.get_cancellation_refundAmount(jsonResponse)
                        case 'return_cancellation_refundAmount':
                            csvData[index]['return_cancellation_refundAmount'] =  csvData[index]['refundAmount'] = customFunction.get_cancellation_refundAmount(jsonResponse)
                        case 'cancellationcharges':
                            csvData[index]['cancellationcharges'] = customFunction.get_cancellation_charges(jsonResponse)
                            csvData[index]['cancellationcharges_with_rg'] = customFunction.get_cancellation_charges_with_rg(csvData[index].get('cancellationcharges',0),csvData[index].get('onward_rg_price',0))
                        case 'return_cancellationcharges':
                            csvData[index]['return_cancellationcharges'] = customFunction.get_cancellation_charges(jsonResponse)
                            csvData[index]['return_cancellationcharges_with_rg'] = customFunction.get_cancellation_charges_with_rg(csvData[index].get('return_cancellationcharges',0),csvData[index].get('return_rg_price',0))
                        case 'seat_refundAmount':
                            csvData[index]['seat_refundAmount'] = customFunction.get_seat_refund_amount(csvData[index],jsonResponse)
                        case 'return_seat_refundAmount':
                            csvData[index]['return_seat_refundAmount'] = customFunction.get_return_seat_refund_amount(csvData[index],jsonResponse)
                        case 'seat_nonrefundAmount':
                            csvData[index]['seat_nonrefundAmount'] = customFunction.get_seat_non_refund_amount(csvData[index],jsonResponse)
                        case 'return_seat_nonrefundAmount':
                            csvData[index]['return_seat_nonrefundAmount'] = customFunction.get_return_seat_non_refund_amount(jsonResponse)
                        case 'wngMsg_0':
                            csvData[index]['wngMsg_0'] = "Cancellation charges are computed on a per seat basis. Above cancellation fare is calculated based on seat fare of " + csvData[index]['Currency'] + " " + csvData[index]['seatPrice']
                        case 'CancelCharge':
                            csvData[index]['CancelCharge'] = customFunction.get_cancellation_charges(jsonResponse)
                case 'refundstatusv2':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy_refund_status(csvData[index],jsonResponse) 
        elif (csvData[index]['country']=='sgmy_ferry_rtrip') and subApiName.lower() == 'orderinfo':
            RouteId = csvData[index]['RouteId']
            doj = csvData[index]['dojanotherformat1']
            omegaResponse = getRealTimeUpdate(RouteId,doj)
            csvData[index]['odpTime'] = omegaResponse['bpList'][0]['time']
            date_str = omegaResponse['dpList'][0]['time']
            dep_time_zone = omegaResponse['depTimeZone']
            arr_time_zone = omegaResponse['arrTimeZone']
            result = convert_time_zone(date_str, dep_time_zone, arr_time_zone)
            csvData[index]['oarTime'] = result
            RouteId = csvData[index]['RTRouteId']
            doj = csvData[index]['RDateOfJourney']
            omegaResponse = getRealTimeUpdate(RouteId,doj)
            date_str = omegaResponse['dpList'][0]['time']
            dep_time_zone = omegaResponse['depTimeZone']
            arr_time_zone = omegaResponse['arrTimeZone']
            csvData[index]['rdpTime']  = omegaResponse['bpList'][0]['time']
            csvData[index]['rarTime']  = convert_time_zone(date_str, dep_time_zone, arr_time_zone)
            csvData[index]['rdpAddress']  = omegaResponse['bpList'][0]['caddress']
            csvData[index]['rarAddress']  = omegaResponse['dpList'][0]['caddress']
            bpTime_obj = datetime.fromisoformat(omegaResponse['bpList'][0]['time'])
            dpTime_obj = datetime.fromisoformat(omegaResponse['dpList'][0]['time'])
            time_difference = dpTime_obj - bpTime_obj
            difference_in_minutes = time_difference.total_seconds() / 60
            csvData[index]['RTduration'] = int(difference_in_minutes)
        elif csvData[index]['country'] == 'sgmy_ferry':
            match dynamicValidationKey:
                case 'totalFare':
                    match csvData[index]['scenarioName']:
                        case 'ferry_adult':
                            csvData[index]['totalFare'] =  str(jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'])
                        case 'ferry_adult_adult':
                            csvData[index]['totalFare'] =  str(jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] * 2)
                        case 'ferry_adult_child':
                            csvData[index]['totalFare'] =  str(jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] + jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['childFee'])
                        case 'ferry_rt_adult':
                            csvData[index]['totalFare'] =  str(jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee']*2)
                        case 'ferry_rt_adult_adult':
                            csvData[index]['totalFare'] =  str(jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] * 4)
                        case 'ferry_rt_adult_child':
                            csvData[index]['totalFare'] =  str((jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] * 2) + (jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['childFee'] * 2))
                case 'totalDiscountedFare':
                    match csvData[index]['scenarioName']:
                        case 'ferry_adult':
                            totalDiscountedFare = float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['adultFee'] if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'])
                            csvData[index]['totalDiscountedFare'] = str(round(totalDiscountedFare,2))
                        case 'ferry_adult_adult':
                            csvData[index]['totalDiscountedFare'] = str(round(float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['adultFee'] * 2 if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] * 2),2))
                        case 'ferry_adult_child':
                            csvData[index]['totalDiscountedFare'] = str(round(float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['adultFee'] + jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['childFee'] if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['adultFee'] + jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['childFee']),2))
                        case 'ferry_rt_adult':
                            csvData[index]['totalDiscountedFare'] = str(round(float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['roundTripAdultFee'] if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['roundTripAdultFee']),2))
                        case 'ferry_rt_adult_adult':
                            csvData[index]['totalDiscountedFare'] = str(round(float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['roundTripAdultFee'] * 2 if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['roundTripAdultFee'] * 2),2))
                        case 'ferry_rt_adult_child':
                            csvData[index]['totalDiscountedFare'] = str(round(float(jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['roundTripAdultFee'] + jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['ferryDiscFareLst'][0]['roundTripChildFee'] if (jsonResponse['inventories'][0].get('operatorOfferCampaign') and jsonResponse['inventories'][0]['operatorOfferCampaign']['CmpgList'][0]['RouteId']>0) else jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['roundTripAdultFee'] + jsonResponse['inventories'][0]['ferryDetails']['ferryFareList'][0]['roundTripChildFee']),2))
                case 'totalDiscountPercentage':
                    totalDiscountPercentage = round((float(csvData[index]['totalFare']) - float(csvData[index]['totalDiscountedFare'])) * 100 / float(csvData[index]['totalFare']),2)
                    csvData[index]['totalDiscountPercentage'] = str(0.0) if totalDiscountPercentage <= 0.0 else str(totalDiscountPercentage)
        # elif subApiName.lower() == 'routes':
        #     RouteId = str(jsonResponse['inventories'][0]['routeId'])
        elif csvData[index]['scenarioName'] == 'Cancellation':
            match subApiName.lower():
                case 'seatlayout':
                    match dynamicValidationKey:
                        case 'bpListLatLong':
                            csvData[index] = customFunction.get_lat_long(csvData[index])
                case 'orderinfo':
                    match dynamicValidationKey:
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'walletoffer':
                            csvData[index]['walletoffer'] = customFunction.get_total_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_walletoffer'] = customFunction.get_onward_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_amount_paid_without_offer'] = customFunction.get_onward_amount_paid_without_offer(csvData[index])
                            csvData[index]['onward_amount_paid_without_offer_without_rg'] = customFunction.get_onward_amount_paid_without_offer_without_rg(csvData[index])
                case 'v2iscancellable':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy(csvData[index],jsonResponse)
                        case 'cancellation_refundAmount':
                            csvData[index]['cancellation_refundAmount'] =  csvData[index]['refundAmount'] = customFunction.get_cancellation_refundAmount(jsonResponse)
                        case 'cancellationcharges':
                            csvData[index]['cancellationcharges'] = customFunction.get_cancellation_charges(jsonResponse)
                            csvData[index]['cancellationcharges_with_rg'] = customFunction.get_cancellation_charges_with_rg(csvData[index].get('cancellationcharges',0),csvData[index].get('onward_rg_price',0))
                        case 'seat_refundAmount':
                            csvData[index]['seat_refundAmount'] = customFunction.get_seat_refund_amount(csvData[index],jsonResponse)
                        case 'seat_nonrefundAmount':
                            csvData[index]['seat_nonrefundAmount'] = customFunction.get_seat_non_refund_amount(csvData[index],jsonResponse)
                        case 'wngMsg_0':
                            csvData[index]['wngMsg_0'] = "Cancellation charges are computed on a per seat basis. Above cancellation fare is calculated based on seat fare of " + csvData[index]['Currency'] + " " + csvData[index]['seatPrice']
                        case 'CancelCharge':
                            csvData[index]['CancelCharge'] = customFunction.get_cancellation_charges(jsonResponse)
                case 'refundstatusv2':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy_refund_status(csvData[index],jsonResponse) 
        elif csvData[index]['scenarioName'] == 'reschedule' or csvData[index].get('is_reschedule') == 'Yes':
            match subApiName.lower():
                case 'routes':
                    match dynamicValidationKey:
                        case 'onward_rescheduleCharge':
                            RouteId = str(jsonResponse['inventories'][0]['routeId'])
                            doj = jsonResponse['inventories'][0]['departureTime'].split(" ")[0]
                            omegaResponse = getRouteDetailsObject(RouteId,doj)
                            reschedule_policy = csvData[index]['onward_reschedule_policy'] = omegaResponse['param42']['rIsc'] if not omegaResponse['param42']['rIsc'] == '' else omegaResponse['param42']['boReqParm'][0]['reschedulePolicy']
                            if '-' in reschedule_policy.split(":")[3]:
                                reschedule_policy_arr = reschedule_policy.split(":")
                                reschedule_policy = csvData[index]['onward_reschedule_policy'] =':'.join(map(str, reschedule_policy_arr[0:3])) + ":"+reschedule_policy.split(":")[3].split("-")[0]
                            csvData[index]['onward_rescheduleTime'] = csvData[index]['rescheduleTime'] = str(reschedule_policy.split(":")[0])
                            reschedule_charge = reschedule_policy.split(":")[3]
                            csvData[index]['rescheduleCharge_without_currency'] = str(reschedule_charge)
                            csvData[index]['onward_rescheduleCharge'] = csvData[index]['rescheduleCharge'] = str(float(reschedule_charge)) + " " + jsonResponse['inventories'][0]['vendorCurrency']
                        case 'return_rescheduleCharge':
                            RouteId = str(jsonResponse['inventories'][0]['routeId'])
                            doj = jsonResponse['inventories'][0]['departureTime'].split(" ")[0]
                            omegaResponse = getRouteDetailsObject(RouteId,doj)
                            reschedule_policy = csvData[index]['return_reschedule_policy'] = omegaResponse['param42']['rIsc'] if not omegaResponse['param42']['rIsc'] == '' else omegaResponse['param42']['boReqParm'][0]['reschedulePolicy']
                            if '-' in reschedule_policy.split(":")[3]:
                                reschedule_policy_arr = reschedule_policy.split(":")
                                reschedule_policy = csvData[index]['return_reschedule_policy'] =':'.join(map(str, reschedule_policy_arr[0:3])) + ":"+reschedule_policy.split(":")[3].split("-")[0]
                            csvData[index]['return_rescheduleTime'] = csvData[index]['rescheduleTime'] = str(reschedule_policy.split(":")[0])
                            reschedule_charge = reschedule_policy.split(":")[3]
                            csvData[index]['return_rescheduleCharge'] = csvData[index]['rescheduleCharge'] = str(float(reschedule_charge)) + " " + jsonResponse['inventories'][0]['vendorCurrency']
                case 'busdetailsv3':
                    match dynamicValidationKey:
                        case 'onward_RescheduleText':
                            csvData[index]['onward_RescheduleText'] = "The ticket you book on this bus can be rescheduled, you can advance or postpone the ticket to a different date as per your convenience. "+str(csvData[index]['onward_rescheduleCharge'])+" is applicable as fee per seat and rescheduling is allowed till "+str(csvData[index]['onward_rescheduleTime'])+" hours before time of departure. Reschedule is available only till services are available for future dates"
                        case 'return_RescheduleText':
                            csvData[index]['return_RescheduleText'] = "The ticket you book on this bus can be rescheduled, you can advance or postpone the ticket to a different date as per your convenience. "+str(csvData[index]['return_rescheduleCharge'])+" is applicable as fee per seat and rescheduling is allowed till "+str(csvData[index]['return_rescheduleTime'])+" hours before time of departure. Reschedule is available only till services are available for future dates"
                        case 'onward_rsPl_msg':
                            datetime_str = jsonResponse['firstBpTime']
                            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                            new_datetime_obj = datetime_obj - timedelta(hours=int(csvData[index]['onward_rescheduleTime']))
                            day = str(new_datetime_obj).split(" ")[0].split("-")[2]
                            csvData[index]['res_day'] = str(day)
                            suffix = getsuffix(int(day))
                            result1 = new_datetime_obj.strftime("%d %b %Y %I:%M %p").split(" ")
                            result = str(result1[0]) + suffix + " "+" ".join(result1[1:])
                            result = "Before "+result
                            csvData[index]['onward_rsPl_msg'] = result
                        case 'return_rsPl_msg':
                            datetime_str = jsonResponse['firstBpTime']
                            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                            new_datetime_obj = datetime_obj - timedelta(hours=int(csvData[index]['return_rescheduleTime']))
                            day = str(new_datetime_obj).split(" ")[0].split("-")[2]
                            suffix = getsuffix(day)
                            result1 = new_datetime_obj.strftime("%d %b %Y %I:%M %p").split(" ")
                            result = str(result1[0]) + suffix + " "+" ".join(result1[1:])
                            result = "Before "+result
                            csvData[index]['return_rsPl_msg'] = result        
                case 'seatlayout':
                    match dynamicValidationKey:
                        case 'bpListLatLong':
                            csvData[index] = customFunction.get_lat_long(csvData[index]) 
                case 'ticketv2info':
                    match dynamicValidationKey:
                        case 'rsPl_charges':
                            csvData[index]['rsPl_charges'] = "Free" if csvData[index]['rsPl_charges'] == "FREE" else csvData[index]['rsPl_charges']
                case 'ticketv1details':
                    match dynamicValidationKey:
                        case 'CurrentRescheduleCharge':
                            charges = csvData[index]['rsPl_charges'].split(" ")
                            csvData[index]['RescheduleCharge'] = str(float(charges[0]))
                            csvData[index]['CurrentRescheduleCharge'] = str(int(float(charges[0]))) + " " + charges[1]
                case 'v1iscancellable':
                    match dynamicValidationKey:
                        case 'Total_Fare':
                            csvData[index]['Total_Fare'] = str(float(csvData[index]['paidAmount']) + float(csvData[index]['totalDiscount']))  
                        case 'onward_RescheduleFareBreakUp_resCharge':
                            csvData[index]['onward_RescheduleFareBreakUp_resCharge'] = str(int(float(csvData[index]['onward_rescheduleCharge'].split(" ")[0])))
                        case 'return_RescheduleFareBreakUp_resCharge':
                            csvData[index]['return_RescheduleFareBreakUp_resCharge'] = str(int(float(csvData[index]['return_rescheduleCharge'].split(" ")[0])))
                        case 'onward_ReschedulePolicyMsg':
                            rsPl_msg = csvData[index]['onward_rsPl_msg'].split("Before ")[1]
                            day = csvData[index]['res_day']
                            month = rsPl_msg.split(" ")[1]
                            time = rsPl_msg.split(" ")[3] + " " + rsPl_msg.split(" ")[4]
                            csvData[index]['onward_ReschedulePolicyMsg'] = "You can reschedule this journey till "+day+" "+month+" "+time
                        case 'return_ReschedulePolicyMsg':
                            rsPl_msg = csvData[index]['return_rsPl_msg'].split("Before ")[1]
                            day = rsPl_msg.split(" ")[0].split("th")[0]
                            month = rsPl_msg.split(" ")[1]
                            time = rsPl_msg.split(" ")[3] + " " + rsPl_msg.split(" ")[4]
                            csvData[index]['return_ReschedulePolicyMsg'] = "You can reschedule this journey till "+day+" "+month+" "+time
                case 'orderinfo':
                    match dynamicValidationKey:
                        case 'rescheduleTotalPayable':
                            totalPayable = 0.0
                            for i in range(0,len(jsonResponse['fareBreakUp'])):
                                for j in range(0,len(jsonResponse['fareBreakUp'][i]['itemFB'])):
                                    if jsonResponse['fareBreakUp'][i]['itemFB'][j]['componentType'] == 'ADD':
                                        totalPayable += jsonResponse['fareBreakUp'][i]['itemFB'][j]['amount']
                                    elif jsonResponse['fareBreakUp'][i]['itemFB'][j]['componentType'] == 'SUB':
                                        totalPayable -= jsonResponse['fareBreakUp'][i]['itemFB'][j]['amount']
                            if len(jsonResponse['fareBreakUp'])>1 and jsonResponse['fareBreakUp'][1]['itemType'] == 'INSURANCE':
                                totalPayable = float(totalPayable) + 1.0
                            csvData[index]['rescheduleTotalPayable'] = str(totalPayable)  
                        case 'totalPayable_reschedule':
                            csvData[index]['totalPayable_reschedule'] = customFunction.get_total_payable_reschedule(jsonResponse)
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'walletoffer':
                            csvData[index]['walletoffer'] = customFunction.get_total_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_walletoffer'] = customFunction.get_onward_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_amount_paid_without_offer'] = customFunction.get_onward_amount_paid_without_offer(csvData[index])
                            csvData[index]['onward_amount_paid_without_offer_without_rg'] = customFunction.get_onward_amount_paid_without_offer_without_rg(csvData[index])
        elif subApiName.lower() == 'profilemeta':
            match dynamicValidationKey:
                case 'userData':
                    userId = getUserId(csvData[index])
                    dbResult = objdbU.getUserDetails(userId)
                    csvData[index]['email'] = dbResult[0][3]
                    if "@ignoredemailid" in csvData[index]['email']:
                        csvData[index]['email'] = ''
                    csvData[index]['phone'] = str(dbResult[0][4])
                    csvData[index]['dob'] = '0001-01-01' if str(dbResult[0][5]) == 'None' else str(dbResult[0][5]).split(" ")[0] 
                    csvData[index]['name'] = dbResult[0][6]
                    csvData[index]['gender'] = dbResult[0][13]
                    csvData[index]['createdDate'] = str(dbResult[0][18])
                    if not csvData[index]['phone'] == 'None':
                        csvData[index]['countryCode'] = "+" + csvData[index]['phone'][0:3] if csvData[index]['phone'].startswith('855') else "+" + csvData[index]['phone'][0:2]
                        csvData[index]['mobileNumber'] = csvData[index]['phone'][3:] if csvData[index]['phone'].startswith('855') else csvData[index]['phone'][2:]
                    else:
                        csvData[index]['countryCode'] = ""
                        csvData[index]['mobileNumber'] = ""
                    #csvData[index]['new_dob'] = str(int(csvData[index]['dob'].split("-")[0]) + 1)
                    csvData[index]['new_name'] = csvData[index]['name']
                    csvData[index]['gender'] = dbResult[0][13]
                    return True
        elif subApiName.lower() == 'getpassangerdetails':
            Flag = False
            match dynamicValidationKey:
                case 'genderAllPax':
                    for i in range(0,len(jsonResponse['data'])):
                        if jsonResponse['data'][i]['gender'] in ('Male','Female'):
                            Flag = True
                        else:
                            Flag = False
                    return Flag
                case 'isMobileVerifiedAllPax':
                    Flag = True if jsonResponse['data'][0]['contactDetails']['isMobileVerified'] == 1 else False
                    for i in range(1,len(jsonResponse['data'])):
                        Flag = True if jsonResponse['data'][i]['contactDetails']['isMobileVerified'] == 1 else False                          
                    return Flag
                case 'hasAccountAllPax':
                    Flag = True if jsonResponse['data'][0]['contactDetails']['hasAccount'] == True else False
                    for i in range(1,len(jsonResponse['data'])):
                        Flag = True if jsonResponse['data'][i]['contactDetails']['hasAccount'] == False else False                        
                    return Flag
        elif csvData[index]['scenarioName'] == 'TTD_Cancellation':
            match subApiName.lower():
                case 'getcart':
                    match dynamicValidationKey:
                        case 'cancellationMsg':
                            date_obj = datetime.strptime(csvData[index]['visitDate'], "%Y-%m-%d")
                            hours = int(csvData[index]['cancellationPolicy'].split(';')[-1].split(':')[0])
                            csvData[index]['validityTime'] = date_obj.strftime("%a, %d %b %Y")
                            new_date_obj = date_obj - timedelta(hours=hours)
                            csvData[index]['validityDecription'] = new_date_obj.strftime("%a, %d %b %Y")
                            csvData[index]['validityDecription'] = csvData[index]['slot']  + " " +csvData[index]['validityDecription'] if csvData[index].get('slot') else csvData[index]['validityDecription'] 
                            csvData[index]['cancellationMsg'] = "Free cancellation before " + csvData[index]['validityDecription']
                case 'v1iscancellablettd':
                    match dynamicValidationKey:
                        case 'adult_cancellation_charge':
                            csvData[index]['adult_cancellation_charge'] = str(float(csvData[index]['adultFare']) * float(csvData[index]['cancellationPercent'])/100)
                        case 'adult_cancellation_charge2':
                            csvData[index]['adult_cancellation_charge2'] = str(float(csvData[index]['adultFare2']) * float(csvData[index]['cancellationPercent'])/100)
                        case 'child_cancellation_charge':
                            csvData[index]['child_cancellation_charge'] = str(float(csvData[index]['childFare']) * float(csvData[index]['cancellationPercent'])/100)
                        case 'adultrefundableValue':
                            adultrefundableValue = float(jsonResponse['subItemWiseRefundables'][0]['priceBreakUp'][0]['value'] - jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'])
                            tb.logInfo(tb,"subItemWiseRefundables[0]['priceBreakUp'][0]['value'] ->",jsonResponse['subItemWiseRefundables'][0]['priceBreakUp'][0]['value'])
                            tb.logInfo(tb,"jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'] ->",jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'])
                            csvData[index]['adultrefundableValue'] = str(int(adultrefundableValue) if adultrefundableValue.is_integer() else adultrefundableValue)
                        case 'adultrefundableValue2':
                            adultrefundableValue = float(jsonResponse['subItemWiseRefundables'][0]['priceBreakUp'][0]['value'] - jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'])
                            tb.logInfo(tb,"subItemWiseRefundables[0]['priceBreakUp'][0]['value'] ->",jsonResponse['subItemWiseRefundables'][0]['priceBreakUp'][0]['value'])
                            tb.logInfo(tb,"jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'] ->",jsonResponse['subItemWiseRefundables'][0]['cancellationCharge'])
                            csvData[index]['adultrefundableValue2'] = str(int(adultrefundableValue) if adultrefundableValue.is_integer() else adultrefundableValue)
                        case 'childrefundableValue':
                            childrefundableValue = float(jsonResponse['subItemWiseRefundables'][1]['priceBreakUp'][0]['value'] - jsonResponse['subItemWiseRefundables'][1]['cancellationCharge'])
                            csvData[index]['childrefundableValue'] = str(int(childrefundableValue) if childrefundableValue.is_integer() else childrefundableValue)
                        case 'refundableAmount':   
                            csvData[index]['childrefundableValue'] = "0.0" if not csvData[index].get('childrefundableValue') else csvData[index]['childrefundableValue']
                            refundableAmount = float(float(csvData[index]['adultrefundableValue']) + float(csvData[index]['childrefundableValue']))
                            csvData[index]['refundableAmount'] = str(int(refundableAmount) if refundableAmount.is_integer() else round(refundableAmount,2))
                        case 'refundableAmount2':   
                            csvData[index]['childrefundableValue2'] = "0.0" if not csvData[index].get('childrefundableValue2') else csvData[index]['childrefundableValue2']
                            refundableAmount = float(float(csvData[index]['adultrefundableValue2']) + float(csvData[index]['childrefundableValue2']))
                            csvData[index]['refundableAmount2'] = str(int(refundableAmount) if refundableAmount.is_integer() else round(refundableAmount,2))
                        case 'currentCancellationPolicy':
                            cancellationPolicy = csvData[index]['cancellationPolicy']
                            policy = cancellationPolicy.split(";")
                            cancelPolicy = getCancelPolicyJson(policy)
                            response = jsonResponse['currentCancellationPolicy']['listCancellationPolicyDTO']    
                            result = set()
                            result.add(True) if response == cancelPolicy else result.add(False)
                            if len(result) == 1 and list(result)[0] == True: 
                                return True
                            else: 
                                tb.logError(tb,"getCancelPolicy ->",cancelPolicy)
                                tb.logError(tb,"response ->",response)
                                getcheckCancelPolicyErrorTTD(cancelPolicy,response)
                                return False
                        case 'discount':
                            csvData[index]['discount'] = str(sum(jsonResponse['offerRetained'].values()))
                        case 'cancellationCharges':
                            if csvData[index].get('activityType') == 'date_time':
                                date_str = csvData[index]['visitDate'] + " " + csvData[index]['slot']
                            else:
                                date_str = csvData[index]['visitDate'] + " " + "00:00"
                            given_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                            time_difference = (given_date - datetime.now()).total_seconds() / 3600
                            cancellationPolicy = csvData[index]['cancellationPolicy'].split(";")
                            cancellationPolicy = cancellationPolicy[::-1]
                            for policy in cancellationPolicy:
                                if time_difference > float(policy.split(":")[0]):
                                    csvData[index]['cancellationPercent'] = str(float(policy.split(":")[2]))
                                    csvData[index]['cancellationCharges'] = str(jsonResponse['totalFare'] * float(policy.split(":")[2]) / 100)
                                    break 
                        case 'quantityPax':
                            csvData[index]['quantityPax'] = str(csvData[index].get('quantity','null') + " Pax")
                        case 'quantityPax_second_ticket':
                            csvData[index]['quantityPax_second_ticket'] = str(csvData[index].get('quantity_second_ticket','null') + " Pax")
                        case 'wallet_core_refundable_amount':
                            csvData[index]['wallet_core_refundable_amount'] = str(round((float(csvData[index]['totalFare']) * 0.95 ) -  float(csvData[index]['cancellationPercent']),2))
                        case 'online_refundable_amount':
                            csvData[index]['online_refundable_amount'] = str(round((float(csvData[index]['totalFare'])) -  float(csvData[index]['cancellationPercent']),2))
                        
                        case 'refundable_amount_second_ticket':
                            wallet_offer_amount = (float(csvData[index]['adultFare']) + float(csvData[index]['adultFare2'])) * 0.05
                            csvData[index]['refundable_amount_second_ticket'] = str(float(csvData[index]['adultFare']) - wallet_offer_amount)
        elif dynamicValidationKey in ('totalDeductable','refundAmount','CancellationCharges','ferry','totalFareReschedule'):
            totalPaid = 0
            #order info
            if jsonResponse.get('fareBreakUp'):
                fare_break_up = jsonResponse['fareBreakUp']
                itemFB = jsonResponse['fareBreakUp'][0]['itemFB']
                if dynamicValidationKey == "ferry":
                    totalPaid = sum(cmn.evalExp(jsonResponse, f"fareBreakUp.[0].itemFB[{i}].amount")[0] for i in range(len(itemFB)))
                    csvData[index][dynamicValidationKey] = str(totalPaid)
                else:
                    totalPaid = sum(cmn.evalExp(jsonResponse, f"fareBreakUp.[{i}].itemFB[0].amount")[0] for i in range(len(fare_break_up)))
                    if len(fare_break_up[0]['itemFB'])>1:
                        csvData[index]['redDealAmount'] = str(jsonResponse['fareBreakUp'][0]['itemFB'][1]['amount'])
                        totalPrice = totalPaid - jsonResponse['fareBreakUp'][0]['itemFB'][1]['amount']
                    else:
                        totalPrice = totalPaid
                    if dynamicValidationKey == "walletoffer":
                        if jsonResponse['walletResponse']['walletOfferUsable'] == ((jsonResponse['fareBreakUp'][0]['itemFB'][0]['amount'] * int(jsonResponse['walletResponse']['splitPercent']))/100):
                            return True
                        else:
                            return False
                    csvData[index][dynamicValidationKey] = str(totalPrice)
                    csvData[index]['totalPaid'] = str(totalPaid)

            if dynamicValidationKey == "totalFareReschedule":
                if float(jsonResponse['RescheduleFareBreakUp'][0]['Value']['amount']) == float(csvData[index]['totalPaid']) - float(csvData[index]['rgprice']):
                    return True
                else: 
                    return False

            if dynamicValidationKey == "CancellationCharges":
                if float(jsonResponse['CancellationCharges']) == round((float(csvData[index]['walletCore']) - float(csvData[index]['totalrefundAmount'])),2):
                    return True
                else:
                    return False    
        elif dynamicValidationKey == "seatPriceMultiPax":
                csvData[index]['seatPriceMultiPax'] = str(float(csvData[index]['seatPrice']) * 2)
        elif dynamicValidationKey == "dojVal":
            results[0] = results[0][:2]
        elif dynamicValidationKey == "totalPaid_without_addons":
            if csvData[index].get('rgprice'):
                csvData[index][dynamicValidationKey] = float(csvData[index]['totalPaid']) - float(csvData[index]['rgprice'])
            else:
                csvData[index][dynamicValidationKey] = float(csvData[index]['totalPaid'])
        #if dynamicValidationKey == "amenities":
            for i,(key,amenity) in enumerate(csvData[index]['amenities'].items()):
                if str(amenity) != str(cmn.evalExp(jsonResponse,"amenities.[{index}]".format(index=i))[0]):
                    return False
            return True
        elif dynamicValidationKey == "serviceNotes":
            serviceNotes=[]    
            for i in range(len(jsonResponse["serviceNotes"]["Policies"])):
                serviceNotes.append(jsonResponse["serviceNotes"]["Policies"][i].PolicyID)
            for key in csvData[index]['serviceNotes']:
                if key not in(serviceNotes):
                    return False
            return True
        elif dynamicValidationKey == "departedBus":
            if int(csvData[index]['busCount']) == len(jsonResponse['inventories']):
                return True
            return False
        elif dynamicValidationKey == "paymentOffer":
            if jsonResponse['PIAmt'] == csvData[index]['paidAmount']:
                return True
            return False
        elif csvData[index]['scenarioName'] == "Terminal_Codes":
            match subApiName.lower():
                case 'seatlayout':
                    match dynamicValidationKey:
                        case 'bpListLatLong':
                            csvData[index] = customFunction.get_lat_long(csvData[index]) 
                case 'orderinfo':
                    match dynamicValidationKey:
                        case 'walletoffer':
                                csvData[index]['walletoffer'] = str(get_round_off_price(float(csvData[index].get('totalBaseFare',0)) * int(jsonResponse['walletResponse']['splitPercent'])/100))        
                                csvData[index]['onward_walletoffer'] = str(get_round_off_price(float(csvData[index]['seatPrice']) * int(jsonResponse['walletResponse']['splitPercent'])/100))         
                                csvData[index]['onward_amount_paid_without_offer'] = str(get_round_off_price(float(csvData[index].get('totalOnward',0)) - float(csvData[index].get('onward_walletoffer'))))
                                csvData[index]['onward_amount_paid_without_offer_without_rg'] = str(get_round_off_price(float(csvData[index].get('onward_amount_paid_without_offer',0)) - float(csvData[index].get('onward_rg_price',0))))          
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'terminal_codes':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            omega_response = get_omega_response(csvData[index])
                            neon_serviceProviderName = None if neon_response['data']['otherItems'].get('BOARDING_PASS') == None else neon_response['data']['otherItems']['BOARDING_PASS'][0]['serviceProviderName']
                            neon_serviceProviderId = None if neon_response['data']['otherItems'].get('BOARDING_PASS') == None else neon_response['data']['otherItems']['BOARDING_PASS'][0]['serviceProviderId']
                            omega_serviceProviderName = None if omega_response['bpList'][0].get('bpassVName') == None else omega_response['bpList'][0].get('bpassVName')
                            omega_serviceProviderId = None if omega_response['bpList'][0].get('bpassVID') == None else omega_response['bpList'][0].get('bpassVID')
                            if neon_serviceProviderName == omega_serviceProviderName and neon_serviceProviderId == omega_serviceProviderId:
                                tb.logInfo(tb,"neon_serviceProviderName->",neon_serviceProviderName)
                                tb.logInfo(tb,"omega_serviceProviderName->",omega_serviceProviderName)
                                tb.logInfo(tb,"neon_serviceProviderId->",neon_serviceProviderId)
                                tb.logInfo(tb,"omega_serviceProviderId->",omega_serviceProviderId)
                                return True
                            else:
                                tb.logError(tb,"neon_serviceProviderName->",neon_serviceProviderName)
                                tb.logError(tb,"omega_serviceProviderName->",omega_serviceProviderName)
                                tb.logError(tb,"neon_serviceProviderId->",neon_serviceProviderId)
                                tb.logError(tb,"omega_serviceProviderId->",omega_serviceProviderId)
                                return False
        elif scenarioName=="twid":
            match subApiName.lower():
                case "orderinfo":
                    match dynamicValidationKey:
                        case "checkTotalFareWithReward":
                            totalFare=customFunction.getTotalFareWithReward(jsonResponse) 
                            csvData[index]["checkTotalFareWithReward"]=str(totalFare)
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'walletoffer':
                            csvData[index]['walletoffer'] = customFunction.get_total_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_walletoffer'] = customFunction.get_onward_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_amount_paid_without_offer'] = customFunction.get_onward_amount_paid_without_offer(csvData[index])
                            csvData[index]['onward_amount_paid_without_offer_without_rg'] = customFunction.get_onward_amount_paid_without_offer_without_rg(csvData[index])
                case 'v2iscancellable':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy(csvData[index],jsonResponse)
                        case 'cancellation_refundAmount':
                            csvData[index]['cancellation_refundAmount'] =  csvData[index]['refundAmount'] = customFunction.get_cancellation_refundAmount(jsonResponse)
                        case 'cancellationcharges':
                            csvData[index]['cancellationcharges'] = customFunction.get_cancellation_charges(jsonResponse)
                            csvData[index]['cancellationcharges_with_rg'] = customFunction.get_cancellation_charges_with_rg(csvData[index].get('cancellationcharges',0),csvData[index].get('onward_rg_price',0))
                        case 'seat_refundAmount':
                            csvData[index]['seat_refundAmount'] = customFunction.get_seat_refund_amount(csvData[index],jsonResponse)
                        case 'seat_nonrefundAmount':
                            csvData[index]['seat_nonrefundAmount'] = customFunction.get_seat_non_refund_amount(csvData[index],jsonResponse)
                        case 'wngMsg_0':
                            csvData[index]['wngMsg_0'] = "Cancellation charges are computed on a per seat basis. Above cancellation fare is calculated based on seat fare of " + csvData[index]['Currency'] + " " + csvData[index]['seatPrice']
                        case 'CancelCharge':
                            csvData[index]['CancelCharge'] = customFunction.get_cancellation_charges(jsonResponse)
                case 'refundstatusv2':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy_refund_status(csvData[index],jsonResponse)
        elif scenarioName == "sgmy_streaks":
            match subApiName.lower():
                case 'routes':
                    match dynamicValidationKey:
                        case 'streak_inv_count':
                            csvData[index]['streak_inv_count'] = str(customFunction.get_inv_len(csvData[index]['routeId'],jsonResponse))  
                        case 'streak_return_inv_count':
                            csvData[index]['streak_return_inv_count'] = str(customFunction.get_inv_len(csvData[index]['return_routeId'],jsonResponse))  
                        case 'MaxOfferAmount':
                            csvData[index]['MaxOfferAmount'] = str(results)
                            if float(csvData[index]['MaxOfferAmount'])>0.0:
                                return True      
                case 'seatlayout':
                    match dynamicValidationKey:
                        case 'bpListLatLong':
                            csvData[index] = customFunction.get_lat_long(csvData[index]) 
                case 'orderinfo':
                    match dynamicValidationKey:
                        case "streak_tag_invalid":
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0]['tags'][0] == 'STREAK_CONSENT':
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return False
                        case "no_streak_tag_invalid":
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0].get('tags') == None:
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0].get('tags'))
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return False
                        case 'streak_tag_invalid_round_trip':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0]['tags'][0] == 'STREAK_CONSENT' and neon_response['data']['orderItems'][1]['tags'][0] == 'STREAK_CONSENT':
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][1]['tags'][0])
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][1]['tags'][0])
                                return False
                        case 'no_streak_tag_invalid_round_trip':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0].get('tags') == None and neon_response['data']['orderItems'][1].get('tags') == None:
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0].get('tags'))
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][1].get('tags'))
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][1]['tags'][0])
                                return False
                        case 'streak_tag_active':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0]['tags'][0] == 'STREAK_CONSENT' and neon_response['data']['orderItems'][0]['tags'][1] == 'STREAK_CALL_UPDATE':
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return False
                        case 'streak_tag_booking':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0]['tags'][0] == 'STREAK_CONSENT' and neon_response['data']['orderItems'][0]['tags'][1] == 'STREAK_CALL_UPDATE':
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return False
                        case 'streak_tag_redemption':
                            neon_response = customFunction.get_neon_response(csvData[index])
                            if neon_response['data']['orderItems'][0]['tags'][0] == 'STREAK_CONSENT' and neon_response['data']['orderItems'][0]['tags'][1] == 'STREAK_CALL_UPDATE' and neon_response['data']['orderItems'][0]['tags'][2] == 'STREAK_CONCLUDE':
                                tb.logInfo(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return True
                            else:
                                tb.logError(tb,"neon_streaks_tag:",neon_response['data']['orderItems'][0]['tags'][0])
                                return False
                        case 'totalOnward':
                            csvData[index]['totalOnward'],csvData[index]['onward_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'ONWARD')
                            csvData[index]['totalFare_without_rg'] = customFunction.get_total_onward_price_without_RG(csvData[index])
                        case 'totalBaseFare':
                            csvData[index]['totalBaseFare'] = customFunction.getTotalBaseFare(jsonResponse)
                        case 'totalFare':
                            csvData[index]['totalFare'] = customFunction.getTotalFare(jsonResponse)
                        case 'totalReturn':
                            csvData[index]['totalReturn'],csvData[index]['return_rg_price'] = customFunction.getTotalJourneyFare(jsonResponse,'RETURN')
                            csvData[index]['return_totalFare_without_rg'] = customFunction.get_total_return_price_without_RG(csvData[index])
                        case 'walletoffer':
                            csvData[index]['walletoffer'] = customFunction.get_total_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_walletoffer'] = customFunction.get_onward_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['return_walletoffer'] = customFunction.get_return_wallet_offer(csvData[index],jsonResponse)
                            csvData[index]['onward_amount_paid_without_offer'] = customFunction.get_onward_amount_paid_without_offer(csvData[index])
                            csvData[index]['return_amount_paid_without_offer'] = customFunction.get_return_amount_paid_without_offer(csvData[index])
                            csvData[index]['onward_amount_paid_without_offer_without_rg'] = customFunction.get_onward_amount_paid_without_offer_without_rg(csvData[index])
                            csvData[index]['return_amount_paid_without_offer_without_rg'] = customFunction.get_return_amount_paid_without_offer_without_rg(csvData[index])
                        case 'streakDiscount':
                            csvData[index]['streakDiscount'] = customFunction.get_streak_discount(jsonResponse)
                        case 'totalDiscount':
                            csvData[index]['totalDiscount'] = customFunction.get_total_discount(jsonResponse)
                        case 'offerDiscount':
                            csvData[index]['offerDiscount'] = customFunction.get_offer_discount(jsonResponse)   
                        case 'totalWalletUsed':
                            csvData[index]['totalWalletUsed'] = customFunction.get_total_wallet_used(jsonResponse)
                        case 'totalPayable':
                            csvData[index]['totalPayable'] = customFunction.get_total_payable(jsonResponse)         
                case 'v2iscancellable':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy(csvData[index],jsonResponse)
                        case 'cancellation_refundAmount':
                            csvData[index]['cancellation_refundAmount'] =  csvData[index]['refundAmount'] = customFunction.get_cancellation_refundAmount(jsonResponse)
                        case 'cancellationcharges':
                            csvData[index]['cancellationcharges'] = customFunction.get_cancellation_charges(jsonResponse)
                            csvData[index]['cancellationcharges_with_rg'] = customFunction.get_cancellation_charges_with_rg(csvData[index].get('cancellationcharges',0),csvData[index].get('onward_rg_price',0))
                        case 'seat_refundAmount':
                            csvData[index]['seat_refundAmount'] = customFunction.get_seat_refund_amount(csvData[index],jsonResponse)
                        case 'seat_nonrefundAmount':
                            csvData[index]['seat_nonrefundAmount'] = customFunction.get_seat_non_refund_amount(csvData[index],jsonResponse)
                        case 'wngMsg_0':
                            csvData[index]['wngMsg_0'] = "Cancellation charges are computed on a per seat basis. Above cancellation fare is calculated based on seat fare of " + csvData[index]['Currency'] + " " + csvData[index]['seatPrice']
                        case 'CancelCharge':
                            csvData[index]['CancelCharge'] = customFunction.get_cancellation_charges(jsonResponse)
                case 'refundstatusv2':
                    match dynamicValidationKey:
                        case 'getCancelPolicy':
                            return customFunction.get_cancel_policy_refund_status(csvData[index],jsonResponse) 
    #Added validations to handle data masking. Pass is_masking_enabled as true in input csv
    if csvData[index].get('data_masked') == None and not csvData[index].get('mobileno') == None and csvData[index].get('is_masking_enabled') == 'Yes':
        csvData[index]['data_masked'] = 'Yes'
        #csvData[index]['name'] = customFunction.get_string_masked(csvData[index]['name'])
        email = csvData[index]['email'].split("@")
        csvData[index]['email'] = customFunction.get_string_masked(email[0]) + "@"+email[1]
        csvData[index]['mobileno'] = customFunction.get_mobile_number_masked(csvData[index]['mobileno'])
    result = validate(csvData,index,dynamicValidationKey,results)
    if result:
        return True
    else:
        return False