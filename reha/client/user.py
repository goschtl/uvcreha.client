from collections import defaultdict, Counter
from uvcreha.browser.form import JSONForm
from uvcreha.browser.crud import AddForm, EditForm
from reha.prototypes.workflows.user import user_workflow
from reha.client.app import routes, TEMPLATES
from uvcreha.browser import Page


@routes.register("/users/{uid}", name="user.view")
class UserIndex(Page):
    template = TEMPLATES['user_lp']
    listing = TEMPLATES['listing']

    def update(self):
        self.uid = self.params['uid']
        self.content_type, self.crud = self.request.get_crud('user')
        self.context = self.crud.fetch(self.uid)

    def GET(self):
        ct, crud = self.request.get_crud('file')
        files = crud.find(uid=self.uid)

        docs = defaultdict(list)
        counters = defaultdict(Counter)

        ct, crud = self.request.get_crud('document')
        for doc in crud.find(uid=self.uid):
            docs[doc.az].append(doc)
            counters[doc.az].update([doc.state])
        return {
            'files': files,
            'docs': docs,
            'counters': counters
        }


@routes.register("/user.add", name="user.add")
class AddUserForm(AddForm):
    title = "Benutzer anlegen"

    def update(self):
        self.content_type, self.crud = self.request.get_crud('user')

    def create(self, data):
        return self.crud.create(
            {
                **data,
                "state": user_workflow.states.pending.name
            },
            self.request
        )

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema,
            include=("uid", "loginname", "password", "email")
        )


@routes.register("/users/{uid}/edit", name="user.edit")
class EditUserForm(EditForm):
    title = "Benutzer anlegen"
    readonly = ('uid',)

    def update(self):
        self.uid = self.params['uid']
        self.content_type, self.crud = self.request.get_crud('user')
        self.context = self.crud.fetch(self.uid)

    def get_initial_data(self):
        return self.context.to_dict()

    def apply(self, data) -> None:
        return self.crud.update(self.context, data, self.request)

    def remove(self, item) -> None:
        return self.crud.delete(item, self.request)

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema, include=(
                "uid", "loginname", "password", "email"
            )
        )
