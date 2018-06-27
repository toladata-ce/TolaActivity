import unicodedata
import json
import requests
import logging
from urlparse import urljoin

from workflow.models import (Country, TolaUser, TolaSites, WorkflowTeam,
                             WorkflowLevel1, Organization)
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import mail_admins, EmailMessage
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


# CREATE NEW DATA DICTIONARY OBJECT
def siloToDict(silo):
    parsed_data = {}
    key_value = 1
    for d in silo:
        label = unicodedata.normalize('NFKD', d.field.name).encode('ascii','ignore')
        value = unicodedata.normalize('NFKD', d.char_store).encode('ascii','ignore')
        row = unicodedata.normalize('NFKD', d.row_number).encode('ascii','ignore')
        parsed_data[key_value] = {label : value}

        key_value += 1

    return parsed_data


def getCountry(user):
        """
        Returns the object the view is displaying.
        """
        # get users country from django cosign module
        user_countries = TolaUser.objects.all().filter(user__id=user.id).values('countries')

        get_countries = Country.objects.all().filter(id__in=user_countries)

        return get_countries


def get_programs_user(user):
    """
    Returns a list of Programs (WorkflowLevel1) ID's where the user has access
    to.
    """
    # get user
    return WorkflowTeam.objects.filter(
        workflow_user__user=user).values_list('workflowlevel1__id', flat=True)


def emailGroup(country, group, link, subject, message, submiter=None):
        # email incident to admins in each country assoicated with the
        # projects program
        for single_country in country.all():
            country = Country.objects.all().filter(country=single_country)
            getGroupEmails = User.objects.all().filter(tola_user=group,tola_user__country=country).values_list('email', flat=True)
            email_link = link
            formatted_email = email_link
            subject = str(subject)
            message = str(message) + formatted_email

            to = [str(item) for item in getGroupEmails]
            if submiter:
                to.append(submiter)
            print to

            email = EmailMessage(subject, message, 'systems@mercycorps.org',
                    to)

            email.send()

        mail_admins(subject, message, fail_silently=False)


def get_table(url, data=None):
    """
    Get table data from a Silo.  First get the Data url from the silo details
    then get data and return it
    :param url: URL to silo meta detail info
    :param data:
    :return: json dump of table data
    """
    token = TolaSites.objects.get(site_id=1)
    if token.tola_tables_token:
        headers = {'content-type': 'application/json',
               'Authorization': 'Token ' + token.tola_tables_token }
    else:
        headers = {'content-type': 'application/json'}
        print "Token Not Found"

    response = requests.get(url,headers=headers, verify=True)
    if data:
        data = json.loads(response.content['data'])
    else:
        data = json.loads(response.content)
    return data


def group_excluded(*group_names, **url):
    # If user is in the group passed in permission denied
    def in_groups(u):
        if u.is_authenticated():
            if not bool(u.groups.filter(name__in=group_names)):
                return True
            raise PermissionDenied
        return False

    return user_passes_test(in_groups)


def group_required(*group_names, **url):
    # Requires user membership in at least one of the groups passed in.
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
            raise PermissionDenied
        return False
    return user_passes_test(in_groups)


def register_in_track(data, tolauser):
        headers = {
            'Authorization': 'Token {}'.format(settings.TOLA_TRACK_TOKEN),
        }

        url_subpath = 'accounts/register/'
        url = urljoin(settings.TOLA_TRACK_URL, url_subpath)

        response = requests.post(url, data=data, headers=headers)
        logger = logging.getLogger(__name__)
        if response.status_code == 201:
            logger.info("The TolaUser %s (id=%s) was created successfully in "
                        "Track." % (tolauser.name, tolauser.id))
        elif response.status_code in [400, 403]:
            logger.warning("The TolaUser %s (id=%s) could not be created "
                           "successfully in Track." %
                           (tolauser.name, tolauser.id))
        return response
