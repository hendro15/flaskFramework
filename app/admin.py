from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from wtforms.fields import SelectField, PasswordField
from app import app, db
from models import Entry, Tag, User


class BaseModelView(ModelView):
    pass


class SlugModelView(BaseModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super(SlugModelView, self).on_model_change(form, model, is_created)


class EntryModelView(ModelView):
    _status_choices = [(choice, label) for choice, label in [
        (Entry.STATUS_PUBLIC, 'Public'),
        (Entry.STATUS_DRAFT, 'Draft'),
        (Entry.STATUS_DELETED, 'Deleted'),
    ]]
    column_choices = {
        'status': _status_choices,
    }
    column_filters = ['status', User.name, User.email, 'created_timestamp']
    column_list = ['title', 'status', 'author', 'tease', 'tag_list', 'created_timestamp']
    column_searchable_list = ['title', 'body']
    # Efficiently SELECT the author
    column_select_related_list = ['author']
    form_ajax_refs = {
        'author': {
            'fields': (User.name, User.email)
        }
    }
    form_args = {
        'status': {'choices': _status_choices, 'coerce': int}
    }
    form_columns = ['title', 'body', 'status', 'author', 'tags']
    form_overrides = {'status': SelectField}


class UserModelView(ModelView):
    column_filters = ('email', 'name', 'active', 'admin')
    column_list = ['email', 'name', 'active', 'admin', 'created_timestamp']
    column_searchable_list = ['name', 'email']
    form_columns = ['email', 'password', 'name', 'active', 'admin']
    form_extra_fields = {
        'password': PasswordField('New Password')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password_hash = User.make_password(form.password.data)
        return super(UserModelView, self).on_model_change(form, model, is_created)


class BlogFileAdmin(FileAdmin):
    pass


admin = Admin(app, 'Admin Site')
admin.add_view(EntryModelView(Entry, db.session))
admin.add_view(SlugModelView(Tag, db.session))
admin.add_view(UserModelView(User, db.session))
admin.add_view(BlogFileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))
