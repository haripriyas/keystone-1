==================
OpenStack Keystone
==================

Keystone provides authentication, authorization and service discovery
mechanisms via HTTP primarily for use by projects in the OpenStack family. It
is most commonly deployed as an HTTP interface to existing identity systems,
such as LDAP.

Developer documentation, the source of which is in ``doc/source/``, is
published at:

    http://docs.openstack.org/developer/keystone/

The API specification and documentation are available at:

    http://specs.openstack.org/openstack/keystone-specs/

The canonical client library is available at:

    https://git.openstack.org/cgit/openstack/python-keystoneclient

Documentation for cloud administrators is available at:

    http://docs.openstack.org/

The source of documentation for cloud administrators is available at:

    https://git.openstack.org/cgit/openstack/openstack-manuals

Information about our team meeting is available at:

    https://wiki.openstack.org/wiki/Meetings/KeystoneMeeting

Bugs and feature requests are tracked on Launchpad at:

    https://bugs.launchpad.net/keystone

Future design work is tracked at:

    http://specs.openstack.org/openstack/keystone-specs/#identity-program-specifications

Contributors are encouraged to join IRC (``#openstack-keystone`` on freenode):

    https://wiki.openstack.org/wiki/IRC

For information on contributing to Keystone, see ``CONTRIBUTING.rst``.

==================
Custom Auth
==================
Custom auth uses two factor authentication that uses OTP along with usual username/password authentication. It integrates Twilio with OpenStack Keystone and Horizon for sending OTP to the users as SMS. This is an OTP authentication plugin created using Openstacks Keystone V3.
This plugin provides an extra layer of security, which will grant access to the horizon only if the user is authenticated with OTP as well as username/password.

We have used Twilio service for sending the sms with OTP code. Only users with registered phone number in keystone DB will be authenticated with this plugin.

This plugin will authenticate the user in 2 Steps:

In first step user will be authenticated based on the username and password which is registered with Openstacks. On successful authenbtication, an OTP will be generated and sent to user's registered phone number. 

In the second step user needs to enter the OTP. This will be validated and access is granted based on that.

When user is trying to authenticate with wrong OTP 3 times , user will be blocked from Login to his/her account for a lockout period of 24hours.

Also OTP will be valid only for 30 seconds, after 30 seconds OTP will be expired. This time limit can be changed in the configuration.

======
Setup
======
1. Setup Horizon and Keystone
2. Run requirement.txt
3. Set the keystone.conf path in keystone/identity/backends/configuration.py 
4. Set the Twilio credentials in keystone/identity/backends/configuration.py 
5. Also set the default OTP expiration settings in authTimeoutDuration.
6. Restore the mysql dump to the keystone database using keystone_customtables.sql





