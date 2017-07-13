try:
    from http.client import HTTPConnection
except:
    from httplib import HTTPConnection

import socket
from re import search, sub
from contextlib import closing
import xmltodict


class Integer():
    "descriptor for property"

class String():
    "descriptor for property"

def msearch():
    endline = '\r\n'

    return endline.join([
        'M-SEARCH * HTTP/1.1',
        'HOST: 239.255.255.250:1900',
        'MAN: "ssdp:discover"',
        'MX: 2',
        'ST: urn:schemas-upnp-org:device:MediaRenderer:1',
        'USER-AGENT: Linux UDAP/2.0 1',
        ]) + 2 * endline


def resolve_ip():
    request_bytes = msearch().encode()

    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
        sock.settimeout(3)
        for attempt in range(5):
            try:
                sock.sendto(request_bytes, ('239.255.255.250', 1900))
                gotbytes, addressport = sock.recvfrom(512)
                gotstr = gotbytes.decode()
                if search('lge', gotstr):
                    ipaddress, port = addressport
                    return ipaddress
            except:
                pass
    raise Exception('dammit')



def ipaddress_required(func):
    def wrapper(cls, *args, **kwargs):
        if Protocol.ipaddress is None:
            Protocol.ipaddress = resolve_ip()
        return func(cls, *args, **kwargs)
    return wrapper

def auth_required(func):
    def wrapper(cls, *args, **kwargs):
        if Protocol.session_id is None:
            Protocol.session_id = Protocol.start_session()
        return func(cls, *args, **kwargs)
    return wrapper


class Command(object):

    def __init__(self, *args, **kwargs):
        self.command_name = self.__class__.__name__

    def envelope(self, payload):
        return ('<?xml version="1.0" encoding="utf-8"?>\r\n'
                '<envelope>'
                '<api type="command">%s</api>'
                '</envelope>') % payload

    def payload(self, attrs):
        payload = ''
        for k,v in attrs.iteritems():
            payload += '<{tag}>{value}</{tag}>'.format(tag=k, value=v)
        return payload

    @auth_required
    def __call__(self, **kwargs):
        attrs = {'name': self.command_name}
        attrs.update(kwargs)

        data = self.envelope(self.payload(attrs))
        response = Protocol.post_xml('/udap/api/command', data)
        if response.status == 200:
            pass
        elif response.status == 400:
            raise Exception(response.read())
        # TODO: validate

        return self.envelope(self.payload(attrs))

class Query(object):

    def __init__(self, *args, **kwargs):
        self.query_name = None

    @auth_required
    def __call__(self, **kwargs):
        data = Protocol.get_data(self.query_name)
        body = data.read()
        filtered = sub(u'[\x0F]', '', body)
        return xmltodict.parse(filtered)

class Protocol(object):

    headers = {"Content-Type": "application/atom+xml", 'User-Agent': 'UDAP/2.0'}
    ipaddress = None
    session_id = None
    key = None

    def __init__(self, ipaddress=None, key=None):
        Protocol.key = key
        for i in dir(self):
            attr = getattr(self, i)
            if isinstance(attr, Query):
                setattr(attr, 'query_name', i)

    @classmethod
    @ipaddress_required
    def get_connection(cls):
        return HTTPConnection(cls.ipaddress, port=8080)

    @classmethod
    def get(cls, url):
        conn = cls.get_connection()
        conn.request('GET', url, headers=cls.headers)
        return conn.getresponse()

    @classmethod
    def get_data(cls, target, **kwargs):
        url = '/udap/api/data?target=%s' % target
        if kwargs:
            url += '&' + '&'.join("%s=%s" % (key,val) for (key,val) in kwargs.iteritems())
        return cls.get(url)

    @classmethod
    def post_xml(cls, url, xml):
        conn = cls.get_connection()
        conn.request('POST', url, xml, headers=cls.headers)
        return conn.getresponse()

    @classmethod
    def start_session(cls):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <envelope>
                <api type="pairing">
                    <name>hello</name>
                    <value>%s</value>
                    <port>8080</port>
                </api>
            </envelope>
        """ % cls.key
        res = cls.post_xml('/udap/api/pairing', xml)
        if res.status != 200:
            raise Exception('DammitAuth')
