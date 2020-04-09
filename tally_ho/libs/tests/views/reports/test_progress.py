from django.core.exceptions import ImproperlyConfigured

from tally_ho.apps.tally.models.result_form import ResultForm
from tally_ho.libs.models.enums.form_state import FormState
from tally_ho.libs.tests.test_base import create_result_form, \
    create_center, create_tally, create_reconciliation_form, TestBase
from tally_ho.libs.reports import progress


class TestProgress(TestBase):
    def setUp(self):
        self.center = create_center()
        self.center_2 = create_center(code=2, office_name='office2')
        self._create_and_login_user()
        self.tally = create_tally()
        self.tally.users.add(self.user)

        for i in range(1, 11):
            create_result_form(
                center=self.center if i >= 2 else self.center_2,
                station_number=i,
                tally=self.tally,
                barcode=i,
                serial_number=i,
                form_state=i - 1)

        self.assertEqual(ResultForm.objects.count(), 10)

    def test_progress_report(self):
        report = progress.ExpectedProgressReport(self.tally.id)
        report.queryset = None
        report.filtered_queryset = None
        with self.assertRaises(ImproperlyConfigured):
            report.total
        with self.assertRaises(ImproperlyConfigured):
            report.number

    def test_expected_progress_report(self):
        report = progress.ExpectedProgressReport(self.tally.id)
        self.assertEqual(report.number, 10)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 100.0)

    def test_intaken_progress_report(self):
        report = progress.IntakenProgressReport(self.tally.id)
        self.assertEqual(report.number, 9)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 90.0)

    def test_archived_progress_report(self):
        report = progress.ArchivedProgressReport(self.tally.id)
        self.assertEqual(report.number, 1)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 10)

    def test_clearance_progress_report(self):
        report = progress.ClearanceProgressReport(self.tally.id)
        self.assertEqual(report.number, 1)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 10)

    def test_audit_progress_report(self):
        report = progress.AuditProgressReport(self.tally.id)
        self.assertEqual(report.number, 1)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 10)

    def test_not_receieved_progress_report(self):
        report = progress.NotRecievedProgressReport(self.tally.id)
        self.assertEqual(report.number, 1)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 10)

    def test_progress_for_office(self):
        report = progress.ExpectedProgressReport(self.tally.id)
        self.assertEqual(report.number, 10)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.percentage, 100.0)

    def test_valid_votes_per_office(self):
        result_form = ResultForm.objects.get(
            form_state=FormState.QUALITY_CONTROL)
        create_reconciliation_form(result_form, self.user)
        report = progress.ValidVotesProgressReport(self.tally.id)
        valid_votes = report.for_center_office(
            self.center.office, query_valid_votes=True)
        self.assertEqual(valid_votes, 1)

    def test_zero_valid_votes_per_office(self):
        report = progress.ValidVotesProgressReport(self.tally.id)
        valid_votes = report.for_center_office(
            self.center.office, query_valid_votes=True)
        self.assertEqual(valid_votes, 0)
