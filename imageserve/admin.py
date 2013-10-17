from django.contrib import admin
from django.conf import settings
from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from guardian.admin import GuardedModelAdmin
# from imageserve.helpers import register_defs, register_manuscripts
# from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting, CacheTable, ISMIEntity
from imageserve.models import Manuscript
from imageserve.models import ManuscriptGroup
from imageserve.models import Witness
from imageserve.models import Text
from imageserve.models import Person
from imageserve.models import AttributeDisplay
from imageserve.models import RelationshipDisplay
from imageserve.ismi.witness import fetch_mss_witnesses

# from imageserve.forms import PageRangeListFormField


class ManuscriptAdminForm(forms.ModelForm):
    """
    Custom admin form to take care of dynamically generating
    the form widget corresponding to the page numbers of the
    witnesses in a codex.
    """
    class Meta:
        model = Manuscript

    # def __init__(self, *args, **kwargs):
    #     super(ManuscriptAdminForm, self).__init__(*args, **kwargs)
    #     instance = kwargs.get('instance')
    #     if instance:
    #         wits = instance.witnesses
    #         if wits:
    #             self.fields['witness_pages'] = PageRangeListFormField(wits)


def update_witnesses(modeladmin, request, queryset):
    fetch_mss_witnesses(queryset)


class ManuscriptAdmin(GuardedModelAdmin):
    search_fields = ('directory',)
    list_display = ('ms_name', 'ismi_id', 'directory', 'num_files')
    actions = (update_witnesses,)


class ManuscriptGroupAdmin(GuardedModelAdmin):
    filter_horizontal = ('manuscripts',)


class WitnessAdmin(GuardedModelAdmin):
    search_fields = ('manuscript__ismi_id', 'manuscript__directory', 'name')
    list_display = ('name', 'ismi_id', 'manuscript_name', 'folios', 'start_folio', 'end_folio')
    ordering = ('manuscript__directory', 'folios')


class TextAdmin(GuardedModelAdmin):
    pass


class PersonAdmin(GuardedModelAdmin):
    pass

class AttributeDisplayAdmin(GuardedModelAdmin):
    pass


class RelationshipDisplayAdmin(GuardedModelAdmin):
    pass

# class AttSettingListFilter(admin.SimpleListFilter):
#     title = _('type of object')
#     parameter_name = 'oc'

#     def lookups(self, request, model_admin):
#         qs = model_admin.queryset(request)
#         return tuple(
#             (oc, _(oc)) for oc in sorted(set(m.oc for m in qs))
#         )

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(oc=self.value())
#         return queryset


# class AttSettingAdmin(admin.ModelAdmin):
#     list_filter = (AttSettingListFilter,)


# class RelSettingListFilter(admin.SimpleListFilter):
#     title = _('between objects of type')
#     parameter_name = 'oc'

#     def lookups(self, request, model_admin):
#         qs = model_admin.queryset(request)
#         return tuple(
#             (oc, oc) for oc in sorted(set(m.tar_oc for m in qs).union(set(m.src_oc for m in qs)))
#         )

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(Q(tar_oc=self.value()) | Q(src_oc=self.value()))
#         return queryset


# class RelSettingAdmin(admin.ModelAdmin):
#     list_filter = (RelSettingListFilter,)


# class CacheTableAdmin(admin.ModelAdmin):
#     list_display = ('cache_key', 'expires')
#     search_fields = ('cache_key',)

admin.site.register(Manuscript, ManuscriptAdmin)
admin.site.register(ManuscriptGroup, ManuscriptGroupAdmin)
admin.site.register(Witness, WitnessAdmin)
admin.site.register(Text, TextAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(AttributeDisplay, AttributeDisplayAdmin)
admin.site.register(RelationshipDisplay, RelationshipDisplayAdmin)
# admin.site.register(AttDisplaySetting, AttSettingAdmin)
# admin.site.register(RelDisplaySetting, RelSettingAdmin)
# admin.site.register(CacheTable, CacheTableAdmin)
# admin.site.register(ISMIEntity)


# if settings.UPDATE_DEFS:
#     register_defs()

# if settings.UPDATE_MANUSCRIPTS:
#     register_manuscripts()
