from ledger.settings_base import *

ROOT_URLCONF = 'wildlifelicensing.urls'

INSTALLED_APPS += [
    'bootstrap3',
    'wildlifelicensing.apps.dashboard',
    'wildlifelicensing.apps.main',
    'wildlifelicensing.apps.applications',
    'wildlifelicensing.apps.emails',
    'wildlifelicensing.apps.returns',
    'wildlifelicensing.apps.customer_management',
    'wildlifelicensing.apps.reports',
    'wildlifelicensing.apps.payments'
]

WSGI_APPLICATION = 'wildlifelicensing.wsgi.application'

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'wildlifelicensing', 'templates'))

BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}


STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')))

CRON_CLASSES = [
    'wildlifelicensing.apps.applications.cron.CheckLicenceRenewalsCronJob',
    'wildlifelicensing.apps.applications.cron.AssessmentRemindersCronJob',
    'wildlifelicensing.apps.returns.cron.CheckOverdueReturnsCronJob',
]

WILDLIFELICENSING_EMAIL_CATCHALL = env('WILDLIFELICENSING_EMAIL_CATCHALL', 'wildlifelicensing@dpaw.wa.gov.au')

HERBIE_SPECIES_WFS_URL = env('HERBIE_SPECIES_WFS_URL',
                             'https://kmi.dpaw.wa.gov.au/geoserver/ows?service=wfs&version=1.1.0&'
                             'request=GetFeature&typeNames=public:herbie_hbvspecies_public&outputFormat=application/json')

WL_PAYMENT_SYSTEM_ID = env('WL_PAYMENT_SYSTEM_ID', 'S369')
WL_SENIOR_VOUCHER_CODE = env('WL_SENIOR_VOUCHER_CODE', 'WL_SENIOR_VOUCHER')
