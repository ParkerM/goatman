"""
Helper for various utility methods
"""
import json
import os.path

import requests

TLD_URL = 'http://data.iana.org/TLD/tlds-alpha-by-domain.txt'

def load_config(config_rel_path):
    """Load config data.

    Parameters
    ----------
    config_rel_path: Relative file path

    Returns
    -------
    dict: Config data
    """
    config_path = get_path('../' + config_rel_path)
    with open(config_path, 'r') as config_in:
        config = json.load(config_in)
    return config

def fetch_tlds(domain_name=None):
    """Get a set of valid top level domains from the URL defined in `TLD_URL`.
    Assumes response is a line seperated list of TLD's

    Parameters
    ----------
    domain_name: Optional. Change the returned set to a tuple containing a set
    of URL's for the supplied domain name. Convenient for using `Pool.map`

    Returns
    -------
    set: Set of top-level domains
    """
    tld_str = requests.get(TLD_URL).text
    if domain_name:
        tld_set = {
            (x.lower(), domain_name + '.' + x.lower())
            for x in tld_str.split('\n') if is_valid_tld(x)
        }
    else:
        tld_set = {x.lower() for x in tld_str.split('\n') if is_valid_tld(x)}
    return tld_set

def is_valid_tld(tld):
    """Check if retrieved TLD is valid. Used for filtering in :func:`fetch_tlds`

    Parameters
    ----------
    tld: Top-level domain string

    Returns
    -------

    """
    if tld is None or tld == '' or tld.startswith('#'):
        return False
    return True

def get_path(rel_path):
    """Get a file path from a specified relative path

    Parameters
    ----------
    rel_path: relative path

    Returns
    -------
    sanitized path
    """
    return os.path.join(os.path.dirname(__file__), rel_path)
