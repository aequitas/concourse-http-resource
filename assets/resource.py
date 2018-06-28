#!/usr/bin/env python3

import json
import logging as log
import os
import re
import sys
import tempfile
from distutils.version import LooseVersion

import requests


class HTTPResource:
    """HTTP resource implementation."""

    def check(self, source, version):
        """Check for new version(s)."""

        index = source['index']
        regex = re.compile(source['regex'])
        ssl_verify = source.get('ssl_verify', True)

        if isinstance(ssl_verify, bool):
            verify = ssl_verify
        elif isinstance(ssl_verify, str):
            verify = str(tempfile.NamedTemporaryFile(delete=False, prefix='ssl-').write(verify))

        # request index and extract versions
        response = requests.request('GET', index, verify=verify)
        response.raise_for_status()
        index_response = response.text

        log.debug('index_response: %s', index_response)

        versions = regex.findall(index_response)
        versions = [{'version': v} for v in versions]

        return self.filter_new_versions(versions, version)

    def filter_new_versions(self, versions, version):
        """Filter and sort version list according to concourse spec for new versions.

        https://concourse-ci.org/implementing-resources.html#resource-check
        """

        requested_version_valid = True

        # temporary add requested version for sorting/filter purposes
        if version and version not in versions:
            versions.append(version)
            requested_version_valid = False

        versions.sort(key=lambda x: LooseVersion(x['version']))

        # no initial version, only return most recent version
        if not version:
            return [versions[-1]]

        # remove all old versions
        versions = versions[versions.index(version):]

        # remove requested version if it was not in the received version list
        if not requested_version_valid:
            versions.remove(version)

        return versions

    def in_cmd(self, target_dir, source, version):
        """Download specific version to target_dir."""

        uri = source['uri']
        file_name = source.get('filename')
        ssl_verify = source.get('ssl_verify', True)

        if isinstance(ssl_verify, bool):
            verify = ssl_verify
        elif isinstance(ssl_verify, str):
            verify = str(tempfile.NamedTemporaryFile(delete=False, prefix='ssl-').write(verify))

        # insert version number into URI
        uri = uri.format(**version)

        response = requests.get(uri, stream=True, verify=verify)
        response.raise_for_status()

        if file_name:
            file_name = file_name.format(**version)
        else:
            file_name = uri.split('/')[-1]
        file_path = os.path.join(target_dir, file_name)
        version_file_path = os.path.join(target_dir, 'version')

        with open(file_path, 'wb') as f:
            for block in response.iter_content(1024):
                print('.', end='', file=sys.stderr)
                f.write(block)
            print()

        with open(version_file_path, 'wb') as f:
            f.write(version['version'].encode())

        metadata = []

        # add all response headers to metadata
        for header, value in response.headers.items():
            metadata.append({'name': header, 'value': value})

        # add url to metadata
        metadata.append({'name': 'url', 'value': uri})

        return {
            'version': version,
            'metadata': metadata,
        }

    def run(self, command_name, json_data, command_argument):
        """Parse input/arguments, perform requested command return output."""

        with tempfile.NamedTemporaryFile(delete=False, prefix=command_name + '-') as f:
            f.write(bytes(json_data, 'utf-8'))

        data = json.loads(json_data)

        # allow debug logging to console for tests
        if os.environ.get('RESOURCE_DEBUG', False) or data.get('source', {}).get('debug', False):
            log.basicConfig(level=log.DEBUG)
        else:
            logfile = tempfile.NamedTemporaryFile(delete=False, prefix='log')
            log.basicConfig(level=log.DEBUG, filename=logfile.name)
            stderr = log.StreamHandler()
            stderr.setLevel(log.INFO)
            log.getLogger().addHandler(stderr)

        log.debug('command: %s', command_name)
        log.debug('input: %s', data)
        log.debug('args: %s', command_argument)
        log.debug('environment: %s', os.environ)

        # combine source and params
        source = data.get('source', {})
        version = data.get('version', {})

        if command_name == 'check':
            response = self.check(source, version)
        elif command_name == 'in':
            response = self.in_cmd(command_argument[0], source, version)
        else:
            response = {}

        return json.dumps(response)

print(HTTPResource().run(os.path.basename(__file__), sys.stdin.read(), sys.argv[1:]))
