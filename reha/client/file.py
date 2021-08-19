from reha.client.app import backend, ui, AdminRequest, TEMPLATES
from uvcreha.browser.crud import EditForm, AddForm, DefaultView
from uvcreha.browser.form import Form
from uvcreha import contenttypes
from uvcreha.workflow import file_workflow


@backend.register("/users/{uid}/file/{az}", name="file.view")
class FileIndex(DefaultView):
    title = "File"

    def update(self):
        self.content_type = contenttypes.registry['file']

    def get_initial_data(self):
        binding = self.content_type.bind(self.request.database)
        return binding.find_one(**self.params)

    def get_form(self):
        return Form.from_schema(
            self.content_type.schema, include=("uid", "az", "mnr", "vid")
        )


@backend.register("/users/{uid}/add_file", name="user.new_file")
class AddFile(AddForm):
    title = "Benutzer anlegen"
    readonly = ('uid',)

    def update(self):
        self.content_type = contenttypes.registry['file']

    def create(self, data):
        crud = self.content_type.get_crud(self.request.app)
        return crud.create({
            **self.params,
            **data,
            'state': file_workflow.states.created.name
        }, self.request)

    def get_form(self):
        return Form.from_schema(
            self.content_type.schema, include=("az", "uid", "mnr", "vid")
        )


@backend.register("/users/{uid}/file/{az}/edit", name="file.edit")
class FileEdit(EditForm):
    title = "File"
    readonly = ('uid', 'az')

    def update(self):
        self.content_type = contenttypes.registry['file']
        self.context = self.content_type.bind(
            self.request.database).find_one(**self.params)

    def get_initial_data(self):
        return self.context

    def apply(self, data):
        crud = self.content_type.get_crud(self.request.app)
        return crud.update(self.context, data, self.request)

    def remove(self, item):
        crud = self.content_type.get_crud(self.request.app)
        return crud.delete(item, self.request)

    def get_form(self):
        return Form.from_schema(
            self.content_type.schema, include=("uid", "az", "mnr", "vid"))


@ui.register_slot(request=AdminRequest, view=FileIndex, name="below-content")
def FileDocumentsList(request, name, view):
    ct = contenttypes.registry['document']
    docs = ct.bind(request.database).find(
        uid=view.context['uid'], az=view.context['az'])
    return TEMPLATES["listing.pt"].render(
        brains=docs, listing_title="Documents")
