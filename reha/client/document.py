from reha.client.app import backend
from uvcreha import jsonschema, contenttypes
from uvcreha.browser.crud import AddForm, EditForm, DefaultView
from uvcreha.browser.form import Form
from wtforms.fields import SelectField


@backend.register("/users/{uid}/file/{az}/docs/{docid}", name="doc.view")
class DocumentIndex(DefaultView):
    title = "Document"

    def update(self):
        self.content_type = contenttypes.registry['document']

    def get_initial_data(self):
        binding = self.content_type.bind(self.request.database)
        return binding.find_one(**self.params)

    def get_form(self):
        return Form.from_schema(
            self.content_type.schema, exclude=(
                'creation_date', # auto-added value
                'state', # workflow state
                'item', # content_type based
            )
        )


def alternatives(name, form):
    alts = []
    for key, versions in jsonschema.documents_store.items():
        if versions:
            latest = versions.get()
            alts.append((
                f'{key}.{latest.number}',
                latest.value.get('title', key)
            ))
    return SelectField(
        'Select your content type', choices=alts).bind(form, name)


@backend.register(
    "/users/{uid}/files/{az}/add_document", name="file.new_doc")
class AddDocument(AddForm):
    title = "Dokument anlegen"
    readonly = ('az', 'uid')

    def update(self):
        self.content_type = contenttypes.registry['document']

    def create(self, data):
        crud = self.content_type.get_crud(self.request.app)
        return crud.create({**self.params, **data}, self.request)

    def get_form(self):
        return Form.from_schema(
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


@backend.register(
    "/users/{uid}/file/{az}/docs/{docid}/edit", name="doc.edit")
class DocumentEdit(EditForm):
    title = "Document"
    readonly = ('uid', 'az', 'docid', 'content_type')

    def update(self):
        self.content_type = contenttypes.registry['document']
        self.context = self.content_type.bind(
            self.request.database).find_one(**self.params)

    def get_initial_data(self):
        binding = self.content_type.bind(self.request.database)
        return binding.find_one(**self.params)

    def apply(self, data):
        crud = self.content_type.get_crud(self.request.app)
        return crud.update(self.context, data, self.request)

    def remove(self, item):
        crud = self.content_type.get_crud(self.request.app)
        return crud.delete(item, self.request)

    def get_form(self):
        return Form.from_schema(
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
