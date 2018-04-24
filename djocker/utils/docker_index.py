import re
from collections import OrderedDict

import requests


class DockerIndex:
    def __init__(self):
        self.baseURL = 'https://index.docker.io/v1'

    def get_endpoint(self, endpoint):
        url = '{}{}'.format(self.baseURL, endpoint)
        return self.do_request(url)

    def do_request(self, url, results=None):
        if not results:
            results = []

        response = requests.get(url)
        response = response.json()

        results = results + response['results'] if 'results' in response else response

        if 'next' in response and response['next']:
            self.do_request(response['next'], results)
        else:
            return results

    def repo_tags(self, repo_name):
        endpoint = '/repositories/{}/tags'.format(repo_name)
        result = self.get_endpoint(endpoint)
        if isinstance(result, list):
            return [tag['name'] for tag in result]
        return None

    def get_latest_version_tags(self, repo_name):
        flavor_lookups = [
            'alpine'
        ]

        client = DockerIndex()
        tags = client.repo_tags(repo_name)
        version_lists = {}
        clean_version_tags = [tag for tag in tags if tag.replace('.', '').isdigit()]
        clean_version_tags.sort(reverse=True)

        for version in clean_version_tags:
            major_version = version
            minor_version = None

            # Extract the major version from versions with dots
            if '.' in version:
                version_split = major_version.split('.')
                major_version = version_split[0]
                minor_version = version_split[1]

            # Cast versions to integer for easier sorting
            major_version = int(major_version)

            # Get the to latest versions of each major version
            if major_version not in version_lists:
                version_lists[major_version] = []

            # Include the latest minor version of each major version
            re_check = r'{}\.{}.*'.format(major_version, minor_version)
            already_in_list = any(
                re.match(re_check, included_version) for included_version in version_lists[major_version]
            )
            if not already_in_list and minor_version:
                version_lists[major_version].append(version)

        # Order the major versions
        sorted_version_mapping = OrderedDict(sorted(version_lists.items(), reverse=True))

        # Create a list of versions
        sorted_version_list = sum(sorted_version_mapping.values(), [])

        flavor_dict = OrderedDict()
        for version in sorted_version_list:
            if version not in flavor_dict:
                flavor_dict.update({version: []})

            for flavor in flavor_lookups:
                if "{}-{}".format(version, flavor) in tags:
                    flavor_dict[version].append(flavor)

        return flavor_dict
