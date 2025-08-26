# Advanced Book Downloaders

This directory contains enhanced downloaders for handling book downloads with better error handling and retry logic.

## Files

1. `enhanced_downloader.py` - Enhanced downloader with retry logic
2. `advanced_downloader.py` - Advanced downloader with custom headers and session management
3. `proxy_config.py` - Proxy configuration for downloads

## Usage

### Enhanced Downloader
```bash
python enhanced_downloader.py
```

Features:
- Retry logic for failed downloads
- Better error handling
- Uses existing downloader functions

### Advanced Downloader
```bash
python advanced_downloader.py
```

Features:
- Custom headers to mimic a real browser
- Session management for connection reuse
- Better handling of HTTP response codes
- Proxy support through `proxy_config.py`

## Proxy Configuration

To use a proxy, modify `proxy_config.py`:

```python
# Uncomment and modify the following lines if you need to use a proxy
HTTP_PROXY = "http://proxy.example.com:8080"
HTTPS_PROXY = "https://proxy.example.com:8080"
```

Or set environment variables:
```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="https://proxy.example.com:8080"
```

## Common Issues and Solutions

### 502 Bad Gateway Errors
These errors typically occur when:
1. The download server is blocking requests from the Codespace environment
2. The server is temporarily unavailable
3. The URL requires specific headers or authentication

The advanced downloader addresses these issues by:
- Setting custom headers to mimic a real browser
- Using proper session management
- Implementing better error handling

### Download Failures
If downloads continue to fail:
1. Try downloading the files manually to verify the URLs are still valid
2. Check if the server requires specific cookies or authentication
3. Consider using a proxy if the server is blocking the Codespace IP range