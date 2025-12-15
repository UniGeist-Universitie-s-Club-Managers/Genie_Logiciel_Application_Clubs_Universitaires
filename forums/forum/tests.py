from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Forum, Thread, Post
from .models import Notification, Survey, SurveyVote

User = get_user_model()


class PostReplyTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='tester', password='pass')
		self.forum = Forum.objects.create(title='F', description='D', created_by=self.user)
		self.thread = Thread.objects.create(forum=self.forum, title='T', body='B', author=self.user)

	def test_post_reply(self):
		self.client.login(username='tester', password='pass')
		url = reverse('forum:thread-detail', kwargs={'pk': self.thread.pk})
		response = self.client.post(url, {'content': 'Ma réponse'})
		# should redirect back to thread detail on success
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Post.objects.filter(thread=self.thread).count(), 1)

	def test_post_reply_with_thread_field_in_post(self):
		# Simulate a client sending an extra 'thread' field in POST data
		self.client.login(username='tester', password='pass')
		url = reverse('forum:thread-detail', kwargs={'pk': self.thread.pk})
		response = self.client.post(url, {'content': 'Ma réponse', 'thread': '3'})
		# should still work and create a post for the current thread
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Post.objects.filter(thread=self.thread).count(), 1)

	def test_vote_and_change_vote(self):
		# create a survey and options
		survey = self.forum.surveys.create(title='S', author=self.user)
		o1 = survey.options.create(text='A')
		o2 = survey.options.create(text='B')

		self.client.login(username='tester', password='pass')
		vote_url = reverse('forum:survey-vote', kwargs={'pk': survey.pk})
		# vote for option A
		r = self.client.post(vote_url, {'option': o1.pk})
		self.assertEqual(r.status_code, 302)
		self.assertEqual(survey.votes.filter(user=self.user).count(), 1)

		# change vote to B
		r = self.client.post(vote_url, {'option': o2.pk})
		self.assertEqual(r.status_code, 302)
		self.assertEqual(survey.votes.get(user=self.user).option, o2)

	def test_add_option_permissions(self):
		survey = self.forum.surveys.create(title='S2', author=self.user)
		add_url = reverse('forum:survey-add-option', kwargs={'pk': survey.pk})

		# anonymous cannot add
		r = self.client.post(add_url, {'text': 'X'})
		self.assertEqual(r.status_code, 302)

		# logged in author can add
		self.client.login(username='tester', password='pass')
		r = self.client.post(add_url, {'text': 'Opt1'})
		self.assertEqual(r.status_code, 302)
		self.assertTrue(survey.options.filter(text='Opt1').exists())

	def test_club_responsible_can_add_option(self):
		# create a club and forum with different author and a responsible
		other = User.objects.create_user(username='other', password='p')
		club = self.user.clubs.create(name='C')
		club.responsible = other
		club.save()
		f = Forum.objects.create(title='F2', description='D2', created_by=self.user, club=club, visibility='private')
		survey = Survey.objects.create(title='S3', forum=f, author=self.user)

		self.client.login(username='other', password='p')
		add_url = reverse('forum:survey-add-option', kwargs={'pk': survey.pk})
		r = self.client.post(add_url, {'text': 'ClubOpt'})
		self.assertEqual(r.status_code, 302)
		self.assertTrue(survey.options.filter(text='ClubOpt').exists())

	def test_view_voters_list(self):
		survey = self.forum.surveys.create(title='S4', author=self.user)
		o = survey.options.create(text='O1')
		other = User.objects.create_user(username='voter', password='p2')
		SurveyVote.objects.create(survey=survey, option=o, user=self.user)
		SurveyVote.objects.create(survey=survey, option=o, user=other)

		self.client.login(username='tester', password='pass')
		url = reverse('forum:survey-option-voters', kwargs={'survey_pk': survey.pk, 'option_pk': o.pk})
		r = self.client.get(url)
		self.assertEqual(r.status_code, 200)
		self.assertContains(r, 'tester')
		self.assertContains(r, 'voter')

	def test_notifications_on_reply_and_vote(self):
		# reply notification
		other = User.objects.create_user(username='other2', password='p2')
		self.client.login(username='other2', password='p2')
		url = reverse('forum:thread-detail', kwargs={'pk': self.thread.pk})
		r = self.client.post(url, {'content': 'Hello owner'})
		self.assertEqual(r.status_code, 302)
		# owner should have a notification
		notifs = Notification.objects.filter(recipient=self.user)
		self.assertTrue(notifs.filter(notif_type='reply').exists())

		# vote notification
		survey = self.forum.surveys.create(title='S5', author=self.user)
		o = survey.options.create(text='opt')
		# other votes
		self.client.login(username='other2', password='p2')
		vote_url = reverse('forum:survey-vote', kwargs={'pk': survey.pk})
		r = self.client.post(vote_url, {'option': o.pk})
		self.assertEqual(r.status_code, 302)
		self.assertTrue(Notification.objects.filter(recipient=self.user, notif_type='vote').exists())
