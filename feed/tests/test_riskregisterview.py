from django.test import TestCase
from rest_framework.test import APIRequestFactory

import factories
from feed.views import RiskRegisterViewSet
from workflow.models import RiskRegister, Organization, TolaUser, WorkflowLevel1, WorkflowLevel2


class RiskRegisterViewTest(TestCase):
    def setUp(self):
        wflvl1 = WorkflowLevel1.objects.create(name='WorkflowLevel1')
        wflvl2 = WorkflowLevel2.objects.create(name='WorkflowLevel2', workflowlevel1=wflvl1)
        RiskRegister.objects.bulk_create([
            RiskRegister(name='RiskRegister_0', workflowlevel2=wflvl2),
            RiskRegister(name='RiskRegister_1', workflowlevel2=wflvl2),
        ])

        factory = APIRequestFactory()
        self.request = factory.get('/api/riskregister/')

    def test_list_riskregister_superuser(self):
        self.request.user = factories.User.build(is_superuser=True, is_staff=True)
        view = RiskRegisterViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_riskregister_normaluser(self):
        user = factories.User()
        organization = Organization.objects.create(name="TestOrg")
        TolaUser.objects.create(user=user, organization=organization)

        self.request.user = user
        view = RiskRegisterViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_riskregister_one_result(self):
        user = factories.User()
        organization = Organization.objects.create(name="TestOrg")
        TolaUser.objects.create(user=user, organization=organization)

        wflvl1 = WorkflowLevel1.objects.create(name='WorkflowLevel1', organization=organization)
        wflvl2 = WorkflowLevel2.objects.create(name='WorkflowLevel2', workflowlevel1=wflvl1)
        RiskRegister.objects.create(name='RiskRegister_0', workflowlevel2=wflvl2)

        self.request.user = user
        view = RiskRegisterViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
