import requests,json

class requestClient:

    setup_test_data={}
    setup=""
    
    def __init__(self):
        pass

    def request(self,request_type:str,url,headers,payload_data=None):
        if request_type.lower() == "post":
            response = requests.post(url,headers=headers,data=payload_data)
        elif request_type.lower() == "get":
            response = requests.get(url,headers=headers)
        elif request_type.lower() == "delete":
            response = requests.delete(url,headers=headers)
        elif request_type.lower() == "patch":
            response = requests.patch(url,headers=headers,data=payload_data)
        elif request_type.lower() == "put":
            response = requests.put(url,headers=headers,data=payload_data)
        else:
            response = None
        return response,response.elapsed
    
    def generateCURL(self,request_type,url,headers,payload_data):
        headers_str = ' '.join(['-H "{}: {}"'.format(k, v) for k, v in headers.items()])
        data_str = json.dumps(payload_data)
        if request_type in ("post","put"):
            curl_command = f"curl --location '{url}' {headers_str} --data '{data_str}'"
        else:
            curl_command = f"curl --location '{url}' {headers_str}"
        return curl_command
    
class StatusCodes:
    STATUS_200 = '200'
    STATUS_404= '404'