from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

import json
import factories
from feed.views import MilestoneViewSet
from workflow.models import WorkflowTeam, ROLE_ORGANIZATION_ADMIN, \
    ROLE_PROGRAM_TEAM, ROLE_PROGRAM_ADMIN, ROLE_VIEW_ONLY


class MilestoneListViewsTest(TestCase):
    def setUp(self):
        factories.Milestone.create_batch(2)
        self.factory = APIRequestFactory()
        self.tola_user = factories.TolaUser()

    def test_list_milestone_superuser(self):
        request = self.factory.get('/api/milestone/')
        request.user = factories.User.build(is_superuser=True,
                                            is_staff=True)
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_milestone_org_admin(self):
        request = self.factory.get('/api/milestone/')
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        request.user = self.tola_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_program_admin(self):
        request = self.factory.get('/api/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))
        request.user = self.tola_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_program_team(self):
        request = self.factory.get('/api/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))
        request.user = self.tola_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_view_only(self):
        request = self.factory.get('/api/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        request.user = self.tola_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class MilestoneViewTest(TestCase):
    def setUp(self):
        self.user = factories.User(is_superuser=True, is_staff=True)
        factory = APIRequestFactory()
        self.request = factory.post('/api/milestone/')

    def test_create_milestone(self):
        user_url = reverse('user-detail', kwargs={'pk': self.user.id},
                           request=self.request)

        data = {'name': 'Project Implementation'}
        self.request = APIRequestFactory().post('/api/milestone/', data)
        self.request.user = self.user
        view = MilestoneViewSet.as_view({'post': 'create'})
        response = view(self.request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Project Implementation')
        self.assertEqual(response.data['created_by'], user_url)

    def test_create_milestone_json(self):
        user_url = reverse('user-detail', kwargs={'pk': self.user.id},
                           request=self.request)

        data = {'name': 'Project Implementation'}
        self.request = APIRequestFactory().post(
            '/api/milestone/', json.dumps(data),
            content_type='application/json')
        self.request.user = self.user
        view = MilestoneViewSet.as_view({'post': 'create'})
        response = view(self.request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Project Implementation')
        self.assertEqual(response.data['created_by'], user_url)
