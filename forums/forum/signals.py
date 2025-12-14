from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post, SurveyVote, Notification


@receiver(post_save, sender=Post)
def create_reply_notification(sender, instance, created, **kwargs):
    if not created:
        return
    thread = instance.thread
    if not thread:
        return
    if instance.author and thread.author and instance.author != thread.author:
        Notification.objects.create(
            recipient=thread.author,
            actor=instance.author,
            notif_type='reply',
            message=f"{instance.author.username} a répondu à ton sujet '{thread.title}'",
            thread=thread,
            post=instance,
        )


@receiver(post_save, sender=SurveyVote)
def create_vote_notification(sender, instance, created, **kwargs):
    survey = instance.survey
    if not survey:
        return
    if instance.user and survey.author and instance.user != survey.author:
        verb = f"{instance.user.username} a voté pour '{instance.option.text}' sur ton sondage '{survey.title}'"
        Notification.objects.create(
            recipient=survey.author,
            actor=instance.user,
            notif_type='vote',
            message=verb,
            survey=survey,
            option=instance.option,
        )
