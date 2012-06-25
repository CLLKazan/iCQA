import os
from string import strip
from django import forms
from forum.settings.base import Setting
from django.utils.translation import ugettext as _
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse

class DummySetting:
    pass

class UnfilteredField(forms.CharField):
    def clean(self, value):
            return value


class SettingsSetForm(forms.Form):
    def __init__(self, set, data=None, unsaved=None, *args, **kwargs):
        initial = dict([(setting.name, setting.value) for setting in set])

        if unsaved:
            initial.update(unsaved)

        super(SettingsSetForm, self).__init__(data, initial=initial, *args, **kwargs)

        for setting in set:
            widget = setting.field_context.get('widget', None)

            if widget is forms.CheckboxSelectMultiple or widget is forms.SelectMultiple or isinstance(widget, forms.SelectMultiple):
                field = forms.MultipleChoiceField(**setting.field_context)
            elif widget is forms.RadioSelect or isinstance(widget, forms.RadioSelect):
                field = forms.ChoiceField(**setting.field_context)
            elif isinstance(setting, (Setting.emulators.get(str, DummySetting), Setting.emulators.get(unicode, DummySetting))):
                if not setting.field_context.get('widget', None):
                    setting.field_context['widget'] = forms.TextInput(attrs={'class': 'longstring'})
                field = forms.CharField(**setting.field_context)
            elif isinstance(setting, Setting.emulators.get(float, DummySetting)):
                field = forms.FloatField(**setting.field_context)
            elif isinstance(setting, Setting.emulators.get(int, DummySetting)):
                field = forms.IntegerField(**setting.field_context)
            elif isinstance(setting, Setting.emulators.get(bool, DummySetting)):
                field = forms.BooleanField(**setting.field_context)
            else:
                field = UnfilteredField(**setting.field_context)

            self.fields[setting.name] = field

        self.set = set

    def as_table(self):
        return self._html_output(
                u'<tr><th>%(label)s' + ('<br /><a class="fieldtool context" href="#">%s</a><span class="sep">|</span><a class="fieldtool default" href="#">%s</a></th>' % (
                    _('context'), _('default'))) + u'<td>%(errors)s%(field)s%(help_text)s</td>',
                u'<tr><td colspan="2">%s</td></tr>', '</td></tr>', u'<br />%s', False)

    def save(self):
        for setting in self.set:
            setting.set_value(self.cleaned_data[setting.name])

class ImageFormWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return """
            <img src="%(value)s" /><br />
            %(change)s: <input type="file" name="%(name)s" />
            <input type="hidden" name="%(name)s_old" value="%(value)s" />
            """ % {'name': name, 'value': value, 'change': _('Change this:')}

    def value_from_datadict(self, data, files, name):
        if name in files:
            f = files[name]

            # check file type
            file_name_suffix = os.path.splitext(f.name)[1].lower()

            if not file_name_suffix in ('.jpg', '.jpeg', '.gif', '.png', '.bmp', '.tiff', '.ico'):
                raise Exception('File type not allowed')

            from forum.settings import UPFILES_FOLDER, UPFILES_ALIAS

            storage = FileSystemStorage(str(UPFILES_FOLDER), str(UPFILES_ALIAS))
            new_file_name = storage.save(f.name, f)
            return str(UPFILES_ALIAS) + new_file_name
        else:
            if "%s_old" % name in data:
                return data["%s_old" % name]
            elif name in data:
                return data[name]

class StringListWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        ret = ""
        for s in value:
            ret += """
            <div class="string-list-input">
                <input type="text" name="%(name)s" value="%(value)s" />
                <button class="string_list_widget_button">-</button>
            </div>
            """  % {'name': name, 'value': s}

        return """
            <div class="string_list_widgets">
                %(ret)s
                <div><button name="%(name)s" class="string_list_widget_button add">+</button></div>
            </div>
            """ % dict(name=name, ret=ret)

    def value_from_datadict(self, data, files, name):
        if 'submit' in data:
            return data.getlist(name)
        else:
            return data[name]

class CommaStringListWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        return super(CommaStringListWidget, self).render(name, ', '.join(value), attrs)


    def value_from_datadict(self, data, files, name):
        if 'submit' in data:
            return map(strip, data[name].split(','))
        else:
            return ', '.join(data[name])    

class TestEmailSettingsWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        if not value:
            value = ''

        return """
            <div id="test_email_settings">
                <a href="%s" onclick="return false;" class="button test_button" href="/">Test</a>

                <div style="margin-top: 7px">
                <div style="display: none" class="ajax_indicator">
                    Testing your current e-mail settings. Please, wait.
                </div>
                <div class="test_status"></div>
                </div>
            </div>
            """ % reverse("test_email_settings")