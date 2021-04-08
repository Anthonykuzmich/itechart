import json
import uuid

from redis import Redis


class LocalStorage:
    state_dict = {}


class RedisStorage(LocalStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def load_state(self):
        self.redis_adapter.set('data', json.dumps(self.state_dict))

    def retrieve_state(self):
        states = self.redis_adapter.get('data')
        return json.loads(states)


class JsonFileStorage(LocalStorage):

    def __init__(self, filepath):
        self.filepath = filepath

    def load_json_state(self):
        state = self.state_dict
        with open(self.filepath, 'w') as file:
            json.dump(state, file)

    def retrieve_state(self):
        with open(self.filepath, 'r') as file:
            try:
                data = json.load(file)
                return data
            except json.decoder.JSONDecodeError:
                return 'no data'


class State(LocalStorage):
    def __init__(self, identificator, state_value):
        self.state = state_value
        self.identificator = identificator

    def set_state(self):
        self.state_dict[self.identificator] = self.state

    def get_state(self):
        return self.state_dict[self.identificator]


# examples of work____________________________________________--
if __name__ == '__main__':
    r = Redis()
    s = State('dasda', 'dasda')
    s.set_state()
    RedisStorage(r).load_state()
    print(RedisStorage(r).retrieve_state())
