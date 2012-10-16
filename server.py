import os
import re
import conf
import divaserve
import json

import tornado.httpserver
import tornado.ioloop
import tornado.web

# this initializes the memcached connection
img_server = divaserve.DivaServe()


def tryint(s):
    try:
        return int(s)
    except:
        return s


def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        ms_info = {}
        ms = os.listdir(conf.IMG_DIR)
        ms.sort(key=alphanum_key)
        ms_info = ((d, len(os.listdir(os.path.join(conf.IMG_DIR, d)))) for d in ms if not d.startswith('.'))
        self.render("templates/index.html", info=ms_info)


class ManuscriptHandler(tornado.web.RequestHandler):
    def get(self, msdir):
        pth = os.path.join(conf.IMG_DIR, msdir)
        self.render("templates/diva.html", image_path=pth, ms_name=msdir)


class DivaHandler(tornado.web.RequestHandler):
    def get(self):
        msdir = self.get_argument('d')
        self.set_header("Content-Type", "application/json")
        js = img_server.getc(msdir)
        self.write(json.dumps(js))


class CanvasHandler(tornado.web.RequestHandler):
    def get(self):
        pass

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), "static"),
    'debug': True,
    'cookie_secret': "iEbkYMzCV8~}a-nT8Vi-2zg@]p*k}euh1hix"
}

application = tornado.web.Application([
    (r"/?", MainHandler),
    (r"/divaserve/?", DivaHandler),
    (r"/canvas/?", CanvasHandler),
    (r"/witness/([a-zA-Z0-9_-]+)", ManuscriptHandler),
], **settings)


def main(port):
    server = tornado.httpserver.HTTPServer(application)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8888
    main(port)
