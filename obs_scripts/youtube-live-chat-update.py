"""
youtube-live-chat-update.py

OBS script that updates the YouTube livechat URL on a browser source on stream 
start to the livechat associated with the (first) current livestream on a 
given channel.

To use this you will need a YouTube API key, see 

  https://developers.google.com/youtube/v3/getting-started 

and 

  https://developers.google.com/youtube/registering_an_application

for more information on how to go about that.

Additionally you will require the channel ID of the channel for which you want
to query the current live stream. You can retrieve that by inspecting the
web site source of the channel in question and looking for `externalId`.

---

Copyright (c) 2021 Gina Häußge

Permission is hereby granted, free of charge, to any person obtaining a 
copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.
"""

import obspython as obs
import urllib.request
import urllib.error
import json

__author__ = "Gina Häußge"
__license__ = "MIT"

channelid   = ""
apikey      = ""
source_name = ""
delay       = 5

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channelid}&eventType=live&type=video&key={apikey}"
YOUTUBE_CHAT_URL = "https://www.youtube.com/live_chat?v={vid}"
NO_STREAM = "data:text/html;base64,PGh0bWw+Cjxib2R5IHN0eWxlPSJkaXNwbGF5OiBmbGV4OyBoZWlnaHQ6IDEwMCU7IHBhZGRpbmc6IDA7IG1hcmdpbjogMDsgYWxpZ24taXRlbXM6IGNlbnRlcjsganVzdGlmeS1jb250ZW50OiBjZW50ZXI7IGZvbnQtZmFtaWx5OiBzYW5zLXNlcmlmIj4KICA8ZGl2IGNsYXNzPSJub3N0cmVhbSI+Tm8gU3RyZWFtLjwvZGl2Pgo8L2JvZHk+CjwvaHRtbD4="

# ------------------------------------------------------------

def update_url():
    global channelid
    global apikey
    global source_name

    obs.timer_remove(update_url)

    source = obs.obs_get_source_by_name(source_name)
    if apikey and source is not None:
        url = YOUTUBE_QUERY_URL.format(channelid=channelid, apikey=apikey)
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                body = data.decode('utf-8')
                data = json.loads(body)

                items = data.get("items")
                if items:
                    vid = items[0]["id"]["videoId"]
                    print("Found live stream, vid: {}".format(vid))

                    livechat = YOUTUBE_CHAT_URL.format(vid=vid)
                    print("Setting livechat URL to {}".format(livechat))
                else:
                    livechat = NO_STREAM
                    print("No active stream, setting placeholder")

                settings = obs.obs_data_create()
                obs.obs_data_set_string(settings, "url", livechat)
                obs.obs_source_update(source, settings)
                obs.obs_data_release(settings)

        except urllib.error.URLError as err:
            obs.script_log(obs.LOG_WARNING, "Error retrieving livechat URL for channel '" + channelid + "': " + err.reason)
            obs.remove_current_callback()

        obs.obs_source_release(source)

def refresh_pressed(props, prop):
    print("Refresh pressed")
    update_url()
    service = obs.obs_frontend_get_streaming_service()
    if (service is None):
        return
    settings = obs.obs_service_get_settings(service)
    obs.obs_data_set_string(settings, "key", "hahaha")
    obs.obs_service_update(service, settings)
    obs.obs_data_release(settings)
    obs.obs_frontend_save_streaming_service()


def on_frontend_event(event):
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        global delay

        print("Streaming started")
        obs.timer_remove(update_url)
        obs.timer_add(update_url, delay * 1000)
    elif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        print("Streaming stopped")
        obs.timer_remove(update_url)

# ------------------------------------------------------------

def script_description():
    return "Updates the YouTube livechat URL on a browser source on stream start.\n\nby @foosel"

def script_update(settings):
    global channelid
    global apikey
    global source_name
    global delay

    channelid    = obs.obs_data_get_string(settings, "channelid")
    apikey       = obs.obs_data_get_string(settings, "apikey")
    source_name  = obs.obs_data_get_string(settings, "source")
    delay        = obs.obs_data_get_int(settings, "delay")

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "delay", 5)

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "channelid", "YouTube Channel ID", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "apikey", "YouTube API key", obs.OBS_TEXT_DEFAULT)

    p = obs.obs_properties_add_list(props, "source", "Browser Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "browser_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_int(props, "delay", "Execution delay (seconds)", 5, 3600, 1)

    obs.obs_properties_add_button(props, "button", "Refresh", refresh_pressed)
    return props

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_frontend_event)