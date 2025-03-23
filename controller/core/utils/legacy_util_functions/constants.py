#constant
from enum import Enum

class apiConstant(Enum):
    HTTPVERSION="httpVersion"
    BASEURL="baseurl"
    PATH="path"
    PATHPARAMS="pathParams"
    _VERSION="version"
    _REQUEST_TYPE="requestType"

class anotherClass(Enum):
    pass

class addOnsData(Enum):
    discount_Percentage_rg_2_48 = "9"
    discount_Percentage_rg_48_168 = "10"
    discount_Percentage_rg_168_0 = "11"
    discount_Percentage_rg_idn = "8.88"
    discount_Percentage_rg_india_0_24 = "8"
    discount_Percentage_rg_india_24_48 = "8"
    discount_Percentage_rg_india_48_72 = "9"
    discount_Percentage_rg_india_72_0 = "9.5"
    RAP_INSURANCE_PRICE = "0.51"

class card_details(Enum):
    card_number = '4712280200076452'
    name = 'akash'
    card_exp_month = '12'
    card_exp_year = '2029'
    security_code = '649'
    first_name = 'test'
    last_name = 'test'
    email = 'ashton.c@redbus.com'
    phone = '919148382577'
    bank_id = '182'
    bank_code = 'Bank Code'
    offer_key = 'PaaS offer key'
    DeviceSessionId = 'vghs6tvkcle931686k1900o6e1'
    Cookie = '117dd679-c430-4796-b7de-f84ca4132d4f636130986361322047'
    PaymentMethod = 'MASTERCARD'
    UserAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    Language = 'en'

class neon_details(Enum):
    OauthEmail = "ashton.c@redbus.com"
    OauthAccessToken = "Qfl32DuxdVWVa6W/VtbD4rivCCI="
    OauthExpires = "1736943463"

class card_details_khm(Enum):
    card_number = '4712280200045143'
    name = 'akash'
    card_exp_month = '02'
    card_exp_year = '2029'
    security_code = '950'
    first_name = 'test'
    last_name = 'test'
    email = 'akash.d@redbus.com'
    phone = '918638033565'
    bank_id = '308'
    bank_code = 'Bank Code'
    offer_key = 'PaaS offer key'
    DeviceSessionId = 'vghs6tvkcle931686k1900o6e1'
    Cookie = '117dd679-c430-4796-b7de-f84ca4132d4f636130986361322047'
    PaymentMethod = 'MASTERCARD'
    UserAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    Language = 'en'

class Omega(Enum):
    latam_end_point = "http://omega-latam-public.redbus.com:8001/"
    sea_end_point = "http://10.5.30.215:8001/"