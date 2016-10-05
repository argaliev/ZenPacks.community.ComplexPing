#!/opt/zenoss/bin/python2.7
#coding: utf-8

import sys
import subprocess
import argparse
import json

def ping(host, timeout='5'):
    return subprocess.call(['ping', '-q', '-c 1', '-w {0}'.format(timeout), host.strip()])

def is_unreachible(host, timeout):
    response = ping(host, timeout)
    return 0 != response

def main():

    parser = argparse.ArgumentParser(description='Process args for complex ping')
    parser.add_argument('-g', '--gateway', required=False, action='store', help='gateway address')
    parser.add_argument('-o', '--os', required=True, action='store', help='operation system address or name')
    parser.add_argument('-i', '--ipmi', required=False, action='store', help='management port address or name')
    parser.add_argument('-w', '--timeout', required=False, default='5', action='store', help='ping timeout')

    args = parser.parse_args()

    status_map = {'os':{'available':True},
                  'device':{'available':True},
                  'gateway':{'available':True},
                  'managed_port':{'available':True}
                  }

    if args.gateway is not None and is_unreachible(args.gateway, args.timeout):
        status_map['gateway']['available'] = False
    else:
        if is_unreachible(args.os, args.timeout):
            if args.ipmi is not None and is_unreachible(args.ipmi, args.timeout):
                status_map['device']['available'] = False
            else:
                status_map['os']['available'] = False
        else:
            if args.ipmi is not None:
                status_map['managed_port']['available'] = not is_unreachible(args.ipmi, args.timeout)

    print json.dumps(status_map)
    return 0

# Main section
if __name__ == "__main__":
    sys.exit(main())