"""
This script consists of all the functions which 
is performing various DB operations
"""

from __future__ import absolute_import
import pam
from . import sql
from twilio.rest import TwilioRestClient
from oslo_log import log
from keystone.auth.plugins.otp import *
from keystone.identity.backends.configuration import *

conf = Config()

# for logging 
LOG = log.getLogger(__name__)

class DbBackend:
    """
    This class contains all the functions for performing 
    necessary querying
    """

    def insertOtp(self,otp,userid) :
        """
        Function for inserting OTP in to table keystone.otp 
        for validation purpose. OTP will be inserted into
        table on successful login with Username and 
        Password
        """
        
        LOG.info("Inside insert OTP function, for inserting OTP value in table")
        
        # for datetime operations
        import datetime
        
        # for formatting the date and time as needed
        f = '%Y-%m-%d %H:%M:%S'
        current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_current = datetime.datetime.strptime(current, f)

        db = conf.getDBConnection()

        # selecting count of userid from table for inseting into table


        Identity = sql.Identity(userid)

        total_row_otp_result = Identity.otpCountQuery(userid)

        total_row_otp = total_row_otp_result[0]

	print total_row_otp

        # If OTP entry already exists update the field value
        if total_row_otp:
		print "update section"
                Identity = sql.Identity(userid)
                updateOtp = Identity.updateOtpQuery(userid,otp)

        # if no OTP entry exists Insert new row in it
        else:

		print "insert section"
		Identity = sql.Identity(userid)
		inserOtp = Identity.insertOtpQuery(userid,otp)
        return True


    def blockUserLogin(self,userid):      
        """
        Function to decide whether user is blocked.
        During login, checks whether the user is blocked by 
        checking user entry in faileduser table in keystone DB. 
        If yes , then time difference(between current and blocked time) is less than 24 hours
        then it will block user from logging in. else it will allow
        user to log in.
        """

        LOG.info("Inside blockuserlogin function, for fetching the details for blocking user")

        db = conf.getDBConnection()

	time_user_blocked = None	
        Identity = sql.Identity(userid)

        time_user_blocked_result = Identity.blockUserLoginQuery(userid)

        print time_user_blocked_result

        if time_user_blocked_result:
		time_user_blocked = time_user_blocked_result[0]

       		print time_user_blocked	


        # when user blocked time exists
        if time_user_blocked:

                # for datetime operations
                import datetime
                import math

                # for formatting the date and time as needed
                f = '%Y-%m-%d %H:%M:%S'
                current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_current = datetime.datetime.strptime(current, f)
                hoursdiffseconds = 0
                hoursdiffseconds  = math.floor(((new_current - time_user_blocked).total_seconds()))

                # if difference between current time and block time is less than 24 hours
                if hoursdiffseconds < 86400:

                        return False
        db.close()
        return True


    def selectAndVerifyOtp(self,otp,userid) :
        """
        Function for selecting OTP from DB table for authentication.
        It will select The OTP from table(keystone.otp) 
        and decides the action by comparing it with that of submitted otp.
        Also checks whether OTP is expired using the defined time limit.
        """
        
        LOG.info("Check the submitted OTP with the one saved in DB")
        db = conf.getDBConnection()
        
        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        result = None
        userSubmittedOtp = otp
        
        # for datetime operations
        import datetime

        # for formatting the date and time as needed
        f = '%Y-%m-%d %H:%M:%S'
        current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_current = datetime.datetime.strptime(current, f)


	print "newcurremt"

	print new_current


	print userid
	Identity = sql.Identity(userid)

	print Identity

        savedOtpResult = Identity.selectOTP(userid)

	if savedOtpResult:
	
		savedOtp = savedOtpResult[0]

        	savedTime = savedOtpResult[1]


        diff = new_current - savedTime
        LOG.info( diff.total_seconds())


        LOG.info(authTimeoutDuration)
        db.close()
        # when totlal difference is greater than authtimeout duration
        if diff.total_seconds() > authTimeoutDuration:
                LOG.info("OTP authentication timed out")

                # for adding data to table on OTP expired case
                self.saveFailedData(userid) 
                raise exception.Unauthorized()

        # If user submitted OTP and OTP from DB matches, user will authenticated.
        LOG.info(savedOtp)
        LOG.info(userSubmittedOtp)
        
        # If cubmitted OTP and OTP from DB matches
        if str(savedOtp).__eq__(str(userSubmittedOtp)) :
                LOG.info("OTPs matching, authentication success.")
                self.clearTableDataOnSuccess(userid)
                return True

        # Submitted OTP and OTP from DB doesn't match
        else :
                LOG.info("OTPs NOT matching, authentication failure.")
                self.saveFailedData(userid)
                raise exception.Unauthorized()
                raise exception.ValidationError(attribute='id',
                                    target="otp")
                return False


    def clearTableDataOnSuccess(self,userid):
        """
        Flushing Table data on Successful Login.
        When user is logging in correctly all the failed data from table for
        particular user will be flushed (keystone.failedusers, faillogin).
        That will be executed after succesful OTP authentication 
        or after succesful login with username and password(after lockout period). 
        """ 
        
        LOG.info("Clear table data on sucess, for clearing table data on successful attepmt")

        db = conf.getDBConnection()
        
        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        # deleting users details from faillogin table
        sqldeletefaillogin = "delete from faillogin where userid = '"+str(userid)+"'"
        try:
                cursor.execute(sqldeletefaillogin)
                db.commit()
        except:
                db.rollback()

        # deleting users details failed users table
        sqldeletefailedusers = "delete from failedusers where userid = '"+str(userid)+"'"
        try:
                cursor.execute(sqldeletefailedusers)
                db.commit()
        except:
                db.rollback()
        db.close()

    def saveFailedData(self,userid) :
        """
        For saving failed data in tables on Wrong OTP attempts.
        When user is entering the wrong OTP each attempts will be entered into keystone DB.
        When user is Attempting wrong OTP, for first two attempts, it will be 
        entered into faillogin table.
        During 3rd wrong attempt user entry will be added into failedusers
        table, which has all users who are locked out.
        When the locked out period is over(ie 24hrs for us) users details will be 
        deleted from table (during the next successful login), and allows the further logins.
        """

        LOG.info("For saving failed data")
        db = conf.getDBConnection()
        
        # prepare a cursor object using cursor() method
        cursor = db.cursor()

        # for datetime operations
        import datetime

        # for formatting the date and time as needed
        f = '%Y-%m-%d %H:%M:%S'
        current = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_current = datetime.datetime.strptime(current, f)

        # for getting the total count of failed attempts for user in user login table
        userfaillogcount = "select count(userid) from faillogin where userid = '"+str(userid)+"'"
        cursor.execute(userfaillogcount)
        res = cursor.fetchone() 
        total_rows_userfail = res[0]

        # for getting the failed user last attempt time
        getlasttime = "select time from failedusers where userid = '"+str(userid)+"' order by time desc limit 1"
        cursor.execute(getlasttime)
        lasttime = cursor.fetchone() 

        hoursdiffseconds = 0

        # last time exists
        if lasttime :
                lasttime_res = lasttime[0]

                # calculating difference
                hoursdiffseconds  = math.floor(((new_current - lasttime_res).total_seconds()))

        # difference greater than 24 hours then delete all the entries for user
        if hoursdiffseconds > 86400 :

                # deleting users details
                sqldeletefaillogin = "delete from faillogin where userid = '"+str(userid)+"'"    
                try:            
                        cursor.execute(sqldeletefaillogin)            
                        db.commit()            
                except:               
                        db.rollback()                        
 
                # deleting users details
                sqldeletefailedusers = "delete from failedusers where userid = '"+str(userid)+"'"        
                try:            
                        cursor.execute(sqldeletefailedusers)            
                        db.commit()            
                except:               
                        db.rollback()                        
    
                # inserting new entry (during wrong OTP entry)
                sqlinsertnew = "INSERT INTO faillogin(userid) VALUES ('"+str(userid)+"')"        
                try:            
                        cursor.execute(sqlinsertnew)            
                        db.commit()            
                except:               
                        db.rollback()                        

        # else part if there is no time difference greater than 24 hours        
        else:

                # until 2 attempts of user trying with wrong otp
                if total_rows_userfail < 2 :
    
                        # inserting record in to faillogin table     
                        sqlinserttofailrecord = "INSERT INTO faillogin(userid) VALUES ('"+str(userid)+"')"         
                        try:            
                                cursor.execute(sqlinserttofailrecord)            
                                db.commit()            
                        except:               
                                db.rollback()                        

                # greater than 2 wrong attempts             
                else:            
    
                        # number of failed attempts by user
                        sqlcountfaileduser = "select count(userid) from failedusers where userid = '"+str(userid)+"'"
                        cursor.execute(sqlcountfaileduser)
                        res2 = cursor.fetchone() 
                        countfailusertable = res2[0]

                        # if entry is already there no need to enter again
                        if countfailusertable:
                                db.close()    
                                return 0
    
                        # if no entry have to insert now
                        else:
        
                                # for inserting details in faileduser table(uesrs needs to be blocked)         
                                sqlfaileduserinsert = "INSERT INTO failedusers(userid) VALUES ('"+str(userid)+"')"            
                                try:            
                                        cursor.execute(sqlfaileduserinsert)            
                                        db.commit()            
                                except:               
                                        db.rollback()                        
        db.close()

    def get_def_proj_id(self,user_id):
        """
        Function to get the default project id for the user.
        This is needed for successful user authentication
        """
        
        LOG.info("For getting default project ID")
       
	Identity = sql.Identity(user_id)

        project_id_result = Identity.get_def_proj_id_query(user_id)

        if project_id_result:
	        project_id = project_id_result[0] 
        return project_id
