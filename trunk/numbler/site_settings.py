# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

# global settings specific to your site implementation

"""
this module is for all of your site setting information that is relevant to your installation.

You can set the properties in this file or modify it to include those
settings from elsewhere.

Example of importing settings from another location (recommended):
from numblerbiz.settings import *

Available properties:

amazon_access_key: the API key for using the amazon web service
amazon_associateTag: tag passed to amazon


"""

settings = {}

# put your own settings here like this:
# from numblerbiz.settings import *

import socket

# don't modify the default settings - add your import statement abvove

_defaults = {
    'amazon_access_key':'12345',
    'amazon_associateTag':'12345',
    'ebay': {
    # sign up for the EBAY API program to get these properties
    'url' : 'https://api.ebay.com/ws/api.dll',
    'DevID':'12345',
    'AppID':'12345',
    'CertID':'12345',
    # USER auth token (generate from the ebay site)
    'authtoken':"foo"
    },
    # domain for managing emails - you probably want to override this
    'servername':socket.getfqdn(),
    # the name of your organization
    'org':'Numbler.org',
    # email address for your users
    'support_mail':'support@numbler.org',
    'smtpserver':'localhost'
}

for key,item in _defaults.items():
    if key not in settings:
        settings[key] = item
        



