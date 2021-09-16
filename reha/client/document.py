from reha.client.app import routes
from uvcreha import contents
from uvcreha.browser.crud import AddForm, EditForm, DefaultView
from uvcreha.browser.form import JSONForm
from wtforms.fields import SelectField
from reha.prototypes.workflows.document import document_workflow


@routes.register("/users/{uid}/file/{az}/docs/{docid}", name="doc.view")
class DocumentIndex(DefaultView):
    title = "Document"

    def update(self):
        self.content_type = self.request.app.utilities['contents']["document"]
        self.crud = self.content_type.bind(
            self.request.app,
            self.request.get_database()
        )
        self.context = self.crud.find_one(**self.params)

    def get_initial_data(self):
        return self.context.dict()

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema, exclude=(
                'creation_date', # auto-added value
                'state', # workflow state
                'item', # content_type based
            )
        )


def alternatives(name, form):
    alts = []
    for key, versions in contents.documents_store.items():
        if versions:
            latest = versions.get()
            alts.append((
                f'{key}.{latest.identifier}',
                latest.value.get('title', key)
            ))
    return SelectField(
        'Select your content type', choices=alts).bind(form, name)


@routes.register(
    "/users/{uid}/files/{az}/add_document", name="file.new_doc")
class AddDocument(AddForm):
    title = "Dokument anlegen"
    readonly = ('az', 'uid')

    def update(self):
        self.content_type = self.request.app.utilities['contents']["document"]
        self.crud = self.content_type.bind(
            self.request.app,
            self.request.get_database()
        )

    def create(self, data):
        return self.crud.create({
            **self.params,
            **data,
            'state': document_workflow.default_state.name
        }, self.request)

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema,
            include=('az', 'uid', 'docid', 'content_type')
        )

    def setupForm(self, data=None, formdata=None):
        form = self.get_form()
        form._fields['content_type'] = alternatives('content_type', form)
        form.process(data=self.params, formdata=formdata)
        if self.readonly is not None:
            form.readonly(self.readonly)
        return form


@routes.register(
    "/users/{uid}/file/{az}/docs/{docid}/edit", name="doc.edit")
class DocumentEdit(EditForm):
    title = "Document"
    readonly = ('uid', 'az', 'docid', 'content_type')

    def update(self):
        self.content_type = self.request.app.utilities['contents']["document"]
        self.crud = self.content_type.bind(
            self.request.app,
            self.request.get_database()
        )
        self.context = self.crud.find_one(**self.params)

    def get_initial_data(self):
        return self.context.dict()

    def apply(self, data):
        return self.crud.update(self.context, data, self.request)

    def remove(self, item):
        return self.crud.delete(item, self.request)

    def get_form(self):
        return JSONForm.from_schema(
            self.content_type.schema, exclude=(
                'creation_date', # auto-added value
                'state', # workflow state
                'item', # content_type based
            )
        )

    def setupForm(self, data=None, formdata=None):
        form = self.get_form()
        form._fields['content_type'] = alternatives('content_type', form)
        form.process(data=self.params, formdata=formdata)
        if self.readonly is not None:
            form.readonly(self.readonly)
        return form
