from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ledger.accounts.models import EmailUser, Profile, Document, RevisionedMixin
from wildlifelicensing.apps.main.models import WildlifeLicence, WildlifeLicenceType, Condition, \
    CommunicationsLogEntry, AssessorGroup, Variant


@python_2_unicode_compatible
class Application(RevisionedMixin):
    CUSTOMER_STATUS_CHOICES = (('temp', 'Temporary'), ('draft', 'Draft'), ('under_review', 'Under Review'),
                               ('id_required', 'Identification Required'),
                               ('returns_required', 'Returns Completion Required'),
                               ('amendment_required', 'Amendment Required'),
                               ('id_and_amendment_required', 'Identification/Amendments Required'),
                               ('id_and_returns_required', 'Identification/Returns Required'),
                               ('returns_and_amendment_required', 'Returns/Amendments Required'),
                               ('id_and_returns_and_amendment_required', 'Identification/Returns/Amendments Required'),
                               ('approved', 'Approved'), ('declined', 'Declined'))

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = ['temp', 'draft', 'amendment_required', 'id_and_amendment_required',
                               'returns_and_amendment_required',
                               'id_and_returns_and_amendment_required']

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = ['under_review', 'id_required', 'returns_required', 'approved']

    PROCESSING_STATUS_CHOICES = (('temp', 'Temporary'), ('draft', 'Draft'), ('new', 'New'), ('renewal', 'Renewal'),
                                 ('licence_amendment', 'Licence Amendment'), ('ready_for_action', 'Ready for Action'),
                                 ('awaiting_applicant_response', 'Awaiting Applicant Response'),
                                 ('awaiting_assessor_response', 'Awaiting Assessor Response'),
                                 ('awaiting_responses', 'Awaiting Responses'),
                                 ('ready_for_conditions', 'Ready for Conditions'),
                                 ('ready_to_issue', 'Ready to Issue'), ('issued', 'Issued'), ('declined', 'Declined'))

    ID_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('awaiting_update', 'Awaiting Update'),
                               ('updated', 'Updated'), ('accepted', 'Accepted'))

    RETURNS_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('awaiting_returns', 'Awaiting Returns'), ('completed', 'Completed'),
        ('accepted', 'Accepted'))

    CHARACTER_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('accepted', 'Accepted'))

    REVIEW_STATUS_CHOICES = (
        ('not_reviewed', 'Not Reviewed'), ('awaiting_amendments', 'Awaiting Amendments'), ('amended', 'Amended'),
        ('accepted', 'Accepted'))

    licence_type = models.ForeignKey(WildlifeLicenceType, blank=True, null=True)
    customer_status = models.CharField('Customer Status', max_length=40, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[0][0])
    data = JSONField(blank=True, null=True)
    documents = models.ManyToManyField(Document)
    hard_copy = models.ForeignKey(Document, blank=True, null=True, related_name='hard_copy')
    correctness_disclaimer = models.BooleanField(default=False)
    further_information_disclaimer = models.BooleanField(default=False)

    applicant = models.ForeignKey(EmailUser, blank=True, null=True, related_name='applicant')
    applicant_profile = models.ForeignKey(Profile, blank=True, null=True)

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateField(blank=True, null=True)

    proxy_applicant = models.ForeignKey(EmailUser, blank=True, null=True, related_name='proxy')

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='assignee')
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    id_check_status = models.CharField('Identification Check Status', max_length=30, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    returns_check_status = models.CharField('Return Check Status', max_length=30, choices=RETURNS_CHECK_STATUS_CHOICES,
                                            default=RETURNS_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=30,
                                              choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=30, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    conditions = models.ManyToManyField(Condition, through='ApplicationCondition')

    licence = models.ForeignKey(WildlifeLicence, blank=True, null=True)

    previous_application = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    is_licence_amendment = models.BooleanField(default=False)

    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    variants = models.ManyToManyField(Variant, blank=True, through='ApplicationVariantLink')

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return '{}-{}'.format(self.lodgement_number, self.lodgement_sequence)

    @property
    def is_assigned(self):
        return self.assigned_officer is not None

    @property
    def is_temporary(self):
        return self.customer_status == 'temp' and self.processing_status == 'temp'

    @property
    def can_user_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.customer_status in self.CUSTOMER_EDITABLE_STATE

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the approved status.
        """
        return self.customer_status in self.CUSTOMER_VIEWABLE_STATE

    @property
    def is_senior_offer_applicable(self):
        return self.licence_type.senior_applicable and \
               self.applicant.is_senior and \
               bool(self.applicant.senior_card)


class ApplicationVariantLink(models.Model):
    application = models.ForeignKey(Application)
    variant = models.ForeignKey(Variant)
    order = models.IntegerField()


class ApplicationLogEntry(CommunicationsLogEntry):
    application = models.ForeignKey(Application)

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.application.reference
        super(ApplicationLogEntry, self).save(**kwargs)


class ApplicationRequest(models.Model):
    application = models.ForeignKey(Application)
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)


class IDRequest(ApplicationRequest):
    REASON_CHOICES = (('missing', 'There is currently no Photographic Identification uploaded'),
                      ('expired', 'The current identification has expired'),
                      ('not_recognised',
                       'The current identification is not recognised by the Department of Parks and Wildlife'),
                      ('illegible', 'The current identification image is of poor quality and cannot be made out.'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])


class ReturnsRequest(ApplicationRequest):
    REASON_CHOICES = (('outstanding', 'There are currently outstanding returns for the previous licence'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])


class AmendmentRequest(ApplicationRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
                      ('missing_information', 'There was missing information'),
                      ('other', 'Other'))
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])


class Assessment(ApplicationRequest):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'))
    assessor_group = models.ForeignKey(AssessorGroup)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_last_reminded = models.DateField(null=True, blank=True)
    conditions = models.ManyToManyField(Condition, through='AssessmentCondition')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)


class ApplicationCondition(models.Model):
    condition = models.ForeignKey(Condition)
    application = models.ForeignKey(Application)
    order = models.IntegerField()

    class Meta:
        unique_together = ('condition', 'application', 'order')


class AssessmentCondition(models.Model):
    ACCEPTANCE_STATUS_CHOICES = (('not_specified', 'Not Specified'), ('accepted', 'Accepted'), ('declined', 'Declined'))
    condition = models.ForeignKey(Condition)
    assessment = models.ForeignKey(Assessment)
    order = models.IntegerField()
    acceptance_status = models.CharField('Acceptance Status', max_length=20, choices=ACCEPTANCE_STATUS_CHOICES,
                                         default=ACCEPTANCE_STATUS_CHOICES[0][0])

    class Meta:
        unique_together = ('condition', 'assessment', 'order')


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
