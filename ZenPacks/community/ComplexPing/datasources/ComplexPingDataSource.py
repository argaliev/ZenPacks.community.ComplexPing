from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSource, PythonDataSourcePlugin

import datetime
from twisted.internet import defer, utils
from Products.ZenEvents.ZenEventClasses import Warning, Error, Critical, Clear
import os
import json

import logging
log = logging.getLogger('zen.ComplexPing')

class ComplexPingDataSource(PythonDataSource):

    ZENPACKID = 'ZenPacks.community.ComplexPing'

    # Friendly name for your data source type in the drop-down selection.
    sourcetypes = ('ComplexPing',)
    sourcetype = sourcetypes[0]

    component = '${here/id}'
    eventClass = '/Status/Ping'
    cycletime = '${dev/zComplexPingInterval}'

    # Custom fields in the datasource
    ComplexPingTimeout = '${dev/zComplexPingTimeout}'

    OS_severity = Critical
    MPORT_severity = Error
    NET_severity = Warning
    DEVICE_severity = Critical

    _properties = PythonDataSource._properties + (
        {'id': 'ComplexPingTimeout', 'type': 'int', 'mode': 'w'},

    )

    # Collection plugin for this type.
    plugin_classname = ZENPACKID + '.datasources.ComplexPingDataSource.ComplexPingPlugin'

class ComplexPingPlugin(PythonDataSourcePlugin):

    proxy_attributes = (
        'zManageInterfaceEnable',
        'zManageInterfaceIP',
        'zGatewayEnable',
        'manageIp',
        )

    @classmethod
    def config_key(cls, datasource, context):
        return (
            context.device().id,
            datasource.getCycleTime(context),
            datasource.rrdTemplate().id,
            datasource.id,
            datasource.plugin_classname,
            )

    @classmethod
    def params(cls, datasource, context):
        params = {}

        def get_gateway(device):
            for comp in device.getDeviceComponents():
                if comp.__class__.__name__ == 'IpRouteEntry':
                    if comp.title.startswith('0.0.0.0'):
                        return comp.nexthop.getRelatedId()
            return None

        params['gateway'] = get_gateway(context)
        params['ComplexPingTimeout'] = datasource.ComplexPingTimeout
        params['OS_severity'] = datasource.OS_severity
        params['MPORT_severity'] = datasource.MPORT_severity
        params['NET_severity'] = datasource.NET_severity
        params['DEVICE_severity'] = datasource.DEVICE_severity

        log.debug(' params is %s \n' % (params))
        return params

    def collect(self, config):
        ds0 = config.datasources[0]
        data = self.new_data()

        status_map = {'os':{'severity':ds0.params['OS_severity'],
                            'eventClass':'/Status/Ping/OS',
                            'available':True},
                      'device':{'severity':ds0.params['DEVICE_severity'],
                                'eventClass':'/Status/Ping/Hardware',
                                'available':True},
                      'gateway':{'severity':ds0.params['NET_severity'],
                                 'eventClass':'/Status/Ping/Gateway',
                                 'available':True},
                      'managed_port':{'severity':ds0.params['MPORT_severity'],
                                      'eventClass':'/Status/Ping/ManagePort',
                                      'available':True}
                      }

        args = ['-o {0}'.format(ds0.manageIp)]
        if ds0.zGatewayEnable and ds0.params['gateway'] is not None:
            args.append('-g {0}'.format(ds0.params['gateway']))

        if ds0.zManageInterfaceEnable and not(ds0.zManageInterfaceIP):
            data['events'].append({
                        'device': config.id,
                        'summary': "managed_port ip is not set, but enabled in zProperties",
                        'severity': Warning,
                        'eventClass' :  status_map['managed_port']['eventClass'],
                        'eventKey': 'complexPingProperties',
                        })
        else:
            if ds0.zManageInterfaceEnable and ds0.zManageInterfaceIP:
                args.append('-i {0}'.format(ds0.zManageInterfaceIP))
            data['events'].append({
                            'device': config.id,
                            'summary': "managed_port ip is OK",
                            'severity': Clear,
                            'eventClass' :  status_map['managed_port']['eventClass'],
                            'eventKey': 'complexPingProperties',
                            })

        ping_path = os.path.dirname(os.path.realpath(__file__)).rsplit('/',1)[0] + '/bin/complex_ping.py'
        log.debug( 'executable script: %s %s ' % (ping_path, args))

        def get_ping_events(results, data):
            out, err, code = results
            log.debug( 'script return code %s ' % (code))
            log.debug( 'script stderr %s ' % (err))
            log.debug( 'script stdout %s ' % (out))

            stdout_startswith = out.find('{')
            stdout_endswith = out.find("}}")+2
            result = json.loads(out[stdout_startswith:stdout_endswith])

            for k,v in status_map.iteritems():
                status_map[k].update(result[k])

            log.debug( 'result status_map %s ' % str(status_map))

            for k,v in status_map.iteritems():
                if v['available'] is True:
                    data['events'].append({
                        'device': config.id,
                        'summary': "{0} is available".format(k),
                        'severity': Clear,
                        'eventClass' : v['eventClass'],
                        'eventKey': 'complexPing',
                    })
                else:
                    data['events'].append({
                        'device': config.id,
                        'summary': "{0} is unavailable".format(k),
                        'severity': v['severity'],
                        'eventClass' : v['eventClass'],
                        'eventKey': 'complexPing',
                    })

            log.debug( 'data %s ' % (data))
            return data

        d = utils.getProcessOutputAndValue(ping_path, args=args)
        d.addCallback(get_ping_events,data)

        return d