# yuntracker-gpscj-home-assistant
Cheap 4G/GPS gizmo from China - HomeAssistant integration - cloud polling

```bash
docker run --name homeassistant \
  -v /Users/rpardini/hass-config:/config \
  -v /Users/rpardini/projects/github-rpardini-public/yuntracker-gpscj-home-assistant/custom_components/yuntracker_gpscj:/config/custom_components/yuntracker_gpscj \
  -p 8123:8123 --privileged ghcr.io/home-assistant/home-assistant:latest
```