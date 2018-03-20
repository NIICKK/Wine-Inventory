# [START imports]
import os
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)+"/templates"),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_TYPE = 'red'

sCountry = ""
sRegion = ""
sName = ""
sVariety = ""

def type_key(type_name=DEFAULT_TYPE):
    return ndb.Key('Type', type_name)

def cart_key(cart_email):
    return ndb.Key('Cart', cart_email)

class WINE(ndb.Model):
    country = ndb.StringProperty()
    region= ndb.StringProperty()
    price = ndb.IntegerProperty()
    name = ndb.StringProperty()
    variety = ndb.StringProperty()
    year = ndb.IntegerProperty()

class TotalCost(ndb.Model):
    cost = ndb.IntegerProperty()

class Purchased(ndb.Model):
    wine_list = ndb.StructuredProperty(WINE, repeated=True)
    date_time = ndb.DateTimeProperty(auto_now_add=True)
    total_cost = ndb.IntegerProperty()


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START enter]
class Enter(webapp2.RequestHandler):

    def get(self):
        type_name = self.request.get('type_name', DEFAULT_TYPE)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'type_name': urllib.quote_plus(type_name),
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('enter.html')
        self.response.write(template.render(template_values))

    def post(self):
        type_name = self.request.get('type_name',
                                          DEFAULT_TYPE)
        wine = WINE(parent=type_key(type_name))

        wine.country = self.request.get('country')
        wine.region = self.request.get('region')
        wine.name = self.request.get('name')
        wine.variety = self.request.get('variety')

        wine.price = int(self.request.get('price'))
        wine.year = int(self.request.get('year'))

        wine.put()

        self.redirect('/enter?type_name=' + type_name)
# [END enter]

# [START browse]
class Browse(webapp2.RequestHandler):

    def get(self):
        type_name = self.request.get('type_name',
                                          DEFAULT_TYPE)
        wines_query = WINE.query(
            ancestor=type_key(type_name)).order(WINE.country)
        wines = wines_query.fetch()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'wines': wines,
            'type_name': urllib.quote_plus(type_name)
        }

        template = JINJA_ENVIRONMENT.get_template('browse.html')
        self.response.write(template.render(template_values))

    def post(self):

        type_name = self.request.get('type_name',
                                          DEFAULT_TYPE)
        if self.request.get('wine_to_cart_country'):
            user = users.get_current_user()
            if user:
                wine_add = WINE(parent=cart_key(user.email()))

                wine_add.country = self.request.get('wine_to_cart_country')
                wine_add.region = self.request.get('wine_to_cart_region')
                wine_add.name = self.request.get('wine_to_cart_name')
                wine_add.variety = self.request.get('wine_to_cart_variety')
                wine_add.price = int(self.request.get('wine_to_cart_price'))
                wine_add.year = int(self.request.get('wine_to_cart_year'))

                cost_key = ndb.Key('TotalCost', user.email())
                if cost_key.get():
                    temp_cost = cost_key.get()
                    temp_cost.cost = temp_cost.cost + wine_add.price
                    temp_cost.put()
                else:
                    cost_entity = TotalCost(cost=wine_add.price)
                    cost_entity.key = cost_key
                    cost_entity.put()

                wine_add.put()
            else:
                self.redirect(users.create_login_url('/browse?type_name=' + type_name))
                return
        self.redirect('/browse?type_name=' + type_name)
# [END browse]

# [START search]
class Search(webapp2.RequestHandler):

    def get(self):
        type_name = self.request.get('type_name', DEFAULT_TYPE)

        global sCountry
        global sRegion
        global sName
        global sVariety

        country = sCountry
        region = sRegion
        name = sName
        variety = sVariety

        sCountry = ''
        sRegion = ''
        sName = ''
        sVariety = ''

        wines_query = WINE.query(
            ancestor=type_key(type_name)).order(-WINE.region)
        wines = []
        message = ''

        if country:
            for wine in wines_query.fetch():
                if country.lower() in wine.country.lower() and region.lower() in wine.region.lower() and name.lower() in wine.name.lower() and variety.lower() in wine.variety.lower():
                    wines.append(wine)


        elif region:
        	for wine in wines_query.fetch():
        		if region.lower() in wine.region.lower() and name.lower() in wine.name.lower() and variety.lower() in wine.variety.lower():
        			wines.append(wine)

        elif name:
        	for wine in wines_query.fetch():
        		if name.lower() in wine.name.lower() and variety.lower() in wine.variety.lower():
        			wines.append(wine)

        elif variety:
        	for wine in wines_query.fetch():
        		if variety.lower() in wine.variety.lower():
        			wines.append(wine)
        message = 'At least one field must be entered'

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
        	'message': message,
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'country': country,
            'region': region,
            'name': name,
            'variety': variety,
            'wines': wines,
            'type_name': urllib.quote_plus(type_name)
        }
        message = ''

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

    def post(self):
        type_name = self.request.get('type_name',
                                          DEFAULT_TYPE)
        country = self.request.get('country')
        region = self.request.get('region')
        name = self.request.get('name')
        variety = self.request.get('variety')

        global sCountry
        global sRegion 
        global sName
        global sVariety

        sCountry = country
        sRegion = region
        sName = name
        sVariety = variety

        if self.request.get('wine_to_cart_country') or self.request.get('wine_to_cart_region'):
            user = users.get_current_user()
            if user:
                wine_add = WINE(parent=cart_key(user.email()))

                wine_add.country = self.request.get('wine_to_cart_country')
                wine_add.region = self.request.get('wine_to_cart_region')
                wine_add.name = self.request.get('wine_to_cart_name')
                wine_add.variety = self.request.get("wine_to_cart_variety")
                wine_add.price = int(self.request.get('wine_to_cart_price'))
                wine_add.year = int(self.request.get('wine_to_cart_year'))

                cost_key = ndb.Key('TotalCost', user.email())
                if cost_key.get():
                    temp_cost = cost_key.get()
                    temp_cost.cost = temp_cost.cost + wine_add.price
                    temp_cost.put()
                else:
                    cost_entity = TotalCost(cost=wine_add.price)
                    cost_entity.key = cost_key
                    cost_entity.put()

                wine_add.put()
            else:
                self.redirect(users.create_login_url('/search?type_name=' + type_name + '&country=' + country + '&region' + region + '&name' + name + '$variety' + variety))
                return

        print(users.get_current_user())

        self.redirect('/search?type_name=' + type_name + '&country=' + country + '&region' + region + '&name' + name + '$variety' + variety)
# [END search]


# [START shopping cart]
class ShoppingCart(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if users.get_current_user():
            cart_email = users.get_current_user().email()
        else:
            self.redirect(users.create_login_url('/shoppingcart'))
            return
        cart_query = WINE.query(ancestor=cart_key(cart_email)).order(WINE.country)
        wines = cart_query.fetch()

        cost_key = ndb.Key('TotalCost', user.email())
        if cost_key.get():
            temp_cost = cost_key.get().cost
        else:
            temp_cost = 0

        template_values = {
            'wines': wines,
            'total_cost': temp_cost,
            'cart_email': cart_email
        }

        template = JINJA_ENVIRONMENT.get_template('shoppingcart.html')
        self.response.write(template.render(template_values))

    def post(self):
        user = users.get_current_user()
        cost_key = ndb.Key('TotalCost', user.email())
        temp_cost = cost_key.get()

        if self.request.get('song_del_id'):
            if user:
                del_key_id = self.request.get('song_del_id')
                del_key = ndb.Key('Cart', user.email(), 'WINE', int(del_key_id)) #have to use int to construct key id

                temp_cost.cost = temp_cost.cost - del_key.get().price
                temp_cost.put()

                del_key.delete()

            else:
                self.redirect(users.create_login_url('/shoppingcart'))
                return
        if self.request.get('purchase'):
            cart_wines = WINE.query(ancestor=cart_key(user.email())).fetch()
            for cart_wine in cart_wines:
                temp_cost.cost = temp_cost.cost - cart_wine.price
                temp_cost.put()
                cart_wine.key.delete()

        self.redirect('/shoppingcart')
# [END shopping cart]

# [start purchase]
class Purchase(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        cost_key = ndb.Key('TotalCost', user.email())
        temp_cost = cost_key.get()

        purchased = Purchased(parent=cart_key(user.email()))
        purchased.total_cost = 0

        cart_wines = WINE.query(ancestor=cart_key(user.email())).fetch()
        for cart_wine in cart_wines:
            temp_cost.cost = temp_cost.cost - cart_wine.price
            temp_cost.put()

            wine = WINE(parent=cart_key(user.email()))
            wine.country = cart_wine.country
            wine.region = cart_wine.region
            wine.name = cart_wine.name
            wine.variety = cart_wine.variety
            wine.price = cart_wine.price
            wine.year = cart_wine.year

            purchased.wine_list.append(wine)
            purchased.total_cost = purchased.total_cost + cart_wine.price
            purchased.put()
            cart_wine.key.delete()

        template_values = {
        }

        template = JINJA_ENVIRONMENT.get_template('purchased.html')
        self.response.write(template.render(template_values))
# [END purchase]

# [start purchase history]
class History(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        purchased_history = Purchased.query(ancestor=cart_key(user.email())).fetch()
        template_values = {
            'purchased_history': purchased_history,
            'cart_email': user.email()
        }

        template = JINJA_ENVIRONMENT.get_template('history.html')
        self.response.write(template.render(template_values))

# [END purchase history]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/enter', Enter),
    ('/browse', Browse),
    ('/search', Search),
    ('/shoppingcart', ShoppingCart),
    ('/purchase', Purchase),
    ('/history', History)
], debug=True)
# [END app]
