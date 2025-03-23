import mysql.connector
from os import environ
from dotenv import load_dotenv
import utils.legacy_util_functions.dbConnectionUtils  as template
from utils.legacy_util_functions.legacy_validation_checker import TestBaseClass as tb

filepath=".env"
load_dotenv(filepath)

class dbUtils:

    def __init__(self) -> None:
        self.tb_o=tb()

    def executeQueryPerzDB(self,query:str):
        data=[]
        mydb = mysql.connector.connect(
        host= environ.get('PERZ_HOST'),
        user= environ.get('PERZ_USERNAME'),
        password= environ.get('PERZ_PASSWORD'),
        database= environ.get('PERZ_DATABASE')
        )
        cursorConnection=mydb.cursor()
        print("query->",query)
        cursorConnection.execute(query)
        for item in cursorConnection:
            data.append(item)
        return data
    
    def executeQueryPerzDBRBOffer(self,query:str):
        data=[]
        mydb = mysql.connector.connect(
        host= environ.get('PERZ_HOST'),
        user= environ.get('PERZ_USERNAME'),
        password= environ.get('PERZ_PASSWORD'),
        database= environ.get('RB_OFFER_DATABASE')
        )
        cursorConnection=mydb.cursor()
        print("query->",query)
        cursorConnection.execute(query)
        for item in cursorConnection:
            data.append(item)
        return data
    
    def executeQueryAuthDB(self,query:str):
        data=[]
        mydb = mysql.connector.connect(
        host= environ.get('AUTH_HOST'),
        user= environ.get('AUTH_USERNAME'),
        password= environ.get('AUTH_PASSWORD'),
        database= environ.get('AUTH_DATABASE')
        )
        cursorConnection=mydb.cursor()
        cursorConnection.execute(query)
        for item in cursorConnection:
            data.append(item)
        return data

    def getOtpfromperzDB(self,mobile_number):
        otp_query = template.GET_OTP.format(mobile_number)
        self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data[0]
    
    def getOtpfromperzDBV2(self,mobile_number):
        otp_query = template.GET_OTP_V2.format(mobile_number)
        self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data[0]
    
    def getv2_uid_user_master(self,mobile_number):
        otp_query = template.GET_v2_uid_user_master.format(mobile_number)
        self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data
    
    def get_uid_user_master(self,mobile_number):
        otp_query = template.GET_uid_user_master.format(mobile_number)
        self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data
    
    def cotravellers(self):
        otp_query = template.GET_cotravellers.format()
        self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data
    
    def validateauth(self,token):
        otp_query = template.GET_validateauth.format(token)
        #self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryAuthDB(otp_query)
        return data
    
    def getUserDetails(self,userId):
        otp_query = template.GET_validateuserDetails.format(userId)
        #self.tb_o.logInfo("Query to Execute: ",otp_query)
        data=self.executeQueryPerzDB(otp_query)
        return data
    
if __name__=='__main__':
    dbo=dbUtils()
    dbo.getOtp("919894726932")