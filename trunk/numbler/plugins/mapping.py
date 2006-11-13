from nevow import athena,util

myPackage = athena.JSPackage({
    'Numbler': util.resource_filename('numbler.js','myaccount.js'),
    })
