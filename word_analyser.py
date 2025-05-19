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