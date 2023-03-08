# force-update-fleet-agents

This is a quick & dirty script to force the update of Elastic Fleet agents.

They sometimes get stuck in "updating" state for some reason, and this helps them get unstuck.

It uses the Kibana Fleet API, which doesn't seem to be documented, so it may break at any time.

## Running

1. Install the dependencies:
    ```shell
    pip install -r requirements.txt
    ```
2. Copy the example config in [`config.example`](config.example) to `force-update-fleet-agents/config.py`.
3. Update `config.py` with your environment settings.
4. Run the script from the root of the repository:
    ```shell
    python -m force-update-fleet-agents
    ```
