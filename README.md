# Notion ToDo Integration for HomeAssistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![Community Forum][forum-shield]][forum]

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JanGiese&repository=https%3A%2F%2Fgithub.com%2FJanGiese%2Fnotion_todo&category=integration)

_Integration to integrate with [Notion](https://www.notion.so/)._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`todo` | Shows all todos

## Prerequisites
- You need to have a notion account and a notion integration token. You can get one by following the instructions [here](https://developers.notion.com/docs/getting-started).
- You need to create a database from the Notion´s official ToDo template. You can find it [here](https://www.notion.so/Notion-To-Do-List-Template-0b2e2d8980b74c5e8e8c1e6c0f8b4b4e).
- You need to share the database with the integration token you created before.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
1. Download _all_ the files from the `custom_components/integration_blueprint/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Notion ToDo"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[integration_blueprint]: https://github.com/JanGiese/notion_todo
[commits-shield]: https://img.shields.io/github/commit-activity/y/JanGiese/notion_todo.svg?style=for-the-badge
[commits]: https://github.com/JanGiese/notion_todo/commits/main
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/JanGiese/notion_todo.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-JanGiese-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/JanGiese/notion_todo.svg?style=for-the-badge
[releases]: https://github.com/JanGiese/notion_todo/releases
