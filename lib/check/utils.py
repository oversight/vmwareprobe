import calendar


ALLOWED_FQDN_CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789-.'


def hostname_to_valid_fqdn(host_name):
    fqdn = ''
    for cr in host_name.lower():
        if cr in ALLOWED_FQDN_CHARS:
            fqdn += cr
        elif cr == '_':
            fqdn += '-'

    return fqdn


def datetime_to_timestamp(inp):
    if inp is None:
        return inp
    return calendar.timegm(inp.timetuple())
