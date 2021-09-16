from fanstatic import Library, Resource
from reiter.application.browser import registries, TemplateLoader
from reiter.view.utils import routables
from roughrider.routing.route import NamedRoutes
from uvcreha.browser.login import LoginForm
from uvcreha.request import Request
from uvcreha.browser import Page


TEMPLATES = TemplateLoader("./templates")
library = Library("reha.client", "static")
htmx = Resource(library, 'htmx.js', bottom=True)
css = Resource(library, 'admin.css')

routes = NamedRoutes(extractor=routables)
ui = registries.UIRegistry()


class AdminRequest(Request):
    pass


@routes.register("/")
class Index(Page):
    template = TEMPLATES['index']
    listing = TEMPLATES['listing']

    def update(self):
        htmx.need()
        self.base = self.request.environ['SCRIPT_NAME']

    def get_users(self, query: str=''):
        ct = self.request.app.utilities['contents']["user"]
        crud = ct.bind(
            self.request.app,
            self.request.get_database()
        )
        users = crud.find()
        if not query:
            return users
        return [user for user in users if user.title.startswith(query)]

    def GET(self):
        users = self.get_users()
        return {'brains': users, "listing_title": "Users"}

    def POST(self):
        data = self.request.extract()
        query = data.form.get('search')
        users = self.get_users(query)
        return self.listing.render(
            brains=users,
            listing_title=query and f"Users (search for {query})" or "Users"
        )


routes.register("/login")(LoginForm)


@ui.register_slot(request=AdminRequest, name="sitecap")
def sitecap(request, name, view):
    return ''


@ui.register_slot(request=AdminRequest, name="footer")
def footer(request, name, view):
    return TEMPLATES["footer.pt"].render(request=request)
