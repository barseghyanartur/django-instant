# -*- coding: utf-8 -*-

from __future__ import print_function
import json
from cent import Client, CentException
from instant.conf import SITE_NAME, CENTRIFUGO_HOST, CENTRIFUGO_PORT, SECRET_KEY, SITE_SLUG, PUBLIC_CHANNEL, BROADCAST_WITH
if BROADCAST_WITH == "go":
    import os
    import instant


def _get_channel(channel, target):
    if channel is None:
        if target is not None:
            if target == "superuser":
                channel = "$" + SITE_SLUG + '_admin'
            elif target == "staff":
                channel = "$" + SITE_SLUG + '_staff'
            elif target == "users":
                channel = "$" + SITE_SLUG + '_users'
            else:
                return False, None
        else:
            channel = PUBLIC_CHANNEL
    return channel


def publish_py(message, event_class="default", data={}, channel=None, site=SITE_NAME, target=None):
    cent_url = CENTRIFUGO_HOST + ":" + str(CENTRIFUGO_PORT)
    client = Client(cent_url, SECRET_KEY, timeout=1)
    channel = _get_channel(channel, target)
    payload = {"message": message, "channel": channel,
               'event_class': event_class, "data": data, "site": site}
    err = None
    try:
        client.publish(channel, payload)
    except CentException as e:
        err = str(e)
    if event_class.lower() == "debug":
        print("[DEBUG] ", str(json.dumps(payload)))
    return err


def publish_go(message, event_class="default", data={}, channel=None, site=SITE_NAME, target=None):
    channel = _get_channel(channel, target)
    channel = channel.replace("$", "-_-")
    conn = '-host="' + CENTRIFUGO_HOST + '" -port="' + \
        str(CENTRIFUGO_PORT) + '" -key="' + SECRET_KEY + '"'
    params = conn + ' -channel="' + channel + '" -event_class="' + event_class + \
        '" -message="' + message + '" -data=\'' + json.dumps(data) + "'"
    pth = os.path.dirname(instant.__file__)
    gocmd = pth + '/go/publish ' + params
    os.system(gocmd)
    if event_class.lower() == "debug":
        print("[DEBUG] ", message, str(json.dumps(data)))
    return


if BROADCAST_WITH == "go":
    publish = publish_go
else:
    publish = publish_py
