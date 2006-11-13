#!/bin/env python

# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
#
# This generates the documentation when the server is started.
#

from nevow import flat,tags as T,loaders,rend,inevow

class functionDocGenerator(rend.Page):
    
    docFactory = loaders.xmlfile('numblerdoctemplate.xml',templateDir='templates')
    reqargpat =  inevow.IQ(docFactory).patternGenerator("reqarg")
    optargpat =  inevow.IQ(docFactory).patternGenerator("optarg")
    commentpat = inevow.IQ(docFactory).patternGenerator("commentpat")
    examplepat = inevow.IQ(docFactory).patternGenerator("examplepat")    

    def __init__(self,funclist):
        self.funclist = funclist

    def data_funclist(self,ctx,data):
        return (x() for x in self.funclist)

    def render_summary(self,ctx,data):
        ds = data.docsummary()
        return ctx.tag[ds]

    def render_arglist(self,ctx,data):
        argsdict = data.getFuncargs()
        args = argsdict['args']
        varArgs = argsdict.get('varargs')
        if varArgs is None:
            varArgs = False
            def argGen():
                for arg in args:
                    if arg[1]: # required
                        yield self.reqargpat(data=arg)
                    elif not varArgs:
                        yield self.optargpat(data=arg)

            return ctx.tag[argGen()]
        else:
            dataval = (','.join([args[0][0],args[1][0],'...']),True,args[0][2])
            return ctx.tag[self.reqargpat(data=dataval)]

    def render_reqarg(self,ctx,data):
        ctx.fillSlots('funcarg',data[0])
        ctx.fillSlots('argdesc',data[2])
        return ctx.tag

    def render_optarg(self,ctx,data):
        ctx.fillSlots('funcarg',data[0])
        ctx.fillSlots('argdesc',data[2])
        return ctx.tag

    def render_comments(self,ctx,data):
        details = data.getFuncdetails()
        if details:
            return ctx.tag[self.commentpat(data=details)]
        else:
            return ''

    def render_examples(self,ctx,data):
        example = data.getFuncExamples()
        if example:
            return ctx.tag[self.examplepat(data=example)]
        return ''

    def render_commentdetails(self,ctx,data):
        ctx.fillSlots('commentinfo',data)
        return ctx.tag
        
    def render_exampledetails(self,ctx,data):
        ctx.fillSlots('example',data)
        return ctx.tag

    def render_funcname(self,ctx,data):
        name = str(data.__class__.__name__)
        #return T.a(href="#%s" % name)[T.h3[name]]
        return T.h3[name]

    def render_syntax(self,ctx,data):
        args = data.getFuncargs()
        arglist = args['args']        
        varArgs = args.get('varargs')
        if varArgs is None:
            varArgs = False
            yield T.span(_class="synreq")[args['name'] + '(']
            for argI in range(0,len(arglist)):
                argval = arglist[argI]
                strdat = argval[0]
                if argI +1 != len(arglist):
                    strdat += ','
                if argval[1]:
                    cssClass = 'synreq'
                else:
                    cssClass = 'synopt'
                yield T.span(_class=cssClass)[strdat]

            yield T.span(_class="synreq")[')']
        else:
            yield T.span(_class="synreq")[''.join([args['name'],'(',arglist[0][0],',',arglist[1][0],',','...)'])]




class DocGenerator(object):

    def __init__(self,funclist):
        self.funclist = funclist


    

    def generateFunc(self,func):

        gen = NumblerFuncDoc(func)
        return flat.flatten(gen)

