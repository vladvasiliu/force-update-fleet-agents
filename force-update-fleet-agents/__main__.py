import dataclasses

import requests

AGENT_VERSION_MIN = "8.2"  # v8.1 has a bug which prevents update via fleet

try:
    from .config import *
except ImportError:
    print(
        "Failed to import config file. Please create `config.py` by copying `config.example`"
    )

KUERY = f'kuery=local_metadata.elastic.agent.upgradeable : true and not local_metadata.elastic.agent.version : 8.10.2 and last_checkin >= now-15m'


@dataclasses.dataclass
class Agent:
    id: str
    version: str
    hostname: str


class Updater:
    def __init__(self):
        self._session = requests.session()
        auth = {"Authorization": f"ApiKey {API_KEY}"}
        xsrf = {"kbn-xsrf": "some-header"}
        self._session.headers.update(auth)
        self._session.headers.update(xsrf)
        self._payload = {"version": AGENT_VERSION_TARGET, "force": True}

    def get_agents(self) -> list[Agent]:
        next_page = 1
        result = []
        while next_page:
            url = f"{KIBANA_BASE_URL}/api/fleet/agents?{KUERY}&page={next_page}"
            response = self._session.get(url)
            response.raise_for_status()

            items = response.json()["items"]
            if items:
                result.extend(parse_item_to_agent(a) for a in items)
                next_page += 1
            else:
                next_page = None

        return result

    def update_agents(self, agents: list[Agent]):
        num_agents = len(agents)
        len_num = len(str(num_agents))
        print(f"force-updating {num_agents} agents...")
        for num, agent in enumerate(agents, start=1):
            current = "{num:{width}}".format(num=num, width=len_num)
            print(
                f"updating agent {current} / {num_agents}: {agent.id} - v{agent.version} ({agent.hostname}): ",
                end="",
            )
            url = f"{KIBANA_BASE_URL}/api/fleet/agents/{agent.id}/upgrade"

            try:
                response = self._session.post(url, json=self._payload)
                response.raise_for_status()
            except Exception as e:
                print("Failed")
                print(e)
                raise e
            else:
                print(f"OK: {response.text}")


def parse_item_to_agent(item: dict) -> Agent:
    return Agent(
        id=item["id"],
        version=item["agent"]["version"],
        hostname=item["local_metadata"]["host"]["name"],
    )


if __name__ == "__main__":
    u = Updater()
    agents = u.get_agents()
    u.update_agents(agents)
