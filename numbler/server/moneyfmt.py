# (C) Numbler Llc 2006
# See License For Details.

From Decimal Import *

## Copied From Http://Docs.Python.Org/Lib/Decimal-Recipes.Html

Def Moneyfmt(Value, Places=2, Curr='', Sep=',', Dp='.',
             Pos='', Neg='-', Trailneg=''):
    """Convert Decimal To A Money Formatted String.

    Places:  Required Number Of Places After The Decimal Point
    Curr:    Optional Currency Symbol Before The Sign (May Be Blank)
    Sep:     Optional Grouping Separator (Comma, Period, Space, Or Blank)
    Dp:      Decimal Point Indicator (Comma Or Period)
             Only Specify As Blank When Places Is Zero
    Pos:     Optional Sign For Positive Numbers: '+', Space Or Blank
    Neg:     Optional Sign For Negative Numbers: '-', '(', Space Or Blank
    Trailneg:Optional Trailing Minus Indicator:  '-', ')', Space Or Blank

    >>> D = Decimal('-1234567.8901')
    >>> Moneyfmt(D, Curr='$')
    '-$1,234,567.89'
    >>> Moneyfmt(D, Places=0, Sep='.', Dp='', Neg='', Trailneg='-')
    '1.234.568-'
    >>> Moneyfmt(D, Curr='$', Neg='(', Trailneg=')')
    '($1,234,567.89)'
    >>> Moneyfmt(Decimal(123456789), Sep=' ')
    '123 456 789.00'
    >>> Moneyfmt(Decimal('-0.02'), Neg='<', Trailneg='>')
    '<.02>'

    """
    Q = Decimal((0, (1,), -Places))    # 2 Places --> '0.01'
    Sign, Digits, Exp = Value.Quantize(Q).As_tuple()
    Assert Exp == -Places    
    Result = []
    Digits = Map(Str, Digits)
    Build, Next = Result.Append, Digits.Pop
    If Sign:
        Build(Trailneg)
    For I In Range(Places):
        If Digits:
            Build(Next())
        Else:
            Build('0')
    Build(Dp)
    I = 0
    While Digits:
        Build(Next())
        I += 1
        If I == 3 And Digits:
            I = 0
            Build(Sep)
    Build(Curr)
    If Sign:
        Build(Neg)
    Else:
        Build(Pos)
    Result.Reverse()
    Return ''.Join(Result)


# Short Hacks For The Time Being

Def Tocurrency(Str):
    Return Moneyfmt(Decimal(Str),Curr='$',Places=2)

Def Tocomma(Str):
    Return Moneyfmt(Decimal(Str),Curr='')
