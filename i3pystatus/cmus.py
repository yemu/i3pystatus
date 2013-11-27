import os

from i3pystatus import IntervalModule, formatp
from i3pystatus.core.util import TimeWrapper
import subprocess

class Cmus(IntervalModule):

    """
    gets the status and current song info using cmus-remote
    """

    settings = (
        "format",
    )
    color = "#909090"
    format = "{status_text}"
    icon = 'aaa'
    status_text = ''
    interval = 1
    status = {
        "paused": "▷",
        "playing": "▶",
        "stop": "◾",
    }
    def _cmus_command(self,command):
        p = subprocess.Popen('cmus-remote --{command}'.format(command=command), shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        return p.communicate()

    def _query_cmus(self):
        status_dict={}
        status, error = self._cmus_command('query')
        #print(status.decode('utf-8'))
        status=status.decode('utf-8').split('\n')
        #print (status)
        if status == b'cmus-remote: cmus is not running\n':
                status_text='not running'
        else:
            for item in status:
                split_item = item.split(' ')
                #print(split_item)
                if split_item[0] in ['tag', 'set']:
                    key = '{opt}_{tag_name}'.format(tag_name=split_item[1], opt=split_item[0])
                    val = ' '.join([x for x in split_item[2:]])
                    status_dict[key] = val
                elif split_item[0] in ['duration', 'position', 'status']:
                    status_dict[split_item[0]] = split_item[1]
            print(status_dict)
        return status_dict

    def run(self):
        status = self._query_cmus()

        fdict = {
            'status': self.status[status["status"]],
            'title': status['tag_title'],
            'album': status['tag_album'],
            'artist': status['tag_artist'],
            'tracknumber': status['tag_tracknumber'],
            'song_length': TimeWrapper(status['duration']),
            'song_elapsed': TimeWrapper(status['position']),
            'bitrate': int(status.get("bitrate", 0)),
        }
        print(fdict)
        self.output = {
            "full_text": formatp(self.format,**fdict),
        }
        print (self.output)

    def on_leftclick(self):
        status =self._get_cmus_status()
        if status == 'playing':
            self._cmus_command('pause')
        if status == 'paused':
            self._cmus_command('play')
        if status == 'stopped':
            self._cmus_command('play')
a =Cmus()
a.run()
