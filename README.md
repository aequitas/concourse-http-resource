[![Docker Automated build](https://img.shields.io/docker/pulls/aequitas/http-resource.svg)](https://hub.docker.com/r/aequitas/http-resource/)
[![Docker Automated build](https://img.shields.io/docker/automated/aequitas/http-resource.svg)](https://hub.docker.com/r/aequitas/http-resource/)
[![Docker Automated build](https://img.shields.io/docker/build/aequitas/http-resource.svg)](https://hub.docker.com/r/aequitas/http-resource/)
[![Cyberveiligheid](https://img.shields.io/badge/Cyberveiligheid-97%25-yellow.svg)](https://eurocyber.nl)

# HTTP(S) Resource (download only)

Concourse resource to a crawl HTTP(S) page for versions and to downloading files.

https://hub.docker.com/r/aequitas/http-resource/

For interacting with HTTP API endpoints see: https://github.com/aequitas/concourse-http-api-resource

## Recent changes

- 06-2018: Handle missing previous version in version list. (@jmcarp)
- 06-2018: added README

## Deploying to Concourse

No changes are necessary to BOSH configuration. However, you must define the HTTP resource in a `resource_types` as can be seen in the below example pipeline.

## Source Configuration

* `index`: *Required.* The URI for the index to crawl.
    Example: `http://example.com/file_list.html`

* `regex`: *Required.* Python regex to find versions in the index. Supports capture groups. Requires at least one capture group named `version`.

* `uri`: *Required.* The URI for downloading a file, will be interpolated with the version number.

* `filename`: *Optional* alternate name for the downloaded file to be stored as, will be interpolated with the version number.

* `debug`: *Optional* Set debug logging of scripts, takes boolean (default `true`).

## Behavior

### `check`: Return list of versions.

Will make a request to `uri` and filter the entire file content matching `regex` and returning list of versions captured by the regex capture group.

### `in`: Download file matching version.

Interpolate `version` with `uri` and download file over HTTP(S).

#### Parameters

* `version`: *Required* The version to return (will be matched against the `version` regex capture group).

### `out`: Not supported.

## Example pipelines

### Demo

Giving an HTTP endpoint `http://example.com/index.html` with the following HTML file:

```html
<html>
  <body>
    <a href="/file-2.3.1.txt">file-2.3.1.txt</a>
    <a href="/file-1.2.3.txt">file-1.2.3.txt</a>
    <a href="/file-0.0.0.txt">file-0.0.0.txt</a>
  </body>
</html>
```

One would use the following configuration:

```yaml
resource_types:
  - name: http
    type: docker-image
    source:
      repository: aequitas/http-resource

resources:
  - name: demo
    type: http
    source:
      index: http://example.com/index.html
      regex: 'href="/file-(?P<version>[0-9\.-]).txt"'
      uri: 'http://example.com/file-{version}.txt'
````

### Downloading the latest Grafana RPM package

```yaml
resource_types:
  - name: http
    type: docker-image
    source:
      repository: aequitas/http-resource

resources:
  - name: grafana_rpm
    type: http
    source:
      index: https://packagecloud.io/grafana/stable
      regex: 'href="/grafana/stable/packages/el/6/grafana-(?P<version>[0-9\.-]).x86_64.rpm"'
      uri: 'https://packagecloud.io/grafana/stable/packages/el/6/grafana-{version}.x86_64.rpm/download.rpm'
      filename: 'grafana-{version}.x86_64.rpm'

jobs:
  - name: grafana
    plan:
      - get: grafana_rpm
        trigger: true
      - task: ...
        ...

```

### Tracking Vagrant releases (courtesy of @suhlig)

```yaml
jobs:
  - name: Vagrant Release
    type: http
    source:
      index: https://releases.hashicorp.com/vagrant/
      regex: 'href="/vagrant/(?P<version>[0-9\.]+)'
      uri: 'https://releases.hashicorp.com/vagrant/{version}/vagrant_{version}_SHA256SUMS'
```

## Development

### Testing
This resource runs a lint/test suite before building the Docker image. To test/build the image simply run:

    docker build .
