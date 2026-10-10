"""
Views for the messages app of Speedy Core: chat list, chat details, polling messages, sending messages and marking chats as read.
"""
from datetime import datetime, timezone

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
from django.contrib import messages
from django.utils.translation import pgettext_lazy
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from speedy.core.base.utils import normalize_username
from speedy.core.blocks.models import Block
from .forms import MessageForm
from .models import Chat


class UserChatsMixin(UserMixin, PermissionRequiredMixin):
    """
    Mixin for views that need the list of chats belonging to the profile's user, restricted by a view_chats permission check.

    Methods:
        dispatch(self, request, *args, **kwargs): Dispatches the request, converting a raised PermissionDenied into the no-permission response.
        get_chat_queryset(self): Returns the queryset of the user's chats with their participants and last message prefetched.
        has_permission(self): Returns whether the requesting user has permission to view the profile's chats.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request, catching a PermissionDenied raised during dispatch and converting it into the no-permission response.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        try:
            return super().dispatch(request=request, *args, **kwargs)
        except PermissionDenied:
            return self.handle_no_permission()

    def get_chat_queryset(self):
        """
        Returns the queryset of chats the profile's user participates in, with participants and last message prefetched.

        :return: The queryset of Chat instances.
        :rtype: django.db.models.QuerySet
        """
        return Chat.objects.chats(entity=self.get_user()).prefetch_related('ent1__user', 'ent2__user', 'last_message')

    def has_permission(self):
        """
        :return: True if the requesting user is allowed to view the profile's list of chats.
        :rtype: bool
        """
        return self.request.user.has_perm(perm='messages.view_chats', obj=self.user)


class UserSingleChatMixin(UserChatsMixin):
    """
    Mixin for views operating on a single chat identified in the URL, restricted by a read_chat permission check.

    Methods:
        dispatch(self, request, *args, **kwargs): Resolves the chat and dispatches the request, converting a raised PermissionDenied into the no-permission response.
        get_chat(self): Returns the single chat matching the chat_slug URL kwarg, or raises Http404.
        get_messages_queryset(self): Returns the queryset of messages in the resolved chat.
        has_permission(self): Returns whether the requesting user has permission to view the chats and read this specific chat.
        get_context_data(self, **kwargs): Adds the resolved chat to the template context.
        handle_no_permission(self): Handles a permission failure, redirecting to the other user with an error message when appropriate.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Resolves the requested chat and dispatches the request, catching a PermissionDenied raised during dispatch and converting it into the no-permission response.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        try:
            self.chat = self.get_chat()
            return super().dispatch(request=request, *args, **kwargs)
        except PermissionDenied:
            return self.handle_no_permission()

    def get_chat(self):
        """
        Returns the single chat matching the chat_slug URL kwarg, either by chat id or by the slug of the other participant.

        :return: The resolved chat.
        :rtype: speedy.core.messages.models.Chat
        :raises django.http.Http404: If no single chat matches the given slug.
        """
        slug = self.kwargs['chat_slug']
        user = self.get_user()
        q_id = Q(id=slug)
        q_slug_1 = Q(ent1__slug=slug, ent2_id=user.id)
        q_slug_2 = Q(ent1_id=user.id, ent2__slug=slug)
        chats = self.get_chat_queryset().filter(q_id | q_slug_1 | q_slug_2)
        if (len(chats) == 1):
            return chats[0]
        else:
            raise Http404()

    def get_messages_queryset(self):
        """
        :return: The queryset of messages belonging to the resolved chat.
        :rtype: django.db.models.QuerySet
        """
        return self.get_chat().messages_queryset

    def has_permission(self):
        """
        :return: True if the requesting user has both permission to view the profile's chats and permission to read this specific chat.
        :rtype: bool
        """
        return ((super().has_permission()) and (self.request.user.has_perm(perm='messages.read_chat', obj=self.chat)))

    def get_context_data(self, **kwargs):
        """
        Adds the resolved chat to the template context.

        :param kwargs: Additional keyword arguments passed to the parent implementation.
        :return: The context data dictionary, including the chat.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'chat': self.chat,
        })
        return cd

    def handle_no_permission(self):
        """
        Handles a permission failure. If the request is from an authenticated user who isn't the profile's user or blocked from/by them, shows an error message about the site's anti-spam message limits and redirects to the profile's user; otherwise, falls back to the default no-permission handling.

        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        if (self.request.user.is_authenticated):
            try:
                if (getattr(self, "user", None) is None):
                    self.user = self.get_user()
                if (self.request.user == self.user) or (Block.objects.there_is_block(entity_1=self.request.user, entity_2=self.user)):
                    pass
                else:
                    messages.error(request=self.request, message=pgettext_lazy(context=self.request.user.get_gender(), message='Due to the abuse of the site to send spam messages, we had to limit the number of messages that can be sent to other members of the site in one day. Please try again tomorrow. Please note that you are not allowed to use Speedy Net to send spam messages, or messages with the same content to a large number of people.'))
                    return redirect(to=self.user)
            except PermissionDenied:
                pass
        return super().handle_no_permission()


class ChatListView(UserChatsMixin, generic.ListView):
    """
    Displays the paginated list of chats belonging to the profile's user.

    Methods:
        get_queryset(self): Returns the profile's chat queryset.
    """
    template_name = 'messages/chat_list.html'
    page_size = 24
    paginate_by = page_size

    def get_queryset(self):
        """
        :return: The queryset of the profile's chats.
        :rtype: django.db.models.QuerySet
        """
        return self.get_chat_queryset()


class ChatDetailView(UserSingleChatMixin, generic.ListView):
    """
    Displays the paginated message history of a single chat, or a message compose form if no chat exists yet between the current user and the profile's user.

    Methods:
        dispatch(self, request, *args, **kwargs): Redirects to the canonical slug, or switches to compose mode, before dispatching normally.
        get_form(self): Returns the message form bound to the resolved chat or the target user.
        get_queryset(self): Returns the chat's messages, or an empty list if there is no existing chat.
        get_template_names(self): Returns the chat detail template, or the message compose form template if there is no existing chat.
        get_context_data(self, **kwargs): Adds the message form to the template context.
    """
    permission_required = 'messages.read_chat'
    template_name = 'messages/chat_detail.html'
    page_size = 24
    paginate_by = page_size

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request. If the user isn't authenticated, denies access. If the URL slug for the visited user isn't canonical, redirects to the canonical slug. If there's no existing chat with the visited user, switches to compose mode (requiring send_message permission) instead of the usual read_chat permission flow.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :rtype: django.http.HttpResponse
        """
        if (not (request.user.is_authenticated)):
            return self.handle_no_permission()
        visited_user_slug = self.kwargs['chat_slug']
        visited_user = self.get_user_queryset().filter(Q(username=normalize_username(username=visited_user_slug)) | Q(id=visited_user_slug)).first()
        if ((visited_user) and (visited_user.slug != visited_user_slug)):
            return redirect(to=reverse(viewname='messages:chat', kwargs={'chat_slug': visited_user.slug}))
        if ((visited_user) and (visited_user != request.user) and (not (Chat.objects.chat_with(ent1=self.request.user, ent2=visited_user, create=False)))):
            self.permission_required = 'messages.send_message'
            self.user = visited_user
            self.chat = None
            if (not (self.request.user.has_perm(perm='messages.send_message', obj=visited_user))):
                return self.handle_no_permission()
            return self.get(request=request, *args, **kwargs)
        return super().dispatch(request=request, *args, **kwargs)

    def get_form(self):
        """
        :return: A MessageForm bound either to the resolved chat, or to the current user and the profile's user when there is no existing chat yet.
        :rtype: speedy.core.messages.forms.MessageForm
        """
        if (self.chat):
            return MessageForm(**{
                'from_entity': self.request.user,
                'chat': self.chat,
            })
        else:
            return MessageForm(**{
                'from_entity': self.request.user,
                'to_entity': self.user,
            })

    def get_queryset(self):
        """
        :return: The chat's messages queryset, or an empty list if there is no existing chat yet.
        :rtype: django.db.models.QuerySet or list
        """
        if (self.chat):
            return self.get_messages_queryset()
        else:
            return []

    def get_template_names(self):
        """
        :return: The chat detail template name if an existing chat is being displayed, or the message compose form template name otherwise.
        :rtype: str
        """
        if (self.chat):
            return 'messages/chat_detail.html'
        else:
            return 'messages/message_form.html'

    def get_context_data(self, **kwargs):
        """
        Adds the message compose form to the template context.

        :param kwargs: Additional keyword arguments passed to the parent implementation.
        :return: The context data dictionary, including the form.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'form': self.get_form(),
        })
        return cd


class ChatPollMessagesView(UserSingleChatMixin, generic.ListView):
    """
    Returns, via AJAX polling, the messages of a chat created after a given timestamp.

    Methods:
        get_queryset(self): Returns the chat's messages created after the 'since' query parameter's timestamp.
        get_context_data(self, **kwargs): Marks the context as an AJAX view.
    """
    template_name = 'messages/message_list_poll.html'
    raise_exception = True

    def get_queryset(self):
        """
        :return: The chat's messages created strictly after the timestamp given in the 'since' query parameter (defaulting to 0).
        :rtype: django.db.models.QuerySet
        """
        since = float(self.request.GET.get('since', 0))
        since += 0.0001
        return self.get_messages_queryset().filter(date_created__gt=datetime.fromtimestamp(timestamp=since, tz=timezone.utc))

    def get_context_data(self, **kwargs):
        """
        Marks the context as an AJAX view.

        :param kwargs: Additional keyword arguments passed to the parent implementation.
        :return: The context data dictionary, including the ajax_view flag.
        :rtype: dict
        """
        cd = super().get_context_data(**kwargs)
        cd.update({
            'ajax_view': True,
        })
        return cd


class SendMessageToChatView(UserSingleChatMixin, generic.CreateView):
    """
    Handles posting a new message to an existing chat.

    Methods:
        get_form_kwargs(self): Adds the sender entity and target chat to the form kwargs.
        get(self, request, *args, **kwargs): Redirects GET requests to the chat page, since messages are only sent via POST.
        get_success_url(self): Returns the URL of the chat after a message is sent.
        has_permission(self): Returns whether the requesting user has permission to send a message to the chat.
    """
    permission_required = 'messages.send_message'
    template_name = 'messages/chat_detail.html'
    form_class = MessageForm
    raise_exception = True

    def get_form_kwargs(self):
        """
        :return: The form kwargs, including the sender entity and the target chat.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'from_entity': self.user,
            'chat': self.chat,
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        """
        Redirects GET requests to the chat page, since this view only supports sending messages via POST.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the chat page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.get_success_url())

    def get_success_url(self):
        """
        :return: The URL of the chat page, using the slug relative to the profile's user.
        :rtype: str
        """
        return reverse(viewname='messages:chat', kwargs={'chat_slug': self.chat.get_slug(current_user=self.user)})

    def has_permission(self):
        """
        :return: For a private (two-participant) chat, True if the requesting user has permission to send a message to the other participant; for a group chat, the mixin's default permission check.
        :rtype: bool
        """
        if (self.chat.participants_count != 2):
            return super().has_permission()
        return self.user.has_perm(perm='messages.send_message', obj=self.chat.get_other_participants(entity=self.user)[0])


class SendMessageToUserView(UserMixin, PermissionRequiredMixin, generic.CreateView):
    """
    Handles sending the first message of a new private chat to a user, either showing a compose form or redirecting to an already-existing chat.

    Methods:
        get(self, request, *args, **kwargs): Redirects to an existing chat with the profile's user, if there is one, otherwise shows the compose form.
        get_form_kwargs(self): Adds the sender entity and target entity to the form kwargs.
        get_success_url(self): Returns the URL of the newly created chat.
    """
    permission_required = 'messages.send_message'
    template_name = 'messages/message_form.html'
    form_class = MessageForm

    def get(self, request, *args, **kwargs):
        """
        Redirects to the existing private chat with the profile's user, if there is one, otherwise shows the compose form.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect to the existing chat, or the compose form response.
        :rtype: django.http.HttpResponse
        """
        existing_chat = Chat.objects.chat_with(ent1=self.request.user, ent2=self.user, create=False)
        if (existing_chat is not None):
            return redirect(to='messages:chat', **{'chat_slug': existing_chat.get_slug(current_user=self.request.user)})
        return super().get(request=request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        :return: The form kwargs, including the sender entity and the target entity.
        :rtype: dict
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'from_entity': self.request.user,
            'to_entity': self.user,
        })
        return kwargs

    def get_success_url(self):
        """
        :return: The URL of the chat that was created by submitting the message form.
        :rtype: str
        """
        return reverse(viewname='messages:chat', kwargs={'chat_slug': self.object.chat.get_slug(current_user=self.request.user)})


class MarkChatAsReadView(UserSingleChatMixin, generic.View):
    """
    Marks the resolved chat as read for the profile's user.

    Methods:
        get(self, request, *args, **kwargs): Redirects GET requests to the chat page without marking it as read.
        post(self, request, *args, **kwargs): Marks the chat as read for the profile's user and redirects to the chat page.
        get_success_url(self): Returns the URL of the chat page.
    """

    def get(self, request, *args, **kwargs):
        """
        Redirects GET requests to the chat page without marking it as read, since this action only supports POST.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the chat page.
        :rtype: django.http.HttpResponseRedirect
        """
        return redirect(to=self.get_success_url())

    def post(self, request, *args, **kwargs):
        """
        Marks the chat as read for the profile's user and redirects to the chat page.

        :param request: The HTTP request.
        :type request: django.http.HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: A redirect response to the chat page.
        :rtype: django.http.HttpResponseRedirect
        """
        self.get_chat().mark_read(entity=self.get_user())
        return redirect(to=self.get_success_url())

    def get_success_url(self):
        """
        :return: The URL of the chat page, using the slug relative to the profile's user.
        :rtype: str
        """
        return reverse(viewname='messages:chat', kwargs={'chat_slug': self.chat.get_slug(current_user=self.user)})


