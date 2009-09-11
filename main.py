import cgi
import wsgiref.handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp

def require_login(func):
    def redirect_if_not_logged_in(self, *args, **keywords):
      if not users.get_current_user():
        self.redirect(users.create_login_url(self.request.uri))
      else:
        func(self, *args, **keywords)
    return redirect_if_not_logged_in

class Unit(db.Model):
  name = db.StringProperty( required = True )
  unit = db.StringProperty( required = True )

class Entry(db.Model):
  user = db.UserProperty(required = True)
  unit = db.ReferenceProperty(Unit, required = True )
  value = db.FloatProperty()
  date = db.DateTimeProperty( auto_now_add = True )

class MainPage(webapp.RequestHandler):
  @require_login
  def get(self):
    self.response.out.write(template.render("index.html", {'entries': Entry.all().order('-date'), 'units': Unit.all() }))

class EntryPage(webapp.RequestHandler):
  @require_login
  def post(self):
    Entry(
      user = users.get_current_user(),
      unit = Unit.get(self.request.get('unit')),
      value = float(self.request.get('value')),
    ).put()
    self.redirect('/')

class UnitPage(webapp.RequestHandler):
  @require_login
  def post(self):
    Unit(
      name = self.request.get('name'),
      unit = self.request.get('unit')
    ).put()
    self.redirect('/')

def main():
  application = webapp.WSGIApplication( [
    ('/', MainPage),
    ('/unit', UnitPage),
    ('/entry', EntryPage)
  ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)
    
if __name__ == "__main__":
  main()
