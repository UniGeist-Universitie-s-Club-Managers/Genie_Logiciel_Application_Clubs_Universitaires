from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from forums.forum.models import Club, Forum, Thread, Post, Survey, SurveyOption


User = get_user_model()


class PrivateForumPermissionsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'pass')
        self.responsible = User.objects.create_user('responsible', 'resp@example.com', 'pass')
        self.member = User.objects.create_user('member', 'member@example.com', 'pass')
        self.other = User.objects.create_user('other', 'other@example.com', 'pass')

        self.club = Club.objects.create(name='Club A', description='Desc', responsible=self.responsible)
        self.club.members.add(self.member)

        self.forum = Forum.objects.create(
            title='Forum privé',
            description='desc',
            visibility='private',
            club=self.club,
            created_by=self.responsible,
        )

        self.thread = Thread.objects.create(
            forum=self.forum,
            title='Sujet membre',
            body='Contenu',
            author=self.member,
        )
        self.post = Post.objects.create(thread=self.thread, content='Réponse', author=self.member)

        self.survey = Survey.objects.create(
            forum=self.forum,
            title='Sondage privé',
            description='Desc',
            author=self.responsible,
        )
        self.option = SurveyOption.objects.create(survey=self.survey, text='Option 1')

    def test_member_can_access_private_forum(self):
        self.client.login(username='member', password='pass')
        response = self.client.get(reverse('forum:forum-detail', args=[self.forum.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_member_receives_403_for_forum(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('forum:forum-detail', args=[self.forum.pk]))
        self.assertEqual(response.status_code, 403)

    def test_non_member_cannot_create_thread(self):
        self.client.login(username='other', password='pass')
        response = self.client.post(
            reverse('forum:thread-create'),
            {'forum': self.forum.pk, 'title': 'X', 'body': 'Y'},
        )
        self.assertEqual(response.status_code, 403)

    def test_non_member_cannot_reply(self):
        self.client.login(username='other', password='pass')
        response = self.client.post(
            reverse('forum:thread-detail', args=[self.thread.pk]),
            {'content': 'Réponse non membre'},
        )
        self.assertEqual(response.status_code, 403)

    def test_responsible_and_admin_can_manage_forum(self):
        self.client.login(username='responsible', password='pass')
        response = self.client.get(reverse('forum:forum-update', args=[self.forum.pk]))
        self.assertEqual(response.status_code, 200)

        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('forum:forum-update', args=[self.forum.pk]))
        self.assertEqual(response.status_code, 200)

    def test_private_survey_hidden_from_non_member(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(reverse('forum:survey-detail', args=[self.survey.pk]))
        self.assertEqual(response.status_code, 403)

    def test_member_can_view_and_vote_survey(self):
        self.assertTrue(self.survey.can_vote(self.member))
        self.assertFalse(self.survey.can_vote(self.other))

