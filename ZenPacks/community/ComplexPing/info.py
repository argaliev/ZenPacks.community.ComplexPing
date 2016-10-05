__doc__="""info.py

Adapter between IComplexPingDataSourceInfo and ComplexPingDataSource.

"""
from zope.component import adapts
from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo

from ZenPacks.community.ComplexPing import interfaces
from ZenPacks.community.ComplexPing.datasources import ComplexPingDataSource

class ComplexPingDataSourceInfo(RRDDataSourceInfo):

    implements(interfaces.IComplexPingDataSourceInfo)
    adapts(ComplexPingDataSource)

    ComplexPingTimeout = ProxyProperty('ComplexPingTimeout')

    cycletime = ProxyProperty('cycletime')

    testable = False