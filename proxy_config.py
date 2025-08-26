#!/usr/bin/env python3
"""
Proxy configuration for downloading books
"""

# Proxy configuration
# Uncomment and modify the following lines if you need to use a proxy

# HTTP_PROXY = "http://proxy.example.com:8080"
# HTTPS_PROXY = "https://proxy.example.com:8080"

# Or use environment variables
import os

HTTP_PROXY = os.environ.get('HTTP_PROXY', '')
HTTPS_PROXY = os.environ.get('HTTPS_PROXY', '')

def get_proxy_dict():
    """Return a dictionary with proxy settings."""
    proxies = {}
    if HTTP_PROXY:
        proxies['http'] = HTTP_PROXY
    if HTTPS_PROXY:
        proxies['https'] = HTTPS_PROXY
    return proxies

def configure_session_with_proxy(session):
    """Configure a requests session with proxy settings."""
    proxies = get_proxy_dict()
    if proxies:
        session.proxies.update(proxies)
        print(f"Configured session with proxies: {proxies}")
    return session