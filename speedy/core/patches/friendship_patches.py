def patch():
    from friendship.models import BUST_CACHES, CACHE_TYPES, Friend, FriendshipManager, FriendshipRequest, cache, cache_key

    MAX_NUMBER_OF_FRIENDS_TO_CACHE = 400
    MAX_NUMBER_OF_REQUESTS_TO_CACHE = 4000

    CACHE_TYPES.setdefault("friends_count", "speedy-core-friends-count-%s")
    BUST_CACHES["friends"].append("friends_count") if "friends_count" not in BUST_CACHES["friends"] else None

    def friends(self, user):
        """ Return a list of all friends """
        key = cache_key("friends", user.pk)
        friends = cache.get(key)

        if friends is None:
            qs = Friend.objects.select_related("from_user").filter(to_user=user)
            friends = [u.from_user for u in qs]
            if (len(friends) <= MAX_NUMBER_OF_FRIENDS_TO_CACHE):
                cache.set(key, friends)

        return friends

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
            if (len(requests) <= MAX_NUMBER_OF_REQUESTS_TO_CACHE):
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
            if (len(requests) <= MAX_NUMBER_OF_REQUESTS_TO_CACHE):
                cache.set(key, requests)

        return requests

    FriendshipManager.friends = friends
    FriendshipManager.requests = requests
    FriendshipManager.sent_requests = sent_requests


