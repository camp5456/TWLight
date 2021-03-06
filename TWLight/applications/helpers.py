from django import forms
from django.utils.translation import ugettext as _

from TWLight.resources.models import Partner, Stream

"""
Lists and characterizes the types of information that partners can require as
part of access grants. See full comment at end of file.
"""

"""
Harvestable from user profile:
    Username (all partnerships)
    Email (all partnerships)
    Projects user is active on (all partnerships)
    Call for volunteers (as needed - checkbox "I'm interested")

        Perhaps invite them to review/update their user profile as part of
        application process.

        Make sure to communicate to them what info will be shared with
        coordinators and what to expect...

Required/nonharvestable:

Optional/universal:
    Real name (many partners)
    Country of residence (Pelican, Numerique)
    Occupation (Elsevier)
    Affiliation (Elsevier)

Optional/unique:
    Questions/comments/concerns (free-text, all partnerships)
    Title requested (McFarland, Pelican)
    Stream requested (OUP, T&F, Elsevier)
    Agreement with Terms of Use (RSUK)
"""

# ~~~~~ Named constants ~~~~~ #
REAL_NAME = 'real_name'
COUNTRY_OF_RESIDENCE = 'country_of_residence'
OCCUPATION = 'occupation'
AFFILIATION = 'affiliation'
PARTNER = 'partner'
RATIONALE = 'rationale'
SPECIFIC_STREAM = 'specific_stream'
SPECIFIC_TITLE = 'specific_title'
COMMENTS = 'comments'
AGREEMENT_WITH_TERMS_OF_USE = 'agreement_with_terms_of_use'


# ~~~~ Basic field names ~~~~ #
USER_FORM_FIELDS = [REAL_NAME, COUNTRY_OF_RESIDENCE, OCCUPATION,
                    AFFILIATION]

# These fields are displayed for all partners.
PARTNER_FORM_BASE_FIELDS = [RATIONALE, COMMENTS]

# These fields are displayed only when a specific partner requires that
# information.
PARTNER_FORM_OPTIONAL_FIELDS = [SPECIFIC_STREAM, SPECIFIC_TITLE,
                                AGREEMENT_WITH_TERMS_OF_USE]


# ~~~~ Field information ~~~~ #
FIELD_TYPES = {
    REAL_NAME: forms.CharField(max_length=128),
    COUNTRY_OF_RESIDENCE: forms.CharField(max_length=128),
    OCCUPATION: forms.CharField(max_length=128),
    AFFILIATION: forms.CharField(max_length=128),
    PARTNER: forms.ModelChoiceField(
        queryset=Partner.objects.all(),
        widget=forms.HiddenInput),
    RATIONALE: forms.CharField(widget=forms.Textarea),
    SPECIFIC_STREAM: forms.ModelChoiceField(queryset=Stream.objects.all()),
    SPECIFIC_TITLE: forms.CharField(max_length=128),
    COMMENTS: forms.CharField(widget=forms.Textarea, required=False),
    AGREEMENT_WITH_TERMS_OF_USE: forms.BooleanField(required=False),
}

FIELD_LABELS = {
    REAL_NAME: _('Your real name'),
    COUNTRY_OF_RESIDENCE: _('Your country of residence'),
    OCCUPATION: _('Your occupation'),
    AFFILIATION: _('Your institutional affiliation'),
    PARTNER: _('Partner name'),
    RATIONALE: _('Why do you want access to this resource?'),
    SPECIFIC_STREAM: _('Which collection do you want?'),
    SPECIFIC_TITLE: _('Which book do you want?'),
    COMMENTS: _('Anything else you want to say'),
    AGREEMENT_WITH_TERMS_OF_USE: _("You must agree with the partner's terms of use"),
}


def get_output_for_application(app):
    """
    This collates the data that we need to send to publishers for a given
    application. Since different publishers require different data and we don't
    want to share personal data where not required, we construct this function
    to fetch only the required data rather than displaying all of Application
    plus Editor in the front end.
    """
    output = {}
    output[_('Email')] = app.editor.user.email

    for field in PARTNER_FORM_OPTIONAL_FIELDS:
        if getattr(app.partner, field): # Will be True if required by Partner.
            output[field] = getattr(app, field)

    for field in USER_FORM_FIELDS:
        if getattr(app.partner, field): # Will be True if required by Partner.
            output[field] = getattr(app.editor, field)

    return output


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

"""
Information comes in three types:
1) Information required for all access grants. (Example: wikipedia username)
2) Information that only some partners require, but which will be the same for
   all partners in any given application. (Example: country of residence)
3) Information that only some partners require, and that may differ for
   different partners. (Example: rationale for resource request)

These facts about required/optional status are used to generate application
forms. In particular, we can generate application forms which impose the
smallest possible data entry burden on users by:
* omitting optional fields if they aren't required by any of the requested
  partners;
* asking for optional information only once per application, rather than once
  per partner, if it will be the same for all partners.

Facts related to this file are hardcoded in three other places in the database:

1) In TWLight.resources.models.Partner, which tracks whether a given partner
   requires the optional information;
2) In TWLight.applications.forms.Application, which has fields for all
   possible partner-specific information (though any given application instance
   may leave optional fields blank).
3) In TWLight.users.models.Editor, which records user data.

Why this hardcoding? Well, having defined database models lets us take advantage
of an awful lot of Django machinery. Also, dynamically generating everything on
the fly might be slow and lead to hard-to-read code.

applications.tests checks to make sure that these three sources are in agreement
about the optional data fields available: both their names and their types. It
also checks that the constructed application form fields match those types.
"""
