import csv,os,json,yaml,re,time,sys
import urllib.parse
from  utils.legacy_util_functions.constants import apiConstant as c
from datetime import  timedelta,date
from utils.legacy_util_functions.crud_ops_client import requestClient as rq
from utils.legacy_util_functions.legacy_validation_checker import TestBaseClass as tbc
from utils.legacy_util_functions import commons as utils
import traceback



class RequestBuilder:

    def __init__(self) -> None:
        self.apiConstantname=[e.name for e in c]
        self.apiConstantValue=[e.value for e in c]
        self.constantHashMap= dict(zip(self.apiConstantname, self.apiConstantValue))
        self.rq_obj=rq()
        self.logger=tbc()
        self.flow2filepath="apiConfig/capi/TestcaseListFlow_2.json"
        self.flow_2=self._getDataFromJsonFile(self.flow2filepath)['Flow2']

    def buildRequest(self,apiConfigData:dict,innerinputfilecsv:dict,microServiceName:str,CodebaseName:str,buildUrlString:str,envString:str,TestType:str="",index:int=0):
        try:
            getCodebasedata=apiConfigData['APIConfig']['Codebase'][CodebaseName]
            getsubApidata=getCodebasedata[buildUrlString]['apiData'][envString]
            if TestType in [""]:
                return self._urlDataBuilder(getsubApidata,innerinputfilecsv,microServiceName,CodebaseName,buildUrlString,envString)
            elif TestType in ["Functional"]:
                return self.urlDataBuilderforFullFlowTest(getsubApidata,innerinputfilecsv,microServiceName,CodebaseName,buildUrlString,index)
            else:
                return NotImplementedError
        except(Exception )as error:
            print("error coming here",error)
            traceback.print_exc()
                    
    def _urlDataBuilder(self,getsubApidata,innerinputdatacsv,microServiceName,CodebaseName,buildUrlString,envString):
        generatedOUrl=""
        for keys in self.constantHashMap:
            if keys.startswith("_"):
                continue
            else:
                generatedOUrl+=getsubApidata[self.constantHashMap[keys]]
        apiVersion=getsubApidata[self.constantHashMap['_VERSION']]
        requestType=getsubApidata[self.constantHashMap['_REQUEST_TYPE']]
        for keys in innerinputdatacsv:
            strform="{"+keys+"}"
            if strform=="{doj}":
                dt = date.today()
                td = timedelta(days=int(innerinputdatacsv[keys]))
                doj=dt + td
                generatedOUrlreplaced=self._replaceUsingRegex(strform, str(doj), generatedOUrl)
                generatedOUrl=generatedOUrlreplaced
            else:
                generatedOUrlreplaced=self._replaceUsingRegex(strform, innerinputdatacsv[keys], generatedOUrl)
                generatedOUrl=generatedOUrlreplaced
        generatedOUrl=self._replaceUsingRegex("{version}",apiVersion,generatedOUrl)
        if buildUrlString.lower() not in self.flow_2:
            queryParamsfilePath=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"query",innerinputdatacsv['queryParamsFilePath'])
            headersParams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"headers",innerinputdatacsv['headerFilePath'])
            apiPayloadParams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"payloads",innerinputdatacsv['payloadFilePath'])
            ignoreListparams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"ignoreList",innerinputdatacsv['ignoreList'])
            validationsparam=self.pathBuildObj.buildPathforCSVFiles(microServiceName,CodebaseName,buildUrlString,"validations",innerinputdatacsv['FieldValidation'])
        else:
            queryParamsfilePath=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"query/"+envString,innerinputdatacsv['queryParamsFilePath'])
            headersParams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"headers/"+envString,innerinputdatacsv['headerFilePath'])
            apiPayloadParams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"payloads/"+envString,innerinputdatacsv['payloadFilePath'])
            ignoreListparams=self.pathBuildObj.buildPathforAuxFiles(microServiceName,CodebaseName,buildUrlString,"ignoreList/"+envString,innerinputdatacsv['ignoreList'])
            validationsparam=self.pathBuildObj.buildPathforCSVFiles(microServiceName,CodebaseName,buildUrlString,"validations",innerinputdatacsv['FieldValidation'])
        getQueryParams=self._getDataFromJsonFile(queryParamsfilePath)
        getHeaders=self._getDataFromJsonFile(headersParams)
        getApiPayload=self._getDataFromJsonFile(apiPayloadParams)
        getIgnoreList=self._getDataFromJsonFile(ignoreListparams)["IgnoreList"]
        # getValidationsList=self.csv_reader_obj.loadCSVFile(validationsparam)
        generatedUrlwithQp=self._queryParser(generatedOUrl,getQueryParams)
        generatedMap={"oUrl":generatedUrlwithQp,"responseType":requestType,"headers":getHeaders,"apiPayload":getApiPayload,"IgnoreList":getIgnoreList,"FieldValidation":validationsparam}
        return generatedMap
    
    def urlDataBuilderforFullFlowTest(self,getsubApidata,innerinputdatacsv,microServiceName,CodebaseName,buildUrlString,index):
        try:
            generatedOUrl=""
            for keys in self.constantHashMap:
                if keys.startswith("_"):
                    continue
                else:
                    generatedOUrl+=getsubApidata[self.constantHashMap[keys]]
            apiVersion=getsubApidata[self.constantHashMap['_VERSION']]
            requestType=getsubApidata[self.constantHashMap['_REQUEST_TYPE']]
            for keys in innerinputdatacsv:
                strform="{"+keys+"}"
                if strform=="{doj}":
                    dt = date.today()
                    td = timedelta(days=int(innerinputdatacsv[keys]))
                    doj=dt + td
                    generatedOUrlreplaced=self._replaceUsingRegex(strform, str(doj), generatedOUrl)
                    generatedOUrl=generatedOUrlreplaced
                else:
                    #Add keys if csvData key is not string
                    if keys not in ('amenities','serviceNotes','redDealsData','routeIds','dbresult','coTrevelersDBResult','bpListLatLong','dpListLatLong','authPayload','dpListLatLongCore','bpListLatLongCore'):
                        generatedOUrlreplaced=self._replaceUsingRegex(strform, innerinputdatacsv[keys], generatedOUrl)
                        generatedOUrl=generatedOUrlreplaced
            generatedOUrl=self._replaceUsingRegex("{version}",apiVersion,generatedOUrl)
            queryParamsfilePath=self.pathBuildObj.buildPathforAuxFilesFunctionalFlow(microServiceName,CodebaseName,buildUrlString,"queryParams",self.fullFlowHeplerparser(buildUrlString,innerinputdatacsv['queryParamsFilePath'],index))
            headersParams=self.pathBuildObj.buildPathforAuxFilesFunctionalFlow(microServiceName,CodebaseName,buildUrlString,"headers",self.fullFlowHeplerparser(buildUrlString,innerinputdatacsv['headerFilePath'],index))
            apiPayloadParams=self.pathBuildObj.buildPathforAuxFilesFunctionalFlow(microServiceName,CodebaseName,buildUrlString,"payload",self.fullFlowHeplerparser(buildUrlString,innerinputdatacsv['payloadFilePath'],index))
            validationsparam=innerinputdatacsv['FieldValidation']
            mapformvalidationFiles=utils.transcodeStringIntoMap(validationsparam)
            validationsparam=self.pathBuildObj.buildPathforCSVFilesFunctionalFlow(microServiceName,CodebaseName,buildUrlString,"validations",mapformvalidationFiles)    
            getQueryParams=self._getDataFromJsonFile(queryParamsfilePath)
            getHeaders=self._getDataFromJsonFile(headersParams)
            getApiPayload=self._getDataFromJsonFile(apiPayloadParams)
            generatedUrlwithQp=self._queryParser(generatedOUrl,getQueryParams)
            generatedMap={"oUrl":generatedUrlwithQp,"responseType":requestType,"headers":getHeaders,"queryParams":getQueryParams,"apiPayload":getApiPayload,"FieldValidation":validationsparam}
            return generatedMap
        except(Exception )as error:
            print("error coming here",error)
            traceback.print_exc()              

    def _replaceUsingRegex(self,toReplace:str,replacer:str,mainString:str):
        repalacedStr=re.sub(toReplace,replacer, mainString)
        return repalacedStr
    
    def _getDataFromJsonFile(self,filePath):
        with open(filePath) as json_query:
            file_contents = json_query.read()
            content=json.loads(file_contents)
            return content
        
    def fullFlowHeplerparser(self,buildUrlString,filesString:str,index:int):
        expressiondata=filesString.split("[")[1].split("]")[0].split(",")
        tobesearched=expressiondata[index]
        if buildUrlString in tobesearched:
            return self.parsefilesString(tobesearched)
        
    def parsefilesString(self,filesString:str):
        validationList=filesString.split("->")[1]
        return validationList

    def _queryParser(self,url:str,queryParams:dict):
        url_parts = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(url_parts.query,keep_blank_values=True))
        updated_query_params={**query, **queryParams}
        query.update(updated_query_params)
        url_parts = url_parts._replace(query=urllib.parse.urlencode(query))
        updated_url = urllib.parse.urlunparse(url_parts)
        updated_url = urllib.parse.unquote(updated_url)
        return updated_url
        
    def _headersParser(self,headers:dict):
        parsedHeaders=json.loads(headers)
        return parsedHeaders
    
    def requestWithRetry(self,responseType,requestUrl,headers,payload,max_tries=3):
        for i in range(max_tries):
            try:
                time.sleep(0.5) 
                response,resp_time=self.rq_obj.request(responseType,requestUrl,headers=headers,payload_data=payload)
                return response,resp_time
            except Exception as e:
                self.logger.logInfo(str(e)+"retrying "+requestUrl+" "+str(i+1)+" time","")
                continue

    def generateCurl(self,responseType,requestUrl,headers,payload,max_tries=3):
        headers_str = ' '.join(['-H "{}: {}"'.format(k, v) for k, v in headers.items()])
        data_str = json.dumps(payload)
        data_str = data_str.replace('\\', '')
        if responseType in ("post","put"):
            curl_command = f"curl --location '{requestUrl}' {headers_str} --data '{data_str}'"
        else:
            curl_command = f"curl --location '{requestUrl}' {headers_str}" 
        return curl_command

    def filterhelper(self,data:str):
        constructMap={}
        if len(data)>0:
            temp_2=data.split("[")[1].split("]")[0].split(",")
            for values in temp_2:
                if "payload" in values:
                    constructMap["payloadFilePath"]=values
                elif "query" in values:
                    constructMap["queryParamsFilePath"]=values
                elif "headers" in values:
                    constructMap["headerFilePath"]=values
                elif "ignoreList" in values:
                    constructMap["ignoreList"]=values
                elif "validation" in values:
                    constructMap["FieldValidation"]=values
            return constructMap
        else: 
            return None
        
    def helper_1(self,csvData:dict):
        finalmap={}
        finalMap_2={}
        for data in csvData:
            value=csvData[data]
            if data.startswith("env_"):
                filterdata=self.filterhelper(value)
                finalmap[data]=filterdata
            else:
                finalmap[data]=csvData[data] 
        for keys in finalmap:
            if type(finalmap[keys])!=type(None):
                finalMap_2[keys]=finalmap[keys]
        return finalMap_2
    
    def createCsvDataMap(self,csvData:dict,env_name:str):
        finalMap={}
        filter_1=self.helper_1(csvData=csvData)
        for keys in filter_1:
            if keys.startswith("env_"):
                if keys==env_name:
                    for keys2 in filter_1[keys]:
                        finalMap[keys2]=filter_1[keys][keys2]                      
            else:
                finalMap[keys]=filter_1[keys]
        return finalMap

if __name__=='__main__':
    # input_file_name="apiConfig/capi/pivot/ticketInfo/input/input_1.csv"
    api_config_yaml="apiConfig/capi/FullFlow/apiConfigFiles/pivot/seatLayout.yaml"
    # csv_reader_obj=Utility()
    env_obj=env()
    url_builder_obj=RequestBuilder()
    # input=csv_reader_obj.loadCSVFile(input_file_name)
    apiConfigFile=env_obj.safe_load_yaml_file(api_config_yaml)
    customdata={'ScenarioName': 'ConfirmBooking', 'srcId': '195201', 'destId': '195160', 'doj': '7', 'TupleIndex': '1', 'country': 'india', 'queryParamsFilePath': '[Seatlayout->queryparam_2024_03_04_20_23_30]', 'headerFilePath': '[Seatlayout->headers_2024_03_04_20_23_30]', 'payloadFilePath': '[Seatlayout->payload_2024_03_04_20_23_30]', 'FieldValidation': 'routes:colombia_webDirect_android_1->Seatlayout:sheet_1', 'ChainApi': 'routes->Seatlayout', 'SetFile': 'set_2', 'ReadRow': 'Yes', 'operaterId': '16735', 'RouteId': '458377'}
    print(type(customdata))
    url=url_builder_obj.buildRequest(apiConfigFile,customdata,"capi","Pivot","Seatlayout","env_prod","Functional")
    print(url)
    