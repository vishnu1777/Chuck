import json
from benedict import benedict
import pytest_check as check
import os
import unittest
from utils.legacy_util_functions import legacy_logger as logmanager
import datetime,time
from pyjsonpath import JsonPath
import jsonpath_ng.ext as jp



class TestBaseClass(unittest.TestCase):

    logger = logmanager.get_logger(__name__)
    
    @classmethod
    def setUpClass(cls):
        cls.logger.info("Test execution started for all test methods witinin: "+cls.__name__)     

    def setUp(self):
        self.logger.info("Test picked: "+str(self.id()).split('.')[-1])
        
    def tearDown(self):
        self.logger.info("Test completed: "+str(self.id()).split('.')[-1])

    @classmethod
    def tearDownClass(cls,fileDeleteList:list=None): 
        if (fileDeleteList is None):
            cls.logger.info("Test execution Completed for all test methods witinin: "+cls.__name__)
        else:
            cls.logger.info("DELETING Constructed Files for API's from The List ->"+str(fileDeleteList))
            for delpaths in fileDeleteList:
                if os.path.exists(delpaths):
                    os.remove(delpaths)
                    cls.logger.info("Successfully Deleted file ->"+str(delpaths))
                else:
                    cls.logger.error("File Not Found in the Given Path ->"+str(delpaths))
            cls.logger.info("Test execution Completed for all test methods witinin: "+cls.__name__)
        
    def logInfo(self, streamIndicator: str, stream):
        if (isinstance(stream,str)):
            self.logger.info(streamIndicator+stream)
        else:
            self.logger.info(streamIndicator+str(stream))

    def logDebug(self, streamIndicator: str, stream):
        if (isinstance(stream,str)):
            self.logger.debug(streamIndicator+stream)
        else:
            self.logger.debug(streamIndicator+str(stream))

    def logError(self, streamIndicator: str, stream):
        if (isinstance(stream,str)):
            self.logger.error(streamIndicator+stream)
        else:
            self.logger.error(streamIndicator+str(stream))

class genericValidations:

    def __init__(self) -> None:
        self.loggerObj=TestBaseClass()

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

  
    def getDataFromFieldPathPydanticPath(self,path:str,jsonMap:any):
        try:
            paths = path.split(".")
            iterator=0
            while iterator < len(paths): 
                key = paths[iterator]
                if "[" in key :
                    key_index = key.split("[")          
                    value = getattr(jsonMap, key_index[0])     
                    iterator+=1
                    jsonMap = value[int(key_index[1].split("]")[0])]
                    temp = value
                else:             
                    value = getattr(jsonMap, key)     
                    iterator+=1
                    jsonMap = value
                    temp = value
            return temp
        except (Exception ,TypeError,ValueError) as error:
            self.loggerObj.logError("Json/Pydantic Path is Invalid, Error occured ->",error)
            return None
    
    def getDataFromFieldPathJsonPath(self,path:str,jsonMap:dict):
        try:
            data = benedict(jsonMap)
            value=data.get(path)
            return value
        except (Exception ,TypeError,ValueError) as error:
            self.loggerObj.logError("Json/Pydantic Path is Invalid, Error occured ->",error)
            return None

    def dataConverter(self,dataToconvert,dataform):
        convertedDataType='empty_response_data'
        match dataform:
            case 'str':
                convertedDataType=str(dataToconvert)
            case 'int':
                convertedDataType=int(dataToconvert)
            case 'float':
                convertedDataType=float(dataToconvert)
            case 'bool':
                convertedDataType=bool(dataToconvert)
        return convertedDataType

    def getDataType(self,data:any):
        try:
            typeOfdata=str(type(data))
            dataType=typeOfdata.split("class")[1].split(">")[0].lstrip().split("'")[1]
            return dataType
        except(Exception) as error:
            self.loggerObj.logError("Error Occured ->"+str(error),"")
            return None
    def evalExp(self,jsondata:dict,expression:str):
        try:
            results=[]
            query = jp.parse(expression)
            for match in query.find(jsondata):
                results.append(match.value)
            return results
        except(Exception) as error:
            value=JsonPath(jsondata, expression).load()
            return value    
    def convertStringListToIntList(self,value:str):
        listvaluestr=value.split("[")[1].split("]")[0].split(":")
        try:
            convertedlist=list(map(int, listvaluestr))
            return convertedlist
        except (Exception ,ValueError) as error:
            print("Given values can't be converted to Integer List ,Error occured ->"+error)
            return None
        
    def convertStringListTofloatList(self,value:str):
        listvaluestr=value.split("[")[1].split("]")[0].split(":")
        try:
            convertedlist=list(map(float, listvaluestr))
            return convertedlist
        except (Exception ,ValueError) as error:
            print("Given values can't be converted to Integer List ,Error occured ->"+error)
            return None
        
    def convertToList(self,stringList:str,dataType:str):
        convertedlist = []
        if stringList.startswith("[["):
            value = stringList[1:-1]
            convertedlist.append(value)
        else:
            if stringList.startswith("["):
                value1=stringList.split("[")[1].split("]")[0].split(",")
                value = [','.join(value1)]
            else:
                #stringListnew="["+stringList+"]"
                #value=stringListnew.split("[")[1].split("]")[0].split(",")
                value = [stringList]
            match dataType:
                case 'str': 
                    convertedlist=list(map(str, value))
                case 'int':
                    convertedlist=list(map(int, value))
                case 'bool':
                    convertedlist=list(map(bool, value))
                case 'float':
                    convertedlist=list(map(float, value))
                case 'NoneType':
                    convertedlist=list(map(str, value))
        return convertedlist

    def validateNull(self,value,feildPath:str):
        value = value[0] if type(value) == type([]) else value
        if value == '':
            value = None
        validationValue=check.is_none(value,"Value is Not Null "+str(feildPath))
        return validationValue
    
    def validateNotNull(self,value,feildPath:str):
        if value == '':
            value = None
        validationValue=check.is_not_none(value,"Value is Null "+str(feildPath))
        return validationValue

    def ValidateEqual(self,Value_0,value_1,feildPath:str):
        validationValue=check.equal(Value_0,value_1,"Values is Not Equal: "+str(feildPath))
        return validationValue
    
    def ValidateGreaterThanZero(self,value,feildPath:str):
        if type(value) in [type(''),type(1),type(1.0)]:
            try:
                intvalue=float(value)
                validationValue=check.greater(intvalue,0.00,"Value is Less than than 0 "+str(feildPath))
                return validationValue
            except (Exception) as ex:
                print("the value given is not parsable to int, error: ",ex)
                return None
        else:
            print("Value type is not matching with int ,str or float")
    
    def ValidatecheckBoolTrue(self,value,feildPath:str):
        validationValue=check.is_true(value,"Value is not True "+str(feildPath))
        return validationValue
    
    def ValidatecheckBoolFalse(self,value,feildPath:str):
        validationValue=check.is_false(value,"Value is not False "+str(feildPath))
        return validationValue
    
    def ValidatecheckBool(self,value,feildPath:str):
        validationValue=check.is_instance(value,(bool),"Value is not Boolean "+str(feildPath))
        return validationValue
    
    def ValidatecheckBoolForExpression(self,responsedata,feildPath:str):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_instance(data,(bool),"Value is not Boolean"))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
    
    def ValidatecheckBoolFalseForExpression(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_false(data,"Value is not False"))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
    def validateMriResponse(self,jsonResponse,fieldPath,mriData,mriValidationkey):
        if fieldPath == 'routesV4':
            result = set()
            requestURL = mriData[2]
            srcId = requestURL.split("/")[7]
            result.add(self.ValidateGreaterThanZero(int(srcId),"srcId"))
            dstId = requestURL.split("/")[8]
            result.add(self.ValidateGreaterThanZero(int(dstId),"srcId"))
            doj = requestURL.split("/")[9].split("?")[0]
            queryParam = requestURL.split("/")[9].split("?")[1]
            queryParam = queryParam.split("&")
            queryParam = str(queryParam)
            all_present = all(word in queryParam for word in ['groupId','limit','offset'])
            result.add(all_present)
            result.add(self.validateNotNull(doj,"doj"))
            if len(result)==1 and (list(result)[0] == True):
                return  True 
            else:
                return False
        else:
            field = mriValidationkey.split("-")
            if fieldPath == 'requestUrl':
                if mriData[4] in('getMpax','seatLayoutV1'):
                    value = mriData[int(field[0])].split("?")[0]
                else:
                    value = mriData[int(field[0])]
            elif fieldPath == 'httpMethod':
                value = mriData[int(field[0])]
            elif mriValidationkey == 'ClientIp':
                value = mriData[2].split("/")[2]
            else:
                value = mriData[int(field[0])][field[1]]
            #response = self.evalExp(jsonResponse,feildPath)[0]
            if fieldPath == "requestHeaders['CountryInfo']['Languages']":
                jsonResponse = jsonResponse[0]
            return self.ValidateEqual(str(jsonResponse[0]).lower(),str(value).lower(),fieldPath)
    def ValidatecheckGreaterThanZeroExpression(self,responsedata,feildPath:str):
        assertionFlags=[]
        for data in responsedata:
            if type(data) in [type(''),type(1),type(1.0)]:
                try:
                    intvalue=float(data)
                    validationValue=check.greater(intvalue,0.0,"Value is Less than than 0 "+feildPath)
                    return validationValue
                except (Exception) as ex:
                    print("the value given is not parsable to int, error: ",ex)
                    return None
            else:
                print("Value type is not matching with int ,str or float")
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
    
    def ValidateCheckNegative(self,value,feildPath:str):
        if type(value) in [type(''),type(1),type(1.0)]:
            try:
                intvalue=int(value)
                validationValue=check.less(intvalue,0,"Value is non negative: "+str(feildPath))
                return validationValue
            except (Exception) as ex:
                print("the value given is not parsable to int, error: ",ex)
                return None
        else:
            print("Value type is not matching with int ,str or float")

    def ValidateCheckPositive(self,value,feildPath:str):
        if type(value) in [type(''),type(1),type(1.0)]:
            try:
                intvalue=int(value)
                validationValue=check.greater_equal(intvalue,0,"Value is not positive: "+str(feildPath))
                return validationValue
            except (Exception) as ex:
                print("the value given is not parsable to int, error: ",ex)
                return None
        else:
            print("Value type is not matching with int ,str or float")

    def ValidateCheckPositiveForExpression(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            if type(data) in [type(''),type(1),type(1.0)]:
                try:
                    intvalue=int(data)
                    validationValue=check.greater_equal(intvalue,0,"Value is Less than than 0 ")
                    return validationValue
                except (Exception) as ex:
                    print("the value given is not parsable to int, error: ",ex)
                    return None
            else:
                print("Value type is not matching with int ,str or float")
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False

    def ValidateDataInString(self,substring,mainstring,feildPath:str):
        validationValue=check.is_in(substring,mainstring,"Substring not found in main String "+str(feildPath))
        return validationValue
    
    def validateDataInStringForExpression(self,substring,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_in(substring,data,"Substring Not matched in Response data"))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False

    def ValidateInBetweenValue(self,value,responseValue):
        convertedValue=self.convertStringListTofloatList(value)
        upperBounb=convertedValue[1]
        lowerbound=convertedValue[0]
        validationValue=check.between(responseValue,lowerbound,upperBounb)
        return validationValue
    
    def checkSubsubset(self,list1,list2):
        if (list1 is None):
            return False 
        elif len(list1)==0:
            return False
        else:
            value=set(list2) <= set(list1)
            return value
    
    def validateNullForExpression(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_none(data,"Data is Not Null"))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
        
    def validateLengthCheckstring(self,responsedata,feildPath:str):
        lengthData=len(str(responsedata))
        validationValue=check.is_true(lengthData>0,"Length is not greater than zero ,feildPath :"+str(feildPath))
        return validationValue
    
    
    def validateLengthCheckArray(self,responsedata,feildPath:str):
        lengthData=len(responsedata)
        validationValue=check.is_true(lengthData>0,"Length is not greater than zero ,feildPath :"+str(feildPath))
        return validationValue
    
    def validateLengthCheckstringempty(self,responsedata,feildPath:str):
        lengthData=len(responsedata)
        validationValue=check.is_true(lengthData==0,"Length is not zero ,feildPath :"+str(feildPath))
        return validationValue
    
    def validateLengthCheckstringForExpression(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_true(len(str(data))>0,"Length is not greater than zero "))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
        
    def validateLengthCheckstringForExpressionEmpty(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_true(len(data)==0,"Length is not greater than zero "))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False
        
    def validateNotNullForExpression(self,responsedata):
        assertionFlags=[]
        for data in responsedata:
            assertionFlags.append(check.is_not_none(data,"Data is Null"))
        final_value=list(set(assertionFlags))
        if len(final_value)==1 and final_value[0]==True:
            return True
        else:
            return False                    

    def isLMBWindow(self):
        current_time = datetime.now().time()
        start_time = time(17, 0, 0)
        end_time = time(23, 59, 59)
        if start_time <= current_time <= end_time:
            return True
        else:
            return False
        
    def validateAutoExpand(self,jsonResponse):
        inventoryValues = []
        jsonres={}
        for rtc in jsonResponse["inventories"]:
            if("RTC" in rtc["travelsName"]):
                inventoryValues.append(rtc)
        jsonres["inventories"]=inventoryValues
        res = self.sortvaldationobj.check_DEPT_TIME(jsonres)
        if res==False:
            return res
        groupJsonValue = jsonResponse["metaData"]["sections"][0]["groups"]
        for value in range(len(groupJsonValue)):
            if(groupJsonValue[value]["groupExpandType"]!=0):
                count = len([i for i in jsonResponse["inventories"] if i["operatorId"]==groupJsonValue[value]["operatorId"]])
                if groupJsonValue[value]["count"] != count:
                    return False
        for index in range(len(jsonres["inventories"])):
            if jsonres["inventories"][index]["operatorId"] != jsonResponse["inventories"][index]["operatorId"]:
                return False
        return True
    
    def calculate_discount(self,seats,offer_percentage):
        original_seat_price = seats['OP']
        discount_price = original_seat_price * offer_percentage / 100
        discount_price = original_seat_price -  discount_price
        return discount_price
    
    def get_seatlayout_version(self,jsonResponse:dict):
        if jsonResponse.get("services"):
            sl_version = 2
        else: 
            sl_version = 1
        return sl_version          
    def validateRedDeal(self,jsonResponse:dict):
        sl_version = self.get_seatlayout_version(jsonResponse)
        offer_percentage = 20
        if sl_version == 2:
            seatList = jsonResponse['services'][0]['seatlist']
            for seats in seatList:
                discount_price = self.calculate_discount(seats,offer_percentage)
                discounted_seat_price = seats['DP']

                if  discount_price != discounted_seat_price:
                    return False,seatList
        else:
            seatList = jsonResponse['seatlist']
            for seats in seatList:
                discount_price = self.calculate_discount(seats,offer_percentage)
                discounted_seat_price = seats['DP']
                if  discount_price != discounted_seat_price:
                    return False,seatList
    
        return True,seatList

    def getValidatedFieldValue(self,datafromCsv:dict,jsonResponse,tupleIndextosue=1,csvtestData={},subApiName={},mriData={},headers="empty"):
        finalMap={}
        if len(datafromCsv)>0 and datafromCsv is not None:
            for keys,values in datafromCsv.items():
                validationvalueHolder={}
                feildPath=str(values['FieldPath'])
                isexpression=values['Type']
                checkExist=values['checkExist'] if values.get('checkExist') else 'no'
                if checkExist.lower() == 'yes':
                    value,response = self.ValidateCheckExist(jsonResponse,feildPath)
                    validationvalueHolder['checkExist']=value
                else:                
                    if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))) and (type(jsonResponse)==type({}) or type(jsonResponse)==type([])):
                        #retrieve the value from csvData and replace in the field path
                        #eg: $.tickets[?(@.id=={optionId})]['tags'][0] replace optionId with optionId from csvData
                        if '{' in feildPath:
                            fieldName =  feildPath.split('{')[1].split('}')[0]
                            fieldValue = csvtestData[tupleIndextosue][fieldName]
                            #feildPath = feildPath.format(fieldName=fieldValue)
                            feildPath = feildPath.split('{')[0] + fieldValue + feildPath.split('}')[1]   
                        ResponseData=self.evalExp(jsonResponse,feildPath)
                        tolog="JsonPathExpression {path} has retrieved value = {data} from JsonResponse".format(path=feildPath,data=ResponseData)
                        if len(ResponseData) == 0:
                            ResponseData = [None]
                    else:
                        if feildPath == "None":
                            ResponseData = [None]
                        elif (type(jsonResponse)==type({}) or type(jsonResponse)==type([])):
                            ResponseData=self.getDataFromFieldPathJsonPath(feildPath,jsonResponse)
                            tolog="JsonPath {path} has retrieved value = {data} from JsonResponse".format(path=feildPath,data=ResponseData)
                        else:
                            ResponseData=self.getDataFromFieldPathPydanticPath(feildPath,jsonResponse)
                        if ResponseData == None:
                            ResponseData = [None]
                    responseDataType=self.getDataType(ResponseData)
                for subkeys in values:
                    if values[subkeys].lower() in ["skip",'']:
                        continue
                    else:
                        csvdata=values[subkeys]
                        match subkeys:
                            case "IsNull":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateNullForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value=self.validateNull(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value
                            case "IsNotNull":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateNotNullForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value=self.validateNotNull(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value
                            case "Valuematch":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    try:
                                        dataType=self.getDataType(ResponseData[0])
                                        convertedCsvData1=self.convertToList(csvdata,dataType)
                                        convertedCsvData = []
                                        for i in range(0,len(convertedCsvData1)):
                                            convertedCsvData.append(convertedCsvData1[i])
                                        value_1=self.checkSubsubset(ResponseData,convertedCsvData)
                                        validationvalueHolder[subkeys]=value_1
                                    except(IndexError,Exception) as error:
                                        value_1=False
                                else:
                                    convertedData=self.dataConverter(csvdata,responseDataType)
                                    value_2=self.ValidateEqual(convertedData,ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_2
                            case "GreaterThanZero":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value_1=self.ValidatecheckGreaterThanZeroExpression(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                                else:
                                    value_1=self.ValidateGreaterThanZero(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                            case "checkBool":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value_1=self.ValidatecheckBoolForExpression(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                                else:
                                    value_1=self.ValidatecheckBool(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                            case "checkBoolTrue":
                                value_1=self.ValidatecheckBoolTrue(ResponseData,feildPath)
                                validationvalueHolder[subkeys]=value_1
                            case "checkBoolFalse":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value_1=self.ValidatecheckBoolFalseForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value_1
                                else:
                                    value_1=self.ValidatecheckBoolFalse(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                            case "CheckNegative":
                                value_1=self.ValidateCheckNegative(ResponseData,feildPath)
                                validationvalueHolder[subkeys]=value_1
                            case "CheckPositive":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value_1=self.ValidateCheckPositiveForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value_1
                                else:
                                    value_1=self.ValidateCheckPositive(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                            case "InBetweenValue":
                                value_1=self.ValidateInBetweenValue(csvdata,float(ResponseData))
                                validationvalueHolder[subkeys]=value_1
                            case "SubstringSearch":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateDataInStringForExpression(csvdata,ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value_1=self.ValidateDataInString(csvdata,ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value_1
                            case "checkLength":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateLengthCheckstringForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value=self.validateLengthCheckstring(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value
                            case "checkLengthZero":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateLengthCheckstringForExpression(ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value=self.validateLengthCheckstring(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value
                            case "checkArrayLength":
                                value=self.validateLengthCheckArray(ResponseData,feildPath)
                                validationvalueHolder[subkeys]=value
                            
                            case "checkLengthzero":
                                if ((isexpression.lower() not in ['']) or (feildPath.startswith("$"))):
                                    value=self.validateLengthCheckstringForExpressionEmpty(ResponseData)
                                    validationvalueHolder[subkeys]=value
                                else:
                                    value=self.validateLengthCheckstringempty(ResponseData,feildPath)
                                    validationvalueHolder[subkeys]=value
                            case "checkRedDeal":
                                redDealType = str(feildPath).lower()
                                if redDealType == "percent_red_deal":
                                    value,ResponseData=self.validateRedDeal(jsonResponse)
                                    validationvalueHolder[subkeys]=value
                            case "ferry_redDeals":
                                api=values['Api'] 
                                value=self.validateferry_redDeals(jsonResponse,feildPath,csvtestData,api)
                                validationvalueHolder[subkeys]=value
                            case "mriValidation":
                                    mriValidationkey = values['mriValidationKey']
                                    value=self.validateMriResponse(ResponseData,feildPath,mriData,mriValidationkey)
                                    validationvalueHolder[subkeys]=value
                            case "autoExpandValidation":
                                value = self.validateAutoExpand(jsonResponse)
                                validationvalueHolder[subkeys]=value
                            case "empty":
                                pass
                        finalMap[feildPath]=validationvalueHolder
            return finalMap
        else:
            return finalMap
    def validateValues(self,validationValues:dict):
        validationList=[]
        for keys in validationValues:
            for subKeys in validationValues[keys]:
                validationList.append(validationValues[keys][subKeys])
        uniqueVal=list(set(validationList))
        return uniqueVal