import string

# basic set of English stop-words to exclude
STOP_WORDS = {
    'a','an','the','and','or','but','if','while','is','at','which','on',
    'for','in','to','of','with','as','by','from','that','this','it'
}

class HashMap:
    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]

    def _get_bucket_index(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        idx = self._get_bucket_index(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        idx = self._get_bucket_index(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    def remove(self, key):
        idx = self._get_bucket_index(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False

    def __len__(self):
        return self.size

    def __contains__(self, key):
        return self.get(key) is not None

    def keys(self):
        for bucket in self.buckets:
            for k, _ in bucket:
                yield k

    def values(self):
        for bucket in self.buckets:
            for _, v in bucket:
                yield v

    def items(self):
        for bucket in self.buckets:
            for k, v in bucket:
                yield (k, v)

    def most_common(self, n=None):
        """
        Return a list of (key, value) pairs sorted by value descending.
        If n is provided, return only the top n items.
        """
        all_items = list(self.items())
        all_items.sort(key=lambda kv: kv[1], reverse=True)
        return all_items if n is None else all_items[:n]


# function that counts the number of specific words in a text
def count_words(text):
    text = text.lower()
    words = text.split()
    map = HashMap()
    # strip punctuation except dot for numeric tokens
    strip_chars = ''.join(ch for ch in string.punctuation if ch != '.')
    for raw in words:
        clean = raw.strip(strip_chars)
        if not clean:
            continue
        if clean in STOP_WORDS:
            continue
        # now count
        if clean in map:
            map.put(clean, map.get(clean) + 1)
        else:
            map.put(clean, 1)
    return map