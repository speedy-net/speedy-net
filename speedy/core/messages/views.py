from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin

from speedy.core.profiles.views import UserMixin
from speedy.core.base.utils import normalize_username
from .forms import MessageForm
from .models import Chat


class UserChatsMixin(UserMixin, PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request=request, *args, **kwargs)
        except PermissionDenied:
            return self.handle_no_permission()

    def get_chat_queryset(self):
        return Chat.objects.chats(entity=self.get_user()).select_related('ent1__user', 'ent2__user', 'last_message')

    def has_permission(self):
        return self.request.user.has_perm(perm='messages.view_chats', obj=self.user)


class UserSingleChatMixin(UserChatsMixin):
    def dispatch(self, request, *args, **kwargs):
        try:
            self.chat = self.get_chat()
            return super().dispatch(request=request, *args, **kwargs)
        except PermissionDenied:
            return self.handle_no_permission()

    def get_chat(self):
        slug = self.kwargs['chat_slug']
        user = self.get_user()
        try:
            q_id = Q(id=slug)
            q_slug_1 = Q(ent1__slug=slug, ent2_id=user.id)
            q_slug_2 = Q(ent1_id=user.id, ent2__slug=slug)
            return self.get_chat_queryset().filter(q_id | q_slug_1 | q_slug_2)[0]
        except (IndexError, Chat.DoesNotExist):
            raise Http404()

    def get_messages_queryset(self):
        return self.get_chat().message_set.select_related('sender__user')

    def has_permission(self):
        return ((super().has_permission()) and (self.request.user.has_perm(perm='messages.read_chat', obj=self.chat)))

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'chat': self.chat,
        })
        return cd


class ChatListView(UserChatsMixin, PermissionRequiredMixin, generic.ListView):
    template_name = 'messages/chat_list.html'
    paginate_by = 25

    def get_queryset(self):
        return self.get_chat_queryset()


class ChatDetailView(UserSingleChatMixin, generic.ListView):
    template_name = 'messages/chat_detail.html'
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        if (not (request.user.is_authenticated)):
            return self.handle_no_permission()
        visited_user_slug = self.kwargs['chat_slug']
        visited_user = self.get_user_queryset().filter(Q(username=normalize_username(username=visited_user_slug)) | Q(id=visited_user_slug)).first()
        if ((visited_user) and (visited_user.slug != visited_user_slug)):
            return redirect(to=reverse('messages:chat', kwargs={'chat_slug': visited_user.slug}))
        if ((visited_user) and (visited_user != request.user) and (not (Chat.objects.chat_with(ent1=self.request.user, ent2=visited_user, create=False)))):
            self.user = visited_user
            self.chat = None
            return self.get(request=request, *args, **kwargs)
        return super().dispatch(request=request, *args, **kwargs)

    def get_form(self):
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
        if (self.chat):
            return self.get_messages_queryset()
        else:
            return []

    def get_template_names(self):
        if (self.chat):
            return 'messages/chat_detail.html'
        else:
            return 'messages/message_form.html'

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd.update({
            'form': self.get_form(),
        })
        return cd


class ChatPollMessagesView(UserSingleChatMixin, generic.ListView):
    template_name = 'messages/message_list_poll.html'

    def get_queryset(self):
        since = float(self.request.GET.get('since', 0))
        since += 0.0001
        return self.get_messages_queryset().filter(date_created__gt=datetime.fromtimestamp(since))


class SendMessageToChatView(UserSingleChatMixin, generic.CreateView):
    template_name = 'messages/chat_detail.html'
    form_class = MessageForm
    raise_exception = True

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
        return reverse('messages:chat', kwargs={'chat_slug': self.chat.get_slug(current_user=self.user)})

    def has_permission(self):
        if (self.chat.participants_count != 2):
            return super().has_permission()
        return self.user.has_perm(perm='messages.send_message', obj=self.chat.get_other_participants(entity=self.user)[0])


class SendMessageToUserView(UserMixin, PermissionRequiredMixin, generic.CreateView):
    permission_required = 'messages.send_message'
    template_name = 'messages/message_form.html'
    form_class = MessageForm

    def get(self, request, *args, **kwargs):
        existing_chat = Chat.objects.chat_with(ent1=self.request.user, ent2=self.user, create=False)
        if (existing_chat is not None):
            return redirect(to='messages:chat', **{'chat_slug': existing_chat.get_slug(current_user=self.request.user)})
        return super().get(request=request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'from_entity': self.request.user,
            'to_entity': self.user,
        })
        return kwargs

    def get_success_url(self):
        return reverse('messages:chat', kwargs={'chat_slug': self.object.chat.get_slug(current_user=self.request.user)})


class MarkChatAsReadView(UserSingleChatMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return redirect(to=self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.get_chat().mark_read(entity=self.get_user())
        return redirect(to=self.get_success_url())

    def get_success_url(self):
        return reverse('messages:chat', kwargs={'chat_slug': self.chat.get_slug(current_user=self.user)})


