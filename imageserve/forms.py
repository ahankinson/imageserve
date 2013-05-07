from django import forms
from django.db import models
from imageserve.helpers import get_by_ismi_id
from south.modelsinspector import add_introspection_rules
import re
from json import loads, dumps


add_introspection_rules([], ["^imageserve\.forms\.IntegerListField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeFormField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeWidget"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListFormField"])
add_introspection_rules([], ["^imageserve\.forms\.PageRangeListWidget"])
add_introspection_rules([], ["^imageserve\.forms\.FolioPagesField"])


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


def folios(**kwargs):
   """
   Generator for folio numbers. Optional keyword argument `start`
   lets you specify a different start point, non-inclusive. Must be a
   valid folio number, or else stuff will break.
   """
   suffixes = {True: 'a', False: 'b'}
   unsuff = dict((v,k) for k,v in suffixes.items())
   start = kwargs.get('start', '0b')
   for k, suff in re.findall(r'(\d+)(a|b)', start): pass
   k = int(k)
   while True:
       if not unsuff[suff]: k += 1
       suff = suffixes[not unsuff[suff]]
       yield str(k)+suff


class FolioPages(object):
    """
    Provides a correspondence between the image numbers in a manuscript
    and the folio numbers on each page.
    
    If no folio list is provided, the keyword argument
    `num_pages` is required.
    """
    def __init__(self, folios_list=None, **kwargs):
        if folios_list is None:
            num_pages = kwargs.get('num_pages')
            if not num_pages:
                msg = ('If no folio list is provided, '
                + 'keyword argument `num_pages` is required')
                raise Exception(msg)
            folios_list = [[] for _ in range(num_pages)]
        gen = enumerate(folios_list, start=1)
        self._folio_pages = dict(gen)
    
    def get_page(self, folio):
        """
        Given a folio number in string form, return the first page on which
        that folio number occurs.
        """
        if folio.isdigit():
            folio = '{0}a'.format(folio)
        for v in self._folio_pages.itervalues():
            if folio in v:
                return min(k for k,v in self._folio_pages.iteritems() if folio in v)
    
    def interpolate_after(self, page, **kwargs):
        """
        Given a page on which a folio number has been chosen, start
        counting and assigning folio numbers to the subsequent pages until
        another page for which a folio number has been chosen is reached.
        
        The optional keyword argument `overwrite` allows you to set ALL the
        folio numbers after the selected page in this manner, regardless
        of whether those pages have folio numbers chosen or not.
        """
        overwrite = kwargs.get('overwrite', False)
        if self._folio_pages[page]:
            zipped = zip(self._folio_pages.items()[page:],
                         folios(start=self.get_folio(page)))
            for ((key, vals), folio) in zipped:
                if not overwrite:
                    if vals:
                        return
                self._folio_pages[key] = [folio]
        else:
            msg = "Cannot interpolate without a starting point"
            raise Exception(msg)
    
    def get_folio(self, page):
        """
        Given a page number, returns the "earliest" folio number on that page.
        """
        for i, n in zip(folios(),self._folio_pages):
            if i in self._folio_pages[page]:
                return i
    
    def clear_page(self, page):
        """
        Removes all folio numbers from the specified page.
        """
        self._folio_pages[page] = []
    
    def __setitem__(self, key, value):
        """
        Sets the folio number for the chosen page. NB: after using this syntax
        the chosen page will have ONLY the selected folio number; any others will
        be overwritten. To avoid this, use add_folio.
        """
        self._folio_pages[key] = [value]
    
    def add_folio(self, page, folio):
        """
        Adds the specified folio number to the list of folio numbers on the specified
        page.
        """
        self._folio_pages[page].append(folio)
    
    def __str__(self):
        return dumps(self._folio_pages.values())


class FolioPagesField(models.Field):
    description = ('JSON object describing the correspondence '
    + 'between page numbers and folio numbers')
    __metaclass__ = models.SubfieldBase
    
    def db_type(self, connection):
        return 'char(25000)' # perhaps this is excessive...
    
    def to_python(self, value):
        if isinstance(value, FolioPages):
            return value
        if value == 'None':
            return None
        if value:
            folios_list = loads(value)
            return FolioPages(folios_list)
    
    def get_prep_value(self, value):
        return str(value)
    
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class IntegerListField(models.Field):
    description = 'A list of integers'
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'char(500)'

    def to_python(self, value):
        if isinstance(value, (list, tuple)):
            return list(value)
        value = value.strip()
        if value:
            return map(int, value.split(','))
        return []

    def get_prep_value(self, value):
        return ','.join(map(str, value))

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class PageRangeListField(models.Field):
    description = 'A list of page ranges'
    __metaclass__ = models.SubfieldBase

    def db_type(self, connection):
        return 'char(500)'

    def to_python(self, value):
        if isinstance(value, PageRangeList):
            return value
        if isinstance(value, (list, tuple)):
            return PageRangeList(value)
        value = value.strip()
        if value:
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
                if ((pages.first <= other_pages.first and other_pages.first <= pages.last) or
                   (other_pages.first <= pages.first and pages.first <= other_pages.last)):
                    raise forms.ValidationError('Overlapping page ranges')
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
                        'First page must come before last page'
                    )
            elif first or last:
                raise forms.ValidationError('Enter a first AND last page')
        raise forms.ValidationError('This form is required')


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
                if ((pages.first <= other_pages.first and other_pages.first <= pages.last) or
                   (other_pages.first <= pages.first and pages.first <= other_pages.last)):
                    raise forms.ValidationError('Overlapping page ranges')
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
        header = u"""<tr>
            <th>Witness</th>
            <th>First Page</th>
            <th>Last Page</th>
        </tr>"""
        zipped = zip(labels, rendered_widgets)
        prerenders = [u'<tr><td>' + l + u'</td>' + w + u'</tr>' for l, w in zipped]
        rows = u'\n'.join(prerenders)
        return u'<table>' + header + rows + u'</table>'
