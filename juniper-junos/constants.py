""" Copyright start
Copyright (C) 2008 - 2022 Fortinet Inc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end """

JUNOS_URL = '{0}:{1}/rpc{2}'
HTTP_HEADERS = {'Accept':'application/json'}
GET_CONFIG = '''
<get-config>
    <source>
        <running/>
    </source>
    <filter type="subtree">{0}</filter>
</get-config>
'''

GLOBAL_ADDRESS_SET = '''
<configuration>
    <security>
        <address-book>
            <name>global</name>
            <address-set>
                <name>{0}</name>
            </address-set>
        </address-book>
    </security>
</configuration>
'''

PREFIX_LIST = '''
<configuration>
    <policy-options>
        <prefix-list>
            <name>{NAME}</name>{PREFIX_LIST}
        </prefix-list>
    </policy-options>
</configuration>
'''

CONFIG_COMMIT = '''
<lock-configuration/>
<load-configuration>{0}</load-configuration>
<commit/>
<unlock-configuration/>
'''

CONFIG_GLOBAL_ADDRESS_BOOK ='''
<configuration>
    <security>
        <address-book>
            <name>global</name>
            {ADDRESS_LIST}
            <address-set>
                <name>{ADDRESS_SET_NAME}</name>
                {ADDRESS_NAME_LIST}
            </address-set>
        </address-book>
    </security>
</configuration>
'''

ADDRESS_OBJECT = {
    'ip-prefix': '<ip-prefix>{0}</ip-prefix>',
    'dns-name': '<dns-name>{0}</dns-name>',
    'wildcard-address': '<wildcard-address>{0}</wildcard-address>',
    'address-book-add-entry': '<address><name>{NAME}</name>{ENTRY}</address>',
    'address-set-add-entry': '<address><name>{NAME}</name></address>',
    'address-book-delete-entry': '<address delete="delete"><name>{NAME}</name></address>',
    'address-set-delete-entry': '<address delete="delete"><name>{NAME}</name></address>',
    'prefix-list-add-item': '<prefix-list-item><name>{0}</name></prefix-list-item>',
    'prefix-list-delete-item': '<prefix-list-item delete="delete"><name>{0}</name></prefix-list-item>'
}
