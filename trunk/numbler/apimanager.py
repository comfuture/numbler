# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.

from nevow import rend, loaders, appserver,static,guard,inevow,url,flat,stan,util,json,tags as T
from support_pages import NumblerFile

class APIManager(rend.Page):
    """
    Class for managing the API documentation tree.
    """
    

    docFactory = loaders.xmlfile('docmain.xml',templateDir='apidoc')
    child_download = NumblerFile('./apidoc/downloads')

    displayTree = [
        # display name, resource, source file, children
        [u'Overview',u'overview',u'overview.xml'],
        [u'Core Concepts',u'core',u'core.xml',
         [[u'working with sheets',u'sheetmgmt',u'sheetmgmt.xml'],
          [u'operations',u'ops',u'operations.xml'],
          [u'Changed cells',u'changedcells',u'changedcells.xml']
          ]
         ],
        [u'Using the API',u'using',u'using.xml',
         [[u'Authentication',u'authdetailed',u'authdetailed.xml'],
          [u'Access control',u'accesscontrol',u'accesscontrol.xml'],
          [u'limitations',u'limits',u'limits.xml'],
          [u'Error handling',u'apierror',u'apierror.xml']
         ]
         ],
        [u'Using the REST API',u'usingrest',u'usingrest.xml',
         [[u'Common REST Elements',u'commonrest',u'commonrest.xml'],
          [u'XML response format',u'restxmlformat',u'restxmlformat.xml'],          
          [u'REST error response',u'resterror',u'resterror.xml'],
          [u'REST authentication',u'restauth',u'restauth.xml'],
          [u'Operations on a sheet',u'restsheetops',u'restsheetops.xml',
           [[u'GET cell',u'restgetcell',u'restgetcell.xml'],
            [u'GET cell range',u'restgetcellrng',u'restgetcellrange.xml'],
            [u'GET sheet',u'restgetsheet',u'restgetsheet.xml'],
            [u'DELETE cell',u'restdelcell',u'restdelcell.xml'],
            [u'DELETE cell range',u'restdelcellrng',u'restdelcellrng.xml'],
            [u'PUT cells',u'restputcell',u'restputcell.xml']
            ]
           ]
          ]
         ],
        [u'Sample code and SDKs',u'samplecode',u'samplecode.xml',
         [[u'Python',u'pythonsdk',u'pythonsdk.xml']
          ]
         ]
        ]

       
        
    def __init__(self):
        self.getfiles(self.displayTree)


    def getfiles(self,nodes):
        for node in nodes:
            if len(node) == 4:
                self.getfiles(node[3])

            try:
                newpage = rend.Page()
                newpage.docFactory = loaders.xmlfile(node[2],templateDir='apidoc')
            except Exception,e:
                pass
            else:
                self.children[node[1]] = newpage
            

    def stripfiles(self,nodes):
        for node in nodes:
            if len(node) == 4:
                yield [node[0],node[1],list(self.stripfiles(node[3]))]
            else:
                yield [node[0],node[1]]
        

    def render_loadtree(self,ctx,data):
        return T.script(type='text/javascript')[T.raw("""
        addLoadEvent(function() { Numbler.apidoc.loadTree('%s'); });
        """ % json.serialize(list(self.stripfiles(self.displayTree))))]

    def render_content(self,ctx,data):
        return self.children['overview']

    children = {}

