from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

import json
import factories
from feed.views import WorkflowTeamViewSet
from workflow.models import (WorkflowTeam, ROLE_ORGANIZATION_ADMIN,
                             ROLE_PROGRAM_ADMIN, ROLE_PROGRAM_TEAM,
                             ROLE_VIEW_ONLY)


class WorkflowTeamListViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.TolaUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.TolaUser(
            user=user_ringo, organization=factories.Organization())
        self.wflvl1 = factories.WorkflowLevel1(
            organization=tola_user_ringo.organization)
        factories.WorkflowTeam(workflow_user=tola_user_ringo,
                               workflowlevel1=self.wflvl1,
                               partner_org=self.wflvl1.organization,
                               role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_list_workflowteam_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_superuser_and_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)

        # Create a workflow team having a diff partner org
        factories.WorkflowTeam(workflow_user=self.tola_user,
                               workflowlevel1=wflvl1)

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_org_admin_diff_user_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        # Create a user belonging to other Project in other Org
        another_org = factories.Organization(name='Another Org')
        user_george = factories.User(first_name='George', last_name='Harrison')
        tola_user_george = factories.TolaUser(
            user=user_george, organization=another_org)
        wflvl1_other = factories.WorkflowLevel1(organization=another_org)
        factories.WorkflowTeam(workflow_user=tola_user_george,
                               workflowlevel1=wflvl1_other)

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_workflowteam_org_admin_diff_user_same_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        # Create a user belonging to other Project in other Org
        user_george = factories.User(first_name='George', last_name='Harrison')
        tola_user_george = factories.TolaUser(
            user=user_george, organization=self.tola_user.organization)
        wflvl1_other = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        factories.WorkflowTeam(workflow_user=tola_user_george,
                               workflowlevel1=wflvl1_other)

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_org_admin_diff_partner_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)

        # Create a workflow team having a diff partner org
        another_org = factories.Organization(name='Another Org')
        factories.WorkflowTeam(workflow_user=self.tola_user,
                               workflowlevel1=wflvl1,
                               partner_org=another_org)

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_program_admin(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_program_team(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_view_only(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))

        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_normaluser(self):
        request_get = self.factory.get('/api/workflowteam/')
        request_get.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class WorkflowTeamCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.TolaUser()
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)

    def test_create_workflowteam_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        wflvl1_url = reverse('workflowlevel1-detail',
                             kwargs={'pk': self.wflvl1.id})
        tolauser_url = reverse('tolauser-detail',
                               kwargs={'pk': self.tola_user.id})
        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        role_url = reverse('group-detail', kwargs={'pk': role.id})
        data = {
            'role': role_url,
            'workflow_user': tolauser_url,
            'workflowlevel1': wflvl1_url,
        }

        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.tola_user,
            role=role,
        )

    def test_create_workflowteam_org_admin(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_ORGANIZATION_ADMIN))

        wflvl1_url = reverse('workflowlevel1-detail',
                             kwargs={'pk': self.wflvl1.id})
        user_george = factories.User(first_name='George', last_name='Harrison')
        tola_user_george = factories.TolaUser(
            user=user_george, organization=factories.Organization())
        tolauser_url = reverse('tolauser-detail',
                               kwargs={'pk': tola_user_george.id})
        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        role_url = reverse('group-detail', kwargs={'pk': role.id})
        data = {
            'role': role_url,
            'workflow_user': tolauser_url,
            'workflowlevel1': wflvl1_url,
        }

        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=tola_user_george,
            role=role,
        )

    def test_create_workflowteam_program_admin(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        wflvl1_url = reverse('workflowlevel1-detail',
                             kwargs={'pk': self.wflvl1.id})
        tolauser_url = reverse('tolauser-detail',
                               kwargs={'pk': self.tola_user.id})
        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        role_url = reverse('group-detail', kwargs={'pk': role.id})
        data = {
            'role': role_url,
            'workflow_user': tolauser_url,
            'workflowlevel1': wflvl1_url,
        }

        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.tola_user,
            role=role,
        )

    def test_create_workflowteam_program_admin_json(self):
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        wflvl1_url = reverse('workflowlevel1-detail',
                             kwargs={'pk': self.wflvl1.id})
        tolauser_url = reverse('tolauser-detail',
                               kwargs={'pk': self.tola_user.id})
        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        role_url = reverse('group-detail', kwargs={'pk': role.id})
        data = {
            'role': role_url,
            'workflow_user': tolauser_url,
            'workflowlevel1': wflvl1_url,
        }

        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.tola_user,
            role=role,
        )

    def test_create_workflowteam_other_user(self):
        role_without_benefits = ROLE_PROGRAM_TEAM
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=role_without_benefits))

        wflvl1_url = reverse('workflowlevel1-detail',
                             kwargs={'pk': self.wflvl1.id})
        tolauser_url = reverse('tolauser-detail',
                               kwargs={'pk': self.tola_user.id})
        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        role_url = reverse('group-detail', kwargs={'pk': role.id})
        data = {
            'role': role_url,
            'workflow_user': tolauser_url,
            'workflowlevel1': wflvl1_url,
        }

        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 403)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, workflowlevel1=self.wflvl1,
            workflow_user=self.tola_user,
            role=role,
        )


class WorkflowTeamUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.TolaUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.TolaUser(
            user=user_ringo, organization=self.tola_user.organization)
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        self.workflowteam = factories.WorkflowTeam(
            workflow_user=tola_user_ringo,
            workflowlevel1=self.wflvl1,
            partner_org=self.wflvl1.organization,
            role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_update_unexisting_workflowteam(self):
        data = {'salary': '100'}
        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowteam_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        data = {'salary': '100'}
        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        salary_updated = WorkflowTeam.objects.\
            values_list('salary', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(salary_updated, '100')

    def test_update_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        data = {'salary': '100'}
        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        salary_updated = WorkflowTeam.objects.\
            values_list('salary', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(salary_updated, '100')

    def test_update_workflowteam_program_admin(self):
        factories.WorkflowTeam(
            workflow_user=self.tola_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        data = {'salary': '100'}
        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        salary_updated = WorkflowTeam.objects.\
            values_list('salary', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(salary_updated, '100')

    def test_update_workflowteam_program_admin_json(self):
        factories.WorkflowTeam(
            workflow_user=self.tola_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        data = {'salary': '100'}
        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        salary_updated = WorkflowTeam.objects.\
            values_list('salary', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(salary_updated, '100')

    def test_update_workflowteam_other_user(self):
        role_without_benefits = ROLE_PROGRAM_TEAM
        self.workflowteam.role = factories.Group(name=role_without_benefits)
        self.workflowteam.save()

        data = {'salary': '100'}
        request = self.factory.post(None, data)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 403)


class WorkflowTeamDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.TolaUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.TolaUser(
            user=user_ringo, organization=self.tola_user.organization)
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        self.workflowteam = factories.WorkflowTeam(
            workflow_user=tola_user_ringo,
            workflowlevel1=self.wflvl1,
            partner_org=self.wflvl1.organization,
            role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_delete_workflowteam_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        request = self.factory.delete(None)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        request = self.factory.delete(None)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_program_admin(self):
        factories.WorkflowTeam(
            workflow_user=self.tola_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        request = self.factory.delete(None)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_role_without_benefit(self):
        factories.WorkflowTeam(
            workflow_user=self.tola_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))

        request = self.factory.delete(None)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowTeam.objects.get(pk=self.workflowteam.pk)


class WorkflowTeamFilterViewTest(TestCase):
    def setUp(self):
        self.tola_user = factories.TolaUser()
        self.factory = APIRequestFactory()

    def test_filter_workflowteam_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        another_org = factories.Organization(name='Another Org')
        wkflvl1_1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(
            organization=another_org)
        workflowteam1 = factories.WorkflowTeam(workflow_user=self.tola_user,
                                               salary=1111,
                                               workflowlevel1=wkflvl1_1)
        factories.WorkflowTeam(workflow_user=self.tola_user,
                               salary=2222,
                               workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '/api/workflowteam/?workflowlevel1__organization__id=%s' %
            self.tola_user.organization.pk)
        request.user = self.tola_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['salary'], str(workflowteam1.salary))
