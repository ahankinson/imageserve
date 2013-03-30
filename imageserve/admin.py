from django.contrib import admin
from django import forms
from guardian.admin import GuardedModelAdmin
from imageserve.helpers import register_defs, register_manuscripts
from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting
from imageserve.forms import PageRangeListFormField


class ManuscriptAdminForm(forms.ModelForm):
    '''
    Custom admin form to take care of dynamically generating
    the form widget corresponding to the page numbers of the
    witnesses in a codex.
    '''
    class Meta:
        model = Manuscript

    def __init__(self, *args, **kwargs):
        super(ManuscriptAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            if instance.witnesses:
                self.fields['witness_pages'] = PageRangeListFormField(instance.witnesses)


class ManuscriptAdmin(GuardedModelAdmin):
    form = ManuscriptAdminForm
    readonly_fields = ('num_files',)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ('witness_pages', 'num_files')
        if obj:
            self.exclude = ('witness_pages',)
            if obj.witnesses:
                self.exclude = ()
        return super(ManuscriptAdmin, self).get_form(request, obj, **kwargs)


class ManuscriptGroupAdmin(GuardedModelAdmin):
    pass

# admin.site.register(models.Manuscript, models.ManuscriptAdmin)
admin.site.register(Manuscript, ManuscriptAdmin)
admin.site.register(ManuscriptGroup, ManuscriptGroupAdmin)
admin.site.register(AttDisplaySetting)
admin.site.register(RelDisplaySetting)

register_defs()
register_manuscripts()
