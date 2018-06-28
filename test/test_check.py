from helpers import cmd


def test_check(httpbin):
    """Test if check returns latest version number."""

    source = {
        'index': httpbin + '/links/10',
        'regex': "href='/links/10/(?P<version>[0-9]+)'",
    }

    output = cmd('check', source)

    assert output == [{'version': '9'}]

def test_check_with_version(httpbin):
    """Test if check returns requested and newer version numbers."""

    source = {
        'index': httpbin + '/links/10',
        'regex': "href='/links/10/(?P<version>[0-9]+)'",
    }

    version = {
        'version': '7',
    }

    output = cmd('check', source, version=version)

    assert output == [
        {'version': '7'},
        {'version': '8'},
        {'version': '9'},
    ]

def test_check_with_missing_version(httpbin):
    """Test if current version is invalid check returns newer version numbers."""

    source = {
        'index': httpbin + '/links/3/0',
        'regex': "href='/links/3/(?P<version>[0-9]+)'",
    }

    version = {
        'version': '0',
    }

    output = cmd('check', source, version=version)

    assert output == [
        {'version': '1'},
        {'version': '2'},
    ]

def test_check_with_missing_version_and_older_versions(httpbin):
    """Test if current version is invalid check returns only newer version numbers."""

    source = {
        'index': httpbin + '/links/10/7',
        'regex': "href='/links/10/(?P<version>[0-9]+)'",
    }

    version = {
        'version': '7',
    }

    output = cmd('check', source, version=version)

    assert output == [
        {'version': '8'},
        {'version': '9'},
    ]

def test_check_no_new_version(httpbin):
    """When no new versions are available only return requested version."""

    source = {
        'index': httpbin + '/links/8',
        'regex': "href='/links/8/(?P<version>[0-9]+)'",
    }

    version = {
        'version': '7',
    }

    output = cmd('check', source, version=version)

    assert output == [
        {'version': '7'},
    ]
