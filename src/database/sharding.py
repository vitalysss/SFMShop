import hashlib

SHARDS = ["shard-0", "shard-1", "shard-2", "shard-3"]


class ShardRouter:
    def __init__(self, shards):
        self.shards = shards

    def shard_for_user(self, user_id):
        encoded_user_id = str(user_id).encode()
        hash_value = hashlib.md5(encoded_user_id).hexdigest()
        hash_number = int(hash_value, 16)
        shard_index = hash_number % len(self.shards)

        return self.shards[shard_index]

    def shard_for_order(self, user_id):
        return self.shard_for_user(user_id)

    def distribution(self, user_ids):
        distribution = {shard: 0 for shard in self.shards}

        for user_id in user_ids:
            shard = self.shard_for_user(user_id)
            distribution[shard] += 1
        return distribution
