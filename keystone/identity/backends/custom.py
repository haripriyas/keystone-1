"""
Script for implementation of doing authentication(overriding default),
For password checking , validation , blocking user login,
Generating Twilio SMS
"""

from __future__ import absolute_import
import pam
from . import sql
from twilio.rest import TwilioRestClient
from oslo_log import log
from keystone.auth.plugins.otp import OTP
from keystone.identity.backends.configuration import *
from keystone.identity.backends.db_functions import *

conf = Config()
db = conf.getDBConnection()
cursor = db.cursor()

# for logging 
LOG = log.getLogger(__name__)
dbBackendObj = DbBackend()

class Identity(sql.Identity):
    """
    Custom Identity class for overriding default authentication.
    """
    
    LOG.info("Inside class Identity")

    # for checking password and validation
    def _check_password(self, password, user_ref):
        """
        For password checking and validation,
        Blocking the users from logging in,
        Generating a message to mobile number
        """

        # for getting necessary field values
        username = user_ref.get('name')
        extra = user_ref.get('extra')     
        userid = user_ref.get('id')
        dbBackendObj.blockUserLogin(userid)

        # Check if the current auth works, if yes, go for the OTP generation.
        if super(Identity, self)._check_password(password, user_ref):

                # if user is listed in failedusers table and needs to be blocked
                if not  dbBackendObj.blockUserLogin(userid):
                        return False
                    
                # on successful login cleartabledatas(failed details)
                else:
                        dbBackendObj.clearTableDataOnSuccess(userid)

                # if phone field exists
                if 'phone' in extra  :

                        # twilio authentication details
                        account_sid = twilio_account_sid
                        auth_token  = twilio_auth_token
                        client = TwilioRestClient(account_sid, auth_token)
                        otp = None
                        toPhone = extra['phone']

                        # calling otp generate function
                        otp = self.generateOTP()

                        # for inserting otp in table
                        dbBackendObj.insertOtp(otp,userid)

                        # For sending SMS to user with OTP values
                        sms = client.sms.messages.create(body="Your OTP for openstack login is :" + str(otp) , to=toPhone, from_=str(twilio_from))
                        
                        # If sms sent, return true, else false.
                        if(sms.sid) :
                                return True
                        else :
                                return False
                else :
                        return False 

    # function for generating OTP
    def generateOTP(self) :
        """
        Function to generate OTP
        """
        
        LOG.info("Inside Generate OTP function")
        
        import pyotp
        totp = pyotp.TOTP('base32secret3232')
        optVal = totp.now()
        return optVal
