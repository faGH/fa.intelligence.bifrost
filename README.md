# fa.intelligence.bifröst
## Description
FrostAura Bifröst is a platform for making forecasts.
## Status
| Project | Status | Platform
| --- | --- | --- |
| Bifröst API | [![Containerization Workflow](https://github.com/faGH/fa.intelligence.bifrost/actions/workflows/containerization_workflow.yml/badge.svg)](https://github.com/faGH/fa.intelligence.bifrost/actions/workflows/containerization_workflow.yml) | GitHub Actions
## Docker Support
### Local
The project supports being run as a container and is in fact indended to. In order to run this service locally, simply run `docker-compose up` in the directory where the `docker-compose.yml` file resides. The service will now run.
### Docker Hub
Automated builds are set up for Docker Hub. To use this service without the source code running, use
- `docker pull frostaura/bifrost` or 
- Visit https://hub.docker.com/repository/docker/frostaura/bifrost.
#### Docker Compose Example
    version: "3"
        services:
            bifrost:
                image: "frostaura/bifrost"
            restart: unless-stopped
            container_name: bifrost
            ports:
                - 8000:9999

## How To
### Getting Started
#### Docker Requirement
- Install Docker Desktop from here: https://www.docker.com/products/docker-desktop
- After installation, ensure that if you're on windows, you switch docker from windows containers to linux containers. This can be done via the Docker icon in the system tray.

## Contribute
In order to contribute, simply fork the repository, make changes and create a pull request.

## Support
To support me in publishing and optimizing strategies, please use my referral link below it won't cost you anything but will help me lots :)

Also if you enjoy FrostAura open-source content and would like to support us in continuous delivery, please consider a donation via a platform of your choice.

| Supported Platforms | Link |
| ------------------- | ---- |
| PayPal | [Donate via Paypal](https://www.paypal.com/donate/?hosted_button_id=SVEXJC9HFBJ72) |
| Binance | [Binance Affiliate Signup](https://accounts.binance.com/en/register?ref=68898442) |

For any queries, contact dean.martin@frostaura.net.