import os
import tornado.ioloop
import tornado.web
import tornado.template
import tornado.auth
import datetime
import pdb

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("template/main.html", name="Person")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("template/login.html")

class GoogleLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        else:
            self.authenticate_redirect('/google_login')

    def _on_auth(self, user):
        if not user:
            # self.redirect('/') with error
            raise tornado.web.HTTPError(500, "Google auth failed")

        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=90)
        self.set_secure_cookie("user", user['email'], expires=expires)
        self.redirect('/')

if __name__ == "__main__":

    settings = {'debug': True,
                'xsrf_cookies': True,
                'login_url': '/login',
                'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
                'static_path': os.path.join(os.path.dirname(__file__), "static")}

    handlers = [
                (r'/', MainHandler),
                (r'/login', LoginHandler),
                (r'/google_login', GoogleLoginHandler)
    ]

    application = tornado.web.Application(handlers, **settings)

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()