======================================
ZenPacks.community.ComplexPing
======================================


Description
===========

This ZenPack provides datasource ComplexPingDataSource, which check device status in few steps:

    1. check gateway, if not available, generate an event, otherwise - continue checks
    2. сheck management interface available(HP iLO, Dell DRAC ..)
    3. check operation system ip available(manageIp in Zenoss)

Zenpack should be used with option `zPingMonitoringIgnore` set to `true`, because once a standard zenping has failed,
all data collection will all be suspended(zenpack will be blocked) until ping access is restore.

Issues:
   - When zenpack generate an event of device unavailable, device status will not changed to DOWN,
   so other data collection continue keep trying to collect data

Requirements & Dependencies
===========================

    * Zenoss Versions Supported: > 4.0
    * External Dependencies:
    * ZenPack Dependencies:
    * Installation Notes: zenhub and zopectl restart after installing this ZenPack.
    * Configuration:

Installation
============
Normal Installation (packaged egg)
----------------------------------
Copy the downloaded .egg to your Zenoss server and run the following commands as the zenoss
user::

   * zenpack --install <package.egg>
   * zenhub restart
   * zopectl restart

Developer Installation (link mode)
----------------------------------
If you wish to further develop and possibly contribute back to this
ZenPack you should clone the git repository, then install the ZenPack in
developer mode::

   * zenpack --link --install <package>
   * zenhub restart
   * zopectl restart

Configuration
=============

Tested with Zenoss 4.2.5

zProperties
-----------
- **zGatewayEnable** - whether it is necessary to check status of gateway
- **zManageInterfaceEnable** - whether it is necessary to check status of management interface
- **zManageInterfaceIP** - ip address of management interface
- **zComplexPingInterval** - time interval to perform monitor
- **zComplexPingTimeout** - ping timeout, in seconds

Monitoring Templates
-----------
- ** /Devices/Server/rrdTemplates/ComplexPing**

Event Classes
-----------
- **/Status/Ping/OS**
- **/Status/Ping/ManagePort**
- **/Status/Ping/Hardware**
- **/Status/Ping/Gateway**

Screenshots
===========
* |ComplexPingEvent|
