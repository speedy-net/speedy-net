def patch():
    from friendship.models import FriendshipManager, FriendshipRequest, cache, cache_key

    def requests(self, user):
        """ Return a list of friendship requests """
        key = cache_key("requests", user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = (
                # FriendshipRequest.objects.select_related("from_user", "to_user")
                FriendshipRequest.objects
                .filter(to_user=user)
                .all()
            )
            requests = list(qs)
            cache.set(key, requests)

        return requests

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        key = cache_key("sent_requests", user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = (
                # FriendshipRequest.objects.select_related("from_user", "to_user")
                FriendshipRequest.objects
                .filter(from_user=user)
                .all()
            )
            requests = list(qs)
            cache.set(key, requests)

        return requests

    FriendshipManager.requests = requests
    FriendshipManager.sent_requests = sent_requests


