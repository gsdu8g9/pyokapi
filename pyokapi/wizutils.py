from http.cookiejar import MozillaCookieJar
from os.path import isfile


def cookie_jar(filename=None):
    if filename:
        if not isfile(filename):
            open(filename, 'w').write(
                '# Netscape HTTP Cookie File\n'
                '# http://curl.haxx.se/rfc/cookie_spec.html\n'
                '# This is a generated file!  Do not edit.\n\n'
            )

        _ = MozillaCookieJar(filename)
        _.load()
        return _
