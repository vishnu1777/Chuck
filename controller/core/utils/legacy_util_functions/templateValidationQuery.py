GET_OTP="""
        SELECT OTP FROM uid_mobile_verification 
        WHERE MobileNo={}
        and IsVerified=0 ORDER BY Id DESC LIMIT 1
    """

GET_OTP_V2="""
        SELECT OTP FROM v2_uid_mobile_verification 
        WHERE MobileNo="{}"
        and IsVerified=0 ORDER BY Id DESC LIMIT 1
    """

GET_v2_uid_user_master="""
        SELECT * FROM v2_uid_user_master 
        WHERE PrimaryMobileNo="{}"
    """

GET_uid_user_master="""
        SELECT * FROM uid_user_master 
        WHERE PrimaryMobileNo="{}"
    """

GET_cotravellers="""
        SELECT * FROM uid_cotraveller 
        WHERE rbUserMasterId=55180336
    """
GET_validateauth="""
        SELECT * FROM auth_token 
        WHERE Token="{}"
    """  

GET_validateuserDetails="""
        SELECT * FROM uid_user_master 
        WHERE UserId="{}"
    """

