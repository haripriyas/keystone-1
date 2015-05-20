'''
Created on 20-May-2015
Test cases for OTP authentication
'''

import unittest
import urllib2
from keystone.identity.backends.configuration import *

#Demo user
username = "murali"
password = "murali"
user_id = "8d4ae7a853ee4508b371263a2c8db337"

conf = Config()

db = conf.getDBConnection()
cursor = db.cursor()

class TestStringMethods(unittest.TestCase):

    def test_login(self):
        data = '{"auth": {"identity": { "methods": ["password"],"password": {"user": {"name": "' + username + '",  "domain": { "id": "default" },  "password": "' + password + '"    }       }       }       }       }'
        url = 'http://localhost:5000/v3/auth/tokens'
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        try :
                f = urllib2.urlopen(req)
                #for x in f:
		#	print ""
                        #print(x)
                f.close()
        except Exception, e :
                        print e
			self.assertEqual(1,0, "Login failed") #To identify failed case 
                        return False
	otpVal = getOTPFromDB() 
	self.assertEqual(test_otp_auth(otpVal),True, "OTP authentication success")
	db.close()


def getOTPFromDB() :
        selectOtpSql = "SELECT OTPvalue, time FROM otp where userid = '"+str(user_id)+"'"
        cursor.execute(selectOtpSql)
        result = cursor.fetchone()
        savedOtp = result[0]
        return savedOtp
    
    
def test_otp_auth(otpVal):
        
        
        data = '{ "auth": { "identity":{ "otp": {"otp_value": "' + str(otpVal) + '"}, "methods": ["password","otp"],"password": {"user": {"name": "' + username + '","domain": { "id": "default" },"password": "'+password+'"}} } }  }'
        url = 'http://localhost:5000/v3/auth/tokens'
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        try :
                f = urllib2.urlopen(req)
                for x in f:
			print ""
                        #print(x)
                f.close()
        except Exception, e :
                        #print e
                        return False
                    
	return True                  

if __name__ == '__main__':
    unittest.main()
