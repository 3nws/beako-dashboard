import socket
import sys
import json
import time
import kivy

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from threading import Thread

kivy.require('2.1.0')

from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '1024')


host = "127.0.0.1"
port = 15555


class BeakoStats(BoxLayout):

    servers = StringProperty("Servers: 0")
    members = StringProperty("Members: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.socket_th = Thread(target=self.listen)
        self.socket_th.start()

    def listen(self):
        print("# Creating socket")
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print("Failed to create socket")
            sys.exit()
        print("# Getting remote IP address")
        try:
            self.remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting")
            sys.exit()

        print("# Connecting to server, " + host + " (" + self.remote_ip + ")")
        self.s.connect((self.remote_ip, port))
        while True:
            reply = self.s.recv(4096)
            self.servers = "Servers: " + str(json.loads(reply.decode()).get("servers"))
            self.members = "Members: " + str(json.loads(reply.decode()).get("members"))
            stats = json.loads(reply.decode()).get("stats")
            self.stats.data = [    # type: ignore
                {"name.text": k, "value": str(v)} for k, v in stats.items()
            ]
            namespaces = json.loads(reply.decode()).get("namespaces")
            self.namespaces.data = [  # type: ignore
                {"name.text": str(namespace[0]), "value": str(namespace[-1])}
                for namespace in namespaces
            ]
            time.sleep(1)


class BeakoStatsApp(App):
    def build(self):
        self.stats = BeakoStats()
        return self.stats


if __name__ == "__main__":
    app = BeakoStatsApp()
    app.run()
    app.stats.socket_th.join()
