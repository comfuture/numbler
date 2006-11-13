# Copyright (C) 2006 Numbler LLC
# See LICENSE for details.
        
class ImportParseWarning(object):
    """ base class for warnings
    text = warning type
    severity = numeric value (defaults to 1)
    key = to avoid duplicate warnings. the key must be unique!
    """
    severity = 1

class StyleWarning(ImportParseWarning):
    text = "Numbler was unable to import some of the formatting from your spreadsheet."
    key = 'w1'

class FontWarning(ImportParseWarning):
    text = "Some of the font formatting could not be imported."
    key = 'f1'

class AlignWarning(ImportParseWarning):
    text = 'Some of the text alignment features in your sheet are not supported.'
    key = 'a1'

class InteriorWarning(ImportParseWarning):
    text = 'only solid color backgrounds are supported.'
    key = 'i1'

class DataImportWarning(ImportParseWarning):
    text = 'Numbler encountered some cell data that it does not understand.  This can happen if the cell contains HTML formatting.'
    key = 'baddataWarning'

