from reha.client.app import routes, ui, AdminRequest, TEMPLATES
from uvcreha.browser.crud import EditForm, AddForm, DefaultView
from uvcreha.browser.form import JSONForm
from reha.prototypes.workflows.file import file_workflow


@routes.register("/users/{uid}/file/{az}", name="file.view")
class FileIndex(DefaultView):
    title = "File"

    def update(self):
        self.content_type, self.crud = self.request.get_crud('file')
        self.context = self.crud.find_one(**self.params)

    def get_initial_data(self):
        return self.context.to_dict()

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema,
            include=("uid", "az", "mnr", "vid")
        )


@routes.register("/users/{uid}/add_file", name="user.new_file")
class AddFile(AddForm):
    title = "Benutzer anlegen"
    readonly = ('uid',)

    def update(self):
        self.content_type, self.crud = self.request.get_crud('file')

    def create(self, data):
        return self.crud.create(
            {
                **self.params,
                **data,
                'state': file_workflow.states.created.name
            },
            self.request
        )

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema,
            include=("az", "uid", "mnr", "vid")
        )


@routes.register("/users/{uid}/file/{az}/edit", name="file.edit")
class FileEdit(EditForm):
    title = "File"
    readonly = ('uid', 'az')

    def update(self):
        self.content_type, self.crud = self.request.get_crud('file')
        self.context = self.crud.find_one(**self.params)

    def get_initial_data(self):
        return self.context.to_dict()

    def apply(self, data):
        return self.crud.update(self.context, data, self.request)

    def remove(self, item):
        return self.crud.delete(item, self.request)

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema,
            include=("uid", "az", "mnr", "vid")
        )


@ui.register_slot(
    request=AdminRequest, view=FileIndex, name="below-content")
def FileDocumentsList(request, name, view):
    content_type, crud = request.get_crud('document')
    docs = crud.find(uid=view.context.uid, az=view.context.az)
    return TEMPLATES["listing.pt"].render(
        brains=docs,
        listing_title="Documents"
    )
