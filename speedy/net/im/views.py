from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.net.profiles.views import UserMixin
from .forms import MessageForm
from .models import Chat


class UserChatsMixin(UserMixin, PermissionRequiredMixin):
    def get_chat_queryset(self):
        return Chat.on_site.chats(self.get_user()).select_related('ent1__user', 'ent2__user', 'last_message')

    def has_permission(self):
        return self.request.user.has_perm('im.view_chats', self.user)


class UserSingleChatMixin(UserChatsMixin):
    def dispatch(self, request, *args, **kwargs):
        self.chat = self.get_chat()
        return super().dispatch(request, *args, **kwargs)

    def get_chat(self):
        try:
            return self.get_chat_queryset().get(id=self.kwargs['chat_pk'])
        except Chat.DoesNotExist:
            raise Http404()

    def get_messages_queryset(self):
        return self.get_chat().message_set.select_related('sender__user')

    def has_permission(self):
        return super().has_permission() and self.request.user.has_perm('im.read_chat', self.chat)

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'chat': self.chat,
        })
        return cd


class ChatListView(UserChatsMixin, PermissionRequiredMixin, generic.ListView):
    paginate_by = 25

    def get_queryset(self):
        return self.get_chat_queryset()


class ChatDetailView(UserSingleChatMixin, generic.ListView):
    template_name = 'im/chat_detail.html'
    paginate_by = 25

    def get_form(self):
        return MessageForm(**{
            'from_entity': self.user,
            'chat': self.chat,
        })

    def get_queryset(self):
        return self.get_messages_queryset()

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'form': self.get_form(),
        })
        return cd


class ChatPollMessagesView(UserSingleChatMixin, generic.ListView):
    template_name = 'im/message_list_poll.html'

    def get_queryset(self):
        since = float(self.request.GET.get('since', 0))
        since += 0.0001
        return self.get_messages_queryset().filter(date_created__gt=datetime.fromtimestamp(since))


class SendMessageToChatView(UserSingleChatMixin, generic.CreateView):
    template_name = 'im/chat_detail.html'
    form_class = MessageForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'from_entity': self.user,
            'chat': self.chat,
        })
        return kwargs

    def get(self, request, *args, **kwargs):
        return redirect(to=self.get_success_url())

    def get_success_url(self):
        return reverse('im:chat', kwargs={'slug': self.user.slug,
                                          'chat_pk': self.chat.id})


class SendMessageToUserView(UserMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = 'im.send_message'
    template_name = 'im/message_form.html'
    form_class = MessageForm

    def get(self, request, *args, **kwargs):
        existing_chat = Chat.on_site.chat_with(self.request.user, self.user, create=False)
        if existing_chat is not None:
            return redirect(to='im:chat', **{'slug': self.request.user.slug, 'chat_pk': existing_chat.id})
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'from_entity': self.request.user,
            'to_entity': self.user,
        })
        return kwargs

    def get_success_url(self):
        return reverse('im:chat', kwargs={'slug': self.request.user.slug, 'chat_pk': self.object.chat.id})


class MarkChatAsReadView(UserSingleChatMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return redirect(to=self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.get_chat().mark_read(self.get_user())
        return redirect(to=self.get_success_url())

    def get_success_url(self):
        return reverse('im:chat', kwargs={'slug': self.user.slug, 'chat_pk': self.chat.id})
