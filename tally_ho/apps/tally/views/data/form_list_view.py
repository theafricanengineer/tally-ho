from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.core.urlresolvers import reverse

from djqscsv import render_to_csv_response
from guardian.mixins import LoginRequiredMixin

from tally_ho.apps.tally.models.ballot import Ballot
from tally_ho.apps.tally.models.result_form import ResultForm
from tally_ho.libs.models.enums.form_state import FormState
from tally_ho.libs.permissions import groups
from tally_ho.libs.views import mixins


ALL = '__all__'


class FormListDataView(LoginRequiredMixin,
                       mixins.GroupRequiredMixin,
                       mixins.TallyAccessMixin,
                       BaseDatatableView):
    group_required = groups.SUPER_ADMINISTRATOR
    model = ResultForm
    columns = (
        'barcode',
        'center.code',
        'station_number',
        'center.office.name',
        'center.office.number',
        'ballot.number',
        'ballot.race_type',
        'form_state',
        'modified_date',
    )

    def get_queryset(self):
        qs = super(FormListDataView, self).get_queryset()
        ballot_number = self.kwargs.get('ballot')
        tally_id = self.kwargs.get('tally_id')

        qs = qs.filter(tally__id=tally_id)

        if ballot_number:
            ballot = Ballot.objects.get(number=ballot_number, tally__id=tally_id)
            qs = qs.filter(
                ballot__number__in=ballot.form_ballot_numbers)

        return qs


class FormListView(LoginRequiredMixin,
                   mixins.GroupRequiredMixin,
                   mixins.TallyAccessMixin,
                   TemplateView):
    group_required = groups.SUPER_ADMINISTRATOR
    template_name = "data/forms.html"

    def get(self, *args, **kwargs):
        form_state = kwargs.get('state')
        tally_id = kwargs.get('tally_id')

        if form_state:
            if form_state == ALL:
                form_list = ResultForm.objects.filter(tally__id=tally_id)
            else:
                form_state = FormState[form_state.upper()]
                form_list = ResultForm.forms_in_state(form_state.value, tally_id=tally_id)

            form_list = form_list.values(
                'barcode', 'form_state', 'gender', 'station_number',
                'center__sub_constituency__code',
                'center__code',
                'ballot__race_type').order_by('barcode')

            return render_to_csv_response(form_list)

        return self.render_to_response(
            self.get_context_data(header_text=_('Form List'),
                                  remote_url=reverse('form-list-data',
                                                     kwargs={'tally_id':tally_id}),
                                  tally_id=tally_id))


class FormNotReceivedListView(FormListView):
    group_required = groups.SUPER_ADMINISTRATOR

    def get(self, *args, **kwargs):
        format_ = kwargs.get('format')
        tally_id = kwargs.get('tally_id')

        if format_ == 'csv':
            form_list = ResultForm.forms_in_state(FormState.UNSUBMITTED, tally_id=tally_id)
            return render_to_csv_response(form_list)

        return self.render_to_response(
            self.get_context_data(header_text=_('Forms Not Received'),
                                  custom=True,
                                  remote_url=reverse('form-not-received-data',
                                      kwargs={'tally_id':tally_id}),
                                  tally_id=tally_id))


class FormNotReceivedDataView(FormListDataView):
    queryset = ResultForm.forms_in_state(FormState.UNSUBMITTED)


class FormsForRaceView(FormListView):
    group_require = groups.SUPER_ADMINISTRATOR

    def get(self, *args, **kwargs):
        ballot = kwargs.get('ballot')
        tally_id = kwargs.get('tally_id')

        return self.render_to_response(self.get_context_data(
            header_text=_('Forms for Race %s' % ballot),
            none=True,
            tally_id=tally_id,
            remote_url=reverse('forms-for-race-data', args=[tally_id, ballot])))
