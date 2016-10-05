__doc__="""interfaces.py

Interface that creates the web form for ComplexPingDataSource.

"""

from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t

class IComplexPingDataSourceInfo(IRRDDataSourceInfo):

    ComplexPingTimeout = schema.TextLine(title=_t(u'Ping timeout, in seconds'),)

    cycletime = schema.TextLine(title=_t(u'Cycle Time (seconds)'))