from gevent.pywsgi import WSGIServer
import server
from server import app
from geventwebsocket import WebSocketServer, WebSocketError
from geventwebsocket.handler import WebSocketHandler


server.init_twidder()
http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
http_server.serve_forever()
