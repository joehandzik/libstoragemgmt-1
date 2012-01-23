#!/usr/bin/env python

# Copyright (C) 2011-2012 Red Hat, Inc.
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Author: tasleson

import os
import unittest

from external.enumeration import Enumeration
import sys
import syslog

# TODO Change this to something more realistic, can be overridden with ENV
# variable in client and specified on the command line for the daemon
UDS_PATH = '/tmp/lsm/ipc'

#Set to True for verbose logging
LOG_VERBOSE = True

def params_to_string(*args):
    return ''.join( [ str(e) for e in args] )

# Unfortunately the process name remains as 'python' so we are using argv[0] in
# the output to allow us to determine which python exe is indeed logging to
# syslog.

def post_msg(level, prg, msg):
    """
    If a message includes new lines we will create multiple syslog
    entries so that the message is readable.  Otherwise it isn't very readable.
    Hopefully we won't be logging much :-)
    """
    for l in msg.split('\n'):
        if len(l):
            syslog.syslog(level, prg + ": " + l)

def Error(*msg):
    post_msg(syslog.LOG_ERR, os.path.basename(sys.argv[0]), params_to_string(*msg))

def Info(*msg):
    if LOG_VERBOSE:
        post_msg(syslog.LOG_INFO, os.path.basename(sys.argv[0]), params_to_string(*msg))

class SocketEOF(Exception):
    """
    Exception class to indicate when we read zero bytes from a socket.
    """
    pass

class LsmError(Exception):
    def __init__(self, code, message, data=None, *args, **kwargs):
        """
        Class represents an error.
        """
        Exception.__init__(self, *args, **kwargs)
        self.args = ( code, message, data )
        self.code = code
        self.msg = message
        self.data = data


def addl_error_data(domain, level, exception, debug = None, debug_data = None):
    """
    Used for gathering additional information about an error.
    """
    return {'domain': domain, 'level': level, 'exception': exception,
            'debug': debug, 'debug_data': debug_data}


def get_class( class_name ):
    """
    Given a class name it returns the class, caller will then
    need to run the constructor to create.
    """
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    if len(module):
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
    else:
        m = __import__('__main__')
        m = getattr(m, class_name)
    return m


ErrorLevel = Enumeration('ErrorLevel',
    [
        ('None', 0),
        ('Warning', 1),
        ('Error', 2)
    ])

#Note: Some of these don't make sense for python, but they do for other
#Languages so we will be keeping them consistent even though we won't be
#using them.
ErrorNumber = Enumeration('ErrorNumber',
    [
        ('OK', 0),
        ('INTERNAL_ERROR', 1),
        ('NO_MEMORY', 2),
        ('NO_SUPPORT', 3),
        ('UNKNOWN_HOST', 4),
        ('NO_CONNECT', 5),
        ('INVALID_CONN', 6),
        ('JOB_STARTED', 7),
        ('INVALID_ARGUMENT', 8),
        ('URI_PARSE', 9),
        ('PLUGIN_PERMISSION', 10),
        ('PLUGIN_DLOPEN', 11),
        ('PLUGIN_DLSYM', 12),
        ('PLUGIN_ERROR', 13),
        ('INVALID_ERR', 14),
        ('PLUGIN_REGISTRATION', 15),
        ('INVALID_POOL', 16),
        ('INVALID_JOB_NUM', 17),
        ('UNSUPPORTED_PROVISIONING', 18),
        ('INVALID_VOLUME', 19),
        ('VOLUME_SAME_SIZE', 20),
        ('INVALID_INIT', 21),
        ('NO_MAPPING', 22),
        ('INSUFFICIENT_SPACE', 23),
        ('IS_MAPPED', 24),
        ('AUTH_FAILED', 45)
    ])

JobStatus = Enumeration('JobStatus',
    [
        ('INPROGRESS', 1),
        ('COMPLETE', 2),
        ('STOPPED', 3),
        ('ERROR', 4)
    ])

class TestCommon(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple(self):

        try:
            raise SocketEOF()
        except SocketEOF as e:
            self.assertTrue( isinstance(e,SocketEOF))

        try:
            raise LsmError(10, 'Message', 'Data')
        except LsmError as e:
            self.assertTrue(e.code == 10 and e.msg == 'Message' and e.data == 'Data')

        ed = addl_error_data('domain', 'level', 'exception', 'debug', 'debug_data')
        self.assertTrue(ed['domain'] == 'domain' and ed['level'] == 'level'
                        and ed['debug'] == 'debug'
                        and ed['exception'] == 'exception'
                        and ed['debug_data'] == 'debug_data')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()