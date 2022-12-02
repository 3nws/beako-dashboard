import socket
import sys
import json
import kivy

from kivy.core.window import Window
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from threading import Thread

from config import HOST

kivy.require("2.1.0")

from kivy.config import Config

Config.set("graphics", "width", "1024")
Config.set("graphics", "height", "1024")


host = HOST
port = 5555


class BeakoStats(BoxLayout):

    servers = StringProperty("Servers: 0")
    members = StringProperty("Members: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.socket_th = Thread(target=self.listen)
        self.socket_th.start()

    def listen(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print("Failed to create socket")
            sys.exit()
        try:
            self.remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting")
            sys.exit()

        while True:
            try:
                reply = self.s.recv(4096)
                self.servers = "Servers: " + str(
                    json.loads(reply.decode()).get("servers")
                )
                self.members = "Members: " + str(
                    json.loads(reply.decode()).get("members")
                )
                stats = json.loads(reply.decode()).get("stats")
                self.stats.data = [  # type: ignore
                    {"name.text": k, "value": str(v)} for k, v in stats.items()
                ]
                namespaces = json.loads(reply.decode()).get("namespaces")
                self.namespaces.data = [  # type: ignore
                    {"name.text": str(namespace[0]), "value": str(namespace[-1])}
                    for namespace in namespaces
                ]
            except OSError:
                try:
                    self.s.connect((self.remote_ip, port))
                except ConnectionRefusedError:
                    pass


class BeakoStatsApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        Window.size = (1024, 768)
        self.stats = BeakoStats()
        return self.stats

    def on_request_close(self, *args):
        self.stats.s.close()
        self.stats.socket_th.join()
        return False


if __name__ == "__main__":
    app = BeakoStatsApp()
    app.run()
