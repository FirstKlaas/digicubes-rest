from threading import Thread
from digicubes_rest.server import DigiCubeServer


class ServerThread(Thread):

    def run(self):
        server = DigiCubeServer()
        server.run()



t = ServerThread()
print("Hello")
t.start()
print("Moin")

