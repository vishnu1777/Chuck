from datetime import datetime, timedelta, date
from utils.legacy_util_functions.crud_ops_client import requestClient as rq
import json, requests, re
from utils.legacy_util_functions.constants import neon_details as neon_details
from utils.legacy_util_functions.constants import Omega as Omega
import utils.legacy_util_functions.commons as cmn
from utils.legacy_util_functions.legacy_validation_checker import TestBaseClass as tb

def getDate(doj):
    dt = date.today()
    td = timedelta(days=int(doj))
    doj=dt + td
    return str(doj)
def getRealTimeUpdate(RouteId,doj,country=''):
    endpoint = Omega.latam_end_point.value if country == 'latam' else Omega.sea_end_point.value
    pathparams = 'IASPublic/getRouteDetailsObject/'+RouteId+'/'+doj
    requestURL = endpoint + pathparams
    try:
        response,resp_time = rq.request(rq,request_type="get",url=requestURL,headers={},payload_data={})
    except Exception as e:
        tb.logError(tb,"omega requestURL->",requestURL)
        tb.logError(tb,"omega api timeout->",e)
    response = json.loads(response.text)
    tb.logInfo(tb,"omega requestURL->",requestURL)
    tb.logInfo(tb,"omega response->",response)
    return response
def getAvAltRoutesObject(csvData):
    GEO  = cmn.get_geo(csvData['headers']['Country_Name'])                 
    doj = getDate(csvData['doj'])
    endpoint = Omega.sea_end_point.value if GEO == 'SEA' else Omega.latam_end_point.value
    pathparams = 'IASPublic/getAvAltRoutesObject/'+csvData['src']+'/'+csvData['dest']+"/"+doj
    requestURL = endpoint + pathparams
    try:
        response,resp_time = rq.request(rq,request_type="get",url=requestURL,headers={},payload_data={})
    except Exception as e:
        tb.logError(tb,"omega requestURL->",requestURL)
        tb.logError(tb,"omega api timeout->",e)
    response = json.loads(response.text)
    tb.logInfo(tb,"omega requestURL->",requestURL)
    tb.logInfo(tb,"omega response->",response)
    return response
def round_of_trailing_zero(number):
    return str(int(number)if float(number).is_integer() else number)
def format_lat_long(latlong):
    latlong = latlong.split(",")
    latlong[0] = round_of_trailing_zero(float(latlong[0]))
    latlong[1] = round_of_trailing_zero(float(latlong[1]))
    latlong_core = str(latlong[0]).rstrip('0') +","+ str(latlong[1]).rstrip('0')
    latlong = latlong[0] +","+ latlong[1]
    return latlong,latlong_core
def get_lat_long(csvData):
    omegaResponse = getRealTimeUpdate(csvData['RouteId'],csvData['dojanotherformat1'],csvData['country'])
    bp_latlong = omegaResponse['bpList'][0]['vLat'] + "," + omegaResponse['bpList'][0]['vLon'] if (csvData.get('country') and csvData['country'] in ('sgmy','khm')) else omegaResponse['bpList'][0]['latitude'] + "," + omegaResponse['bpList'][0]['longitude']
    dp_latlong = omegaResponse['dpList'][0]['vLat'] + "," + omegaResponse['dpList'][0]['vLon'] if (csvData.get('country') and csvData['country'] in ('sgmy','khm')) else omegaResponse['dpList'][0]['latitude'] + "," + omegaResponse['dpList'][0]['longitude']
    if bp_latlong == ',':
        csvData['bpListLatLongCore'] = ''
        csvData['bpListLatLong'] = None 
    else:
        csvData['bpListLatLong'],csvData['bpListLatLongCore'] = format_lat_long(bp_latlong)
    if dp_latlong == ',':
        csvData['dpListLatLongCore'] = '' 
        csvData['dpListLatLong'] = None
    else:
        csvData['dpListLatLong'],csvData['dpListLatLongCore'] = format_lat_long(dp_latlong)
    return csvData
def get_round_off_price(totalFare):
    totalFare = round(totalFare,2)
    return f"{totalFare:.2f}".rstrip('0').rstrip('.')
def getTotalBaseFare(jsonResponse):
    totalBaseFare = 0
    for fare_break_up in jsonResponse['fareBreakUp']:
        if fare_break_up['itemType'] == 'BUS':
            for itemFB in fare_break_up['itemFB']:
                if itemFB['type'] == 'BASIC_FARE':
                    totalBaseFare += itemFB['amount']
    return str(get_round_off_price(totalBaseFare))
def getTotalJourneyFare(jsonResponse,journey):
    totalFare = 0
    rg_price = 0
    for fare_break_up in jsonResponse['fareBreakUp']:
        if fare_break_up['journeyType'] == journey:
            for itemFB in fare_break_up['itemFB']:
                if itemFB['componentType'] == 'ADD':
                    totalFare += itemFB['amount']
                elif itemFB['componentType'] == 'SUB':
                    totalFare -= itemFB['amount']
            if fare_break_up['itemType'] == 'ASSURANCE_SERVICE':
                rg_price = str(fare_break_up['itemFB'][0]['amount'])
    return str(get_round_off_price(totalFare)),str(rg_price)
def get_total_onward_price_without_RG(csvData):
    return str(get_round_off_price(float(csvData.get('totalOnward',0)) - float(csvData.get('onward_rg_price',0))))
def get_total_return_price_without_RG(csvData):
    return str(get_round_off_price(float(csvData.get('totalReturn',0)) - float(csvData.get('return_rg_price',0))))
def getTotalFare(jsonResponse):
    totalFare = 0
    for fare_break_up in jsonResponse['fareBreakUp']:
        for itemFB in fare_break_up['itemFB']:
            if itemFB['componentType'] == 'ADD':
                totalFare += itemFB['amount']
            elif itemFB['componentType'] == 'SUB':
                totalFare -= itemFB['amount']
    return str(get_round_off_price(totalFare))
def get_total_payable_reschedule(jsonResponse):
    totalPayable_onward_reschedule = 0
    for fareBreakUp in jsonResponse['fareBreakUp']:
        for itemFB in fareBreakUp['itemFB']:
            if itemFB['displayName'] == 'Insurance':
                totalPayable_onward_reschedule += (itemFB['amount'] * 2)
            elif itemFB['componentType'] == 'ADD':
                totalPayable_onward_reschedule += itemFB['amount']
            elif itemFB['componentType'] == 'SUB':
                totalPayable_onward_reschedule -= itemFB['amount']   
    return str(totalPayable_onward_reschedule)
def get_total_wallet_offer(csvData,jsonResponse):
    if not jsonResponse.get('walletResponse') == None:
        return str(get_round_off_price(float(csvData.get('totalBaseFare',0)) * int(jsonResponse['walletResponse']['splitPercent'])/100))  
    else:
        return str(0.0)
def get_onward_wallet_offer(csvData,jsonResponse):
    if not jsonResponse.get('walletResponse') == None:
        return str(get_round_off_price(float(csvData['seatPrice']) * int(jsonResponse['walletResponse']['splitPercent'])/100))               
    else:
        return str(0.0)
def get_return_wallet_offer(csvData,jsonResponse):
    if not jsonResponse.get('walletResponse') == None:
        return str(get_round_off_price(float(csvData.get('return_seatPrice',0)) * int(jsonResponse['walletResponse']['splitPercent'])/100))
    else:
        return str(0.0)         
def get_onward_amount_paid_without_offer(csvData):
    return str(get_round_off_price(float(csvData.get('totalOnward',0)) - float(csvData.get('onward_walletoffer'))))
def get_return_amount_paid_without_offer(csvData):
    return str(get_round_off_price(float(csvData.get('totalReturn',0)) - float(csvData.get('return_walletoffer'))))
def get_onward_amount_paid_without_offer_without_rg(csvData):
    return str(get_round_off_price(float(csvData.get('onward_amount_paid_without_offer',0)) - float(csvData.get('onward_rg_price',0))))          
def get_return_amount_paid_without_offer_without_rg(csvData):
    return str(get_round_off_price(float(csvData.get('return_amount_paid_without_offer',0)) - float(csvData.get('return_rg_price',0))))            
def get_day_suffix(day):
            if 11 <= day <= 13:
                return 'th'
            elif day % 10 == 1:
                return 'st'
            elif day % 10 == 2:
                return 'nd'
            elif day % 10 == 3:
                return 'rd'
            else:
                return 'th'
def getCancelPolicyJsonBus(policy,csvData):
    currency = csvData['Currency']
    endDateTimeArray = []
    cancelPolicy = []
    date=csvData["BpFullTime"]
    for i in range(0,len(policy)):
        date_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        new_date_object = date_object - timedelta(hours=int(policy[i].split(":")[0]))
        day = new_date_object.day
        day_suffix = get_day_suffix(day)
        endDateTime = new_date_object.strftime('%d-%m-%Y %H:%M:%S')
        endDateTimeArray.append(endDateTime)
        cancellationStringArray = []
        total_fare=csvData["seatPrice"]
        if str(policy[i].split(":")[1]) == "-1":
            cancellationString = "Before " + new_date_object.strftime(f'%-d{day_suffix} %b %I:%M %p')
            cancellationStringArray.append(cancellationString)
            current_time = datetime.now()
            if csvData.get('country_name') and csvData['country_name'] == 'sgmy':
                hour,min = 2,30
            elif csvData.get('country_name') and csvData['country_name'] == 'khm':
                hour,min = 1,30
            new_time = current_time + timedelta(hours=hour, minutes=min)
            formatted_time = new_time.strftime('%d-%m-%Y %H:%M:%S')
            startDateTime = formatted_time
            currentSlot = True
        else:
            new_date_string = "Before " + new_date_object.strftime(f'%-d{day_suffix} %b %I:%M %p')
            cancellationStringArray.append(new_date_string)
            after_date_object = date_object - timedelta(hours=int(policy[i].split(":")[1]))
            day_suffix = get_day_suffix(after_date_object.day)
            cancellationString = "After " + after_date_object.strftime(f'%-d{day_suffix} %b %I:%M %p') + " & " + new_date_string
            startDateTime = endDateTimeArray[i-1] 
            endDateTime = new_date_object.strftime('%d-%m-%Y %H:%M:%S')
            endDateTimeArray.append(endDateTime)
            currentSlot = False
        chargePerc = policy[i].split(":")[2]+"%"
        chargeExact = float(float(total_fare) * int(policy[i].split(":")[2])/100)
        refundableAmount = round(float(total_fare) - float(chargeExact),2)
        if csvData.get('country_name') == 'khm':
            dict = {
                "cancellationString": cancellationString,
                "chargeExact": currency + " " +str(chargeExact).rstrip('0').rstrip('.'),  
                "chargePerc": chargePerc,
                "refundableAmount": currency + " " + str(refundableAmount).rstrip('0').rstrip('.'),
                "currentSlot" : currentSlot,
                "endDateTime": endDateTime,
                "startDateTime": startDateTime
            }
        else:
            dict = {
                "cancellationString": cancellationString,
                "chargeExact": currency + " " +str(chargeExact).rstrip('0').rstrip('.'),  
                "chargePerc": chargePerc,
                "refundableAmount": currency + " " + str(refundableAmount).rstrip('0').rstrip('.'),
                "currentSlot" : currentSlot,
                "endDateTime": endDateTime,
                "startDateTime": startDateTime
            }
        cancelPolicy.append(dict)
    return cancelPolicy
def check_time_difference(given_time_str):
    given_time = datetime.strptime(given_time_str, "%d-%m-%Y %H:%M:%S")    
    current_time = datetime.now()    
    time_difference = abs((given_time - current_time).total_seconds())  
    return time_difference > 1
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
def get_cancel_policy(csvData,jsonResponse):
    policy = csvData["policy"]
    policy = policy.split(";")[::-1]
    cancelPolicy = []
    cancelPolicy = getCancelPolicyJsonBus(policy,csvData)
    result = set()
    response = jsonResponse['items'][0]['cancelPolicy']
    result.add(True) if response == cancelPolicy else result.add(False)
    if len(result) == 1 and list(result)[0] == True: 
        return True
    else:
        result = check_time_difference(cancelPolicy[0]['startDateTime']) 
        print("result ->",result)
        if result:
            return True
        else:
            tb.logError(tb,"getCancelPolicy ->",cancelPolicy)
            tb.logError(tb,"response ->",response)
            getcheckCancelPolicyError(cancelPolicy,response)
            return False
def get_cancellation_refundAmount(jsonResponse):
    refundAmount = 0
    for i in range(0,len(jsonResponse['items'][0]['refundBreakUp'])):
        refundAmount += jsonResponse['items'][0]['refundBreakUp'][i]['refundAmount']
    for i in range(0,len(jsonResponse['items'][0]['offerBreakUp'])):
        refundAmount -= jsonResponse['items'][0]['offerBreakUp'][i]['nonRefundAmount']
    return str(round(float(refundAmount),2))
def get_cancellation_charges(jsonResponse):
    cancellationcharges = 0
    for i in range(0,len(jsonResponse['items'][0]['refundBreakUp'])):
        if not jsonResponse['items'][0]['refundBreakUp'][i]['displayName'] == 'CONVENIENCE_FEE':
            cancellationcharges += jsonResponse['items'][0]['refundBreakUp'][i]['nonRefundAmount']
    return str(cancellationcharges)
def get_cancellation_charges_with_rg(cancellationcharges,rg_price):
    return str(float(cancellationcharges) + float(rg_price))
def get_seat_refund_amount(csvData,jsonResponse):
    currency = csvData['Currency']+""
    return str(jsonResponse['items'][0]['cancelPolicy'][0]['refundableAmount'].split(currency)[1])
def get_return_seat_refund_amount(csvData,jsonResponse):
    currency = csvData['Currency']+""
    return str(jsonResponse['items'][0]['cancelPolicy'][0]['refundableAmount'].split(currency)[1] -  - float(csvData['walletOffer']))
def get_seat_non_refund_amount(csvData,jsonResponse):
    currency = csvData['Currency']+""
    return str(jsonResponse['items'][0]['cancelPolicy'][0]['chargeExact'].split(currency)[1])
def get_return_seat_non_refund_amount(jsonResponse):
    return str(get_round_off_price(float(jsonResponse['items'][0]['refundBreakUp'][0]['amount']) - float(jsonResponse['items'][0]['refundBreakUp'][0]['refundAmount'])))
def get_cancel_policy_refund_status(csvData,jsonResponse):
    policy = csvData["policy"]
    policy = policy.split(";")[::-1]
    cancelPolicy = []
    cancelPolicy = getCancelPolicyJsonBus(policy,csvData)
    result = set()
    response = jsonResponse['items'][0]['cancelPolicy']
    result.add(True) if response == cancelPolicy else result.add(False)
    if len(result) == 1 and list(result)[0] == True: 
        return True
    else:
        result = check_time_difference(cancelPolicy[0]['startDateTime']) 
        print("result ->",result)
        if result:
            return True
        else:
            tb.logError(tb,"getCancelPolicy ->",cancelPolicy)
            tb.logError(tb,"response ->",response)
            getcheckCancelPolicyError(cancelPolicy,response)
            return False
def getTotalFareWithReward(fare_data):
     # Initialize variables to store the calculated amounts
    basic_fare_total = 0
    discount_total = 0
    # Access the 'fareBreakUp' list and the 'itemFB' list inside it
    fare_breakup = fare_data.get("fareBreakUp", [])
    for fare in fare_breakup:
        item_fb = fare.get("itemFB", [])
        for item in item_fb:
            if item.get("type") == "BASIC_FARE":
                basic_fare_total += item.get("amount", 0)
            elif item.get("type") == "SERVICE_TAX":
                basic_fare_total += item.get("amount", 0)
            elif item.get("type") == "RED_DEALS":
                discount_total += item.get("amount", 0)
            elif item.get("type") == "TWID_REWARD":
                discount_total += item.get("amount", 0)
    # Calculate the final difference
    wallet_usable_amount=float(fare_data['orderFareSplit'].get('totalWalletUsed')) if fare_data['orderFareSplit'].get('totalWalletUsed') else 0.0
    offer_amount = 0.0
    
    offer_amount = float(fare_data.get('orderFareSplit').get('offerDiscount')) if fare_data.get('orderFareSplit').get('offerDiscount') else 0.0
    difference = basic_fare_total - wallet_usable_amount - offer_amount 
    formatted_value = f"{difference:.10f}".rstrip('0').rstrip('.')
    # Convert the formatted string back to float for comparison
    return max(float(formatted_value), 0)
def get_string_masked(str):
    if len(str) <= 2:
        return str 
    return str[0] + '*' * (len(str) - 2) + str[-1]
def get_mobile_number_masked(num):
    if len(num) <= 2:
        return num 
    return '*' * (len(num) - 2) + num[len(num)-3:]
def get_neon_response(csvData):
    headers = {
        "Content-Type": "application/json",
        "OauthEmail": neon_details.OauthEmail.value,
        "OauthAccessToken": neon_details.OauthAccessToken.value,
        "OauthExpires": neon_details.OauthExpires.value
    }
    base_url_prod = 'http://neon.intlomsproxy.redbus.in/v2/'
    base_url_stage = 'http://neon-dom-oms-stage-1.redbus.in:8000/v4/'
    url = base_url_prod+"orders/{orderId}?showThirdPartyDetails=true".format(orderId = csvData['OrderUUId'])
    response = requests.get(url,headers=headers)
    print(response)
    return json.loads(response.text)
def getTotalPayable(jsonResponse,csvData):
    if jsonResponse['walletResponse'].get('totalWalletBalance'):
        return 0.0
    else:
        return csvData['totalFare']
def get_total_wallet_used(jsonResponse):
    if jsonResponse['walletResponse'].get('totalWalletBalance') == None:
        return 0.0
    else:
        return jsonResponse['orderFareSplit']['totalFare'] - jsonResponse['orderFareSplit']['offerDiscount']
def get_streak_discount(jsonResponse):
    streak_discount = 0
    for fare_break_up in jsonResponse['fareBreakUp']:
        for itemFB in fare_break_up['itemFB']:
            if itemFB['componentType'] == 'ADD':
                streak_discount += itemFB['amount']
            elif itemFB['componentType'] == 'SUB':
                streak_discount -= itemFB['amount']
    return streak_discount
def get_inv_len(route_id,jsonResponse):
    operator_id = next((inv['operatorId'] for inv in jsonResponse['inventories'] if str(inv['routeId']) == str(route_id)), None)
    count = 0
    for inv in jsonResponse['inventories']:
        if inv['operatorId'] == operator_id:
            count += 1
    return count
def get_total_discount(jsonResponse):
    total_discount = 0
    total_discount += jsonResponse['orderFareSplit']['offerDiscount'] + jsonResponse['orderFareSplit']['streakDiscount']
    if not jsonResponse.get('walletResponse') == None:
        total_discount += jsonResponse['walletResponse']['walletOfferUsable']
    return str(total_discount)
def get_offer_discount(jsonResponse):
    if not jsonResponse.get('offerResponse') == None:
        offer_discount = jsonResponse['offerResponse']['data']['Value']
    else:
        offer_discount = 0.0
    return str(offer_discount)
def get_total_payable(jsonResponse):
    return str(jsonResponse['orderFareSplit']['totalFare'] - jsonResponse['orderFareSplit']['offerDiscount'] - jsonResponse['orderFareSplit']['totalWalletUsed'])
# Function to convert date format (Before 4th Nov 04:30 PM) to (2024-11-04T16:30:00)
def convertDateTimeToDateTTimeFormat(inputDateFormat):
    inputDateFormat = re.sub(r'(st|nd|rd|th)', '', inputDateFormat)
    date_obj = datetime.strptime(inputDateFormat, '%d %b %I:%M %p')
    date_obj = date_obj.replace(year=2024)
    formatted_date = date_obj.strftime('%Y-%m-%dT%H:%M:%S')
    return formatted_date
# Function to match date format
def match_date_format_for_policy(jsonResponse,key):
    policy_size = len(jsonResponse["cancelpolicylist"])
    start_time = jsonResponse["cancelpolicylist"][0]["duration"]
    end_time = jsonResponse["cancelpolicylist"][policy_size-1]["duration"]
    cancel_policy_start_time = jsonResponse["cancelPolicyStartTime"]
    cancel_policy_end_time = jsonResponse["cancelPolicyEndTime"]
    start_time = start_time.split("Before ")[1]
    end_time = (end_time.split(" Until")[0]).split("From ")[1]
    formatted_start_date = convertDateTimeToDateTTimeFormat(start_time)
    formatted_end_date = convertDateTimeToDateTTimeFormat(end_time)
    if formatted_start_date == cancel_policy_start_time and formatted_end_date == cancel_policy_end_time:
        print(" Policy Start Time : ",start_time," = ",cancel_policy_start_time,"\n","Policy End Time : ",end_time," = ",cancel_policy_end_time)
        return True
    else:
        return False
def calculate_orderinfo_fare(jsonResponse):
    value =True
    fare_breakUp = jsonResponse['fareBreakUp']
    order_fares = jsonResponse['orderFareSplit']
    amount_payable = 0
    for fares in fare_breakUp[0]['itemFB']:
        if fares['displayName'] == 'redDeal':
            amount_payable -= fares['amount']
        else:
            amount_payable += fares['amount']
    if len(fare_breakUp)>1:
        amount_payable += fare_breakUp[1]['itemFB'][0]['amount']
    if order_fares['totalFare'] != amount_payable or order_fares['totalBaseFare'] != fare_breakUp[0]['itemFB'][0]['amount']:
        value = False
    return value
# add discount offercode and percentage in the dictionary
def discount_offer_code_validation(jsonResponse):
    all_offer_codes = {
        "SUPERHIT" : 5,
        "SUPERHITPP" : 5
    }
    order_Fare_split = jsonResponse['orderFareSplit']
    offer_code = jsonResponse['offerResponse']['data']['Code']
    offer_percentage = all_offer_codes[offer_code]
    total_discount = round((order_Fare_split['totalBaseFare'] * offer_percentage) / 100,2)
    # max offer discount should be 150
    max_offer = total_discount if total_discount <=150 else 150
    print("maxOffer",max_offer)
    print("total_discount",total_discount)
    if max_offer != order_Fare_split['offerDiscount']:
        return False
    if  total_discount + order_Fare_split['totalBaseFare'] != order_Fare_split['totalFare']:
        return False
    return True
def check_omega_response_adhoc_distance_sort(omega_response):
    for i in range(0,len(omega_response)-1):
        if (omega_response[i]['search_tag'] in ("DEST_FIXED","SOURCE_FIXED")) and (omega_response[i+1]['search_tag'] in ("DEST_FIXED","SOURCE_FIXED"))and omega_response[i]['adhocDistance'] > omega_response[i+1]['adhocDistance']:
            tb.logError(tb,"Distance is not sorted at index:"+str(i)+" ",str(omega_response[i]['adhocDistance'])+":"+str(omega_response[i+1]['adhocDistance']))
            return False
        if (omega_response[i]['search_tag'] == 'SOURCE_DEST_UNFIXED') and (omega_response[i+1]['search_tag'] == 'SOURCE_DEST_UNFIXED')and omega_response[i]['adhocDistance'] > omega_response[i+1]['adhocDistance']:
            tb.logError(tb,"Distance is not sorted at index:"+str(i)+" ",str(omega_response[i]['adhocDistance'])+":"+str(omega_response[i+1]['adhocDistance']))
            return False
    return True
def check_keys_omega_capi_response(alternateRoutes_lenth,alternateRoutes,omega_response):
    for i in range(0,alternateRoutes_lenth):
        for keys in alternateRoutes[i]:
            if isinstance(alternateRoutes[i][keys], dict):  
                for keys1 in alternateRoutes[i][keys]:
                    if not alternateRoutes[i][keys][keys1] == omega_response[i][keys][keys1]:
                        tb.logError(tb,"Element mismatch at index"+str(i),"omega key :"+str(omega_response[i][keys])+" capi key:"+str(alternateRoutes[i][keys]))
                        return False
            elif alternateRoutes[i]['search_tag'] == 'SOURCE_FIXED' and keys == 'altSourceDist':
                return alternateRoutes[i][keys] == 0.0
            elif alternateRoutes[i]['search_tag'] == 'DEST_FIXED' and keys == 'altDestDist':
                return alternateRoutes[i][keys] == 0.0
            elif not alternateRoutes[i][keys] == omega_response[i][keys]:
                tb.logError(tb,"Element mismatch at index"+str(i),"keys ->"+keys+" omega key :"+str(omega_response[i][keys])+" capi key: "+str(alternateRoutes[i][keys]))
                return False
    return True
def validate_alternate_routes_bus(jsonResponse,csvData):
    omega_response = getAvAltRoutesObject(csvData)
    omega_response = omega_response['routes']
    if check_omega_response_adhoc_distance_sort(omega_response):
        alternateRoutes = jsonResponse['BUS']['alternateRoutes']
        alternateRoutes_lenth = len(alternateRoutes)
        if not len(omega_response) == alternateRoutes_lenth:
            tb.logError(tb,"Length is not equal:Length of omega ->"+str(len(omega_response)),"Length of capi oops ->"+str(len(alternateRoutes)))
            return False
        print("alternateRoutes ->",alternateRoutes)
        print("omega_response ->",omega_response)
        return check_keys_omega_capi_response(alternateRoutes_lenth,alternateRoutes,omega_response)
    return False
def validate_discount_sg_rg_rails(jsonResponse,csvData):
    total_price = 0
    for response in jsonResponse['data']:
        total_price += response['displayPrice']
    return str(total_price * int(csvData['discount']) // 100) 
#def validate_rails_fareBreakup_discount(jsonResponse):
