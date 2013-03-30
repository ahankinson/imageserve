from django import forms
from django.db import models
# from imageserve.models import Manuscript
from imageserve.helpers import get_by_ismi_id
from south.modelsinspector import add_introspection_rules


add_introspection_rules([], ["^imageserve\.forms\.IntegerListField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeFormField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeWidget"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListFormField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListWidget"])


class PageRange(object):
    def __init__(self, first, last):
        self.first = first
        self.last = last


class PageRangeList(object):
    def __init__(self, page_ranges):
        self._page_ranges = page_ranges

    def __iter__(self):
        for pages in self._page_ranges:
            yield pages

    def __getitem__(self, key):
        return self._page_ranges[key]


class IntegerListField(models.Field):
    description = "A list of integers"
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'char(500)'

    def to_python(self, value):
        if value:
            if isinstance(value, (list, tuple)):
                return list(value)
            return map(int, value.split(','))
        return []

    def get_prep_value(self, value):
        return ','.join(map(str, value))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class PageRangeListField(models.Field):
    description = "A list of page ranges"
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'char(500)'

    def to_python(self, value):
        if value:
            if isinstance(value, PageRangeList):
                return value
            if isinstance(value, (list, tuple)):
                return PageRangeList(value)
            pages = [tuple(r.split('-')) for r in value.split(',')]
            ret_list = []
            for first, last in pages:
                if first == 'None':
                    ret_list.append(PageRange(None, None))
                else:
                    ret_list.append(PageRange(int(first), int(last)))
            return PageRangeList(ret_list)
        return PageRangeList([])

    def get_prep_value(self, value):
        return ','.join(['-'.join([str(r.first), str(r.last)]) for r in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        for i, pages in enumerate(value):
            for other_pages in value[i+1:]:
                # Can this be simplified a bit? It's quite hard to follow.
                if ((pages.first <= other_pages.first and other_pages.first <= pages.last and pages.last <= other_pages.last) or
                   (other_pages.first <= pages.first and pages.first <= other_pages.last and other_pages.last <= pages.last)):
                    raise forms.ValidationError("Overlapping page ranges")
        return super(PageRangeListField, self).clean(value, model_instance)

    def formfield(self, **kwargs):
        defaults = {'form_class': PageRangeListFormField}
        defaults.update(kwargs)
        return super(PageRangeListField, self).formfield(**defaults)


class PageRangeFormField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        kwargs.update(fields=(forms.IntegerField(required=True),
                              forms.IntegerField(required=True)))
        super(PageRangeFormField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        if data_list:
            first, last = data_list
            if first and last:
                first, last = map(int, data_list)
                if first <= last:
                    return PageRange(first, last)
                else:
                    raise forms.ValidationError(
                        "First page must come before last page"
                    )
            elif first or last:
                raise forms.ValidationError("Enter a first AND last page")
        raise forms.ValidationError("This form is required")


class PageRangeWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        kwargs.update(widgets=(forms.TextInput, forms.TextInput))
        super(PageRangeWidget, self).__init__(*args, **kwargs)

    def decompress(self, value):
        if value:
            first = str(value.first) if value.first else ''
            last = str(value.last) if value.last else ''
            return [first, last]
        return ['', '']

    def format_output(self, rendered_widgets):
        w1, w2 = rendered_widgets
        return u'<td>'+w1+u'</td><td>'+w2+'</td>'


class PageRangeListFormField(forms.MultiValueField):
    def __init__(self, witnesses=[], *args, **kwargs):
        fields = tuple(PageRangeFormField() for w in witnesses)
        widget = PageRangeListWidget(witnesses)
        super(PageRangeListFormField, self).__init__(fields=fields,
                                                     widget=widget)

    def compress(self, data_list):
        for i, pages in enumerate(data_list):
            for other_pages in data_list[i+1:]:
                # Same here -- this needs to be made more readable
                if ((pages.first <= other_pages.first and other_pages.first <= pages.last and pages.last <= other_pages.last) or
                   (other_pages.first <= pages.first and pages.first <= other_pages.last and other_pages.last <= pages.last)):
                    raise forms.ValidationError("Overlapping page ranges")
        return PageRangeList(data_list)


class PageRangeListWidget(forms.MultiWidget):
    def __init__(self, witnesses):
        self.witnesses = witnesses
        widgets = [PageRangeWidget for w in self.witnesses]
        super(PageRangeListWidget, self).__init__(widgets=widgets)

    def decompress(self, value):
        if value:
            return [pages for pages in value]
        return [PageRange(None, None) for w in self.witnesses]

    def format_output(self, rendered_widgets):
        labels = [get_by_ismi_id(w).get('ov') for w in self.witnesses]
        header = u'''<tr>
            <th>Witness</th>
            <th>First Page</th>
            <th>Last Page</th>
        </tr>'''
        zipped = zip(labels, rendered_widgets)
        prerenders = [u'<tr><td>' + l + u'</td>' + w + u'</tr>' for l, w in zipped]
        rows = u'\n'.join(prerenders)
        return u'<table>' + header + rows + u'</table>'
