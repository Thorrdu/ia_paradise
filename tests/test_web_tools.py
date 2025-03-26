import asyncio
import pytest
from agents.web_tools import (
    RateLimiter,
    SecurityManager,
    WebBrowserTool,
    APIGatewayTool,
    DirectSocketTool
)

@pytest.fixture
def rate_limiter():
    return RateLimiter(requests_per_minute=60)

@pytest.fixture
def security_manager():
    return SecurityManager(allowed_domains=["python.org", "github.com"])

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RateLimiter(requests_per_minute=2)
    start_time = asyncio.get_event_loop().time()
    
    # First request - should pass immediately
    await limiter.wait_if_needed()
    
    # Second request - should pass immediately
    await limiter.wait_if_needed()
    
    # Third request - should wait
    await limiter.wait_if_needed()
    
    end_time = asyncio.get_event_loop().time()
    assert end_time - start_time >= 60, "The rate limiter did not correctly limit the requests"

@pytest.mark.asyncio
async def test_security_manager():
    manager = SecurityManager(allowed_domains=["python.org"])
    
    assert manager.is_allowed_domain("https://www.python.org/doc")
    assert not manager.is_allowed_domain("https://malicious-site.com")

@pytest.mark.asyncio
async def test_web_browser_tool(rate_limiter, security_manager):
    browser_tool = WebBrowserTool(rate_limiter, security_manager)
    
    # Test access to an allowed domain
    content = await browser_tool.get_page_content("https://www.python.org")
    assert "Python" in content
    
    # Test access to an unauthorized domain
    with pytest.raises(ValueError):
        await browser_tool.get_page_content("https://unauthorized-domain.com")

@pytest.mark.asyncio
async def test_api_gateway_tool(rate_limiter, security_manager):
    api_tool = APIGatewayTool(rate_limiter, security_manager)
    
    # Test a valid API request
    response = await api_tool.make_request("https://api.github.com/users/python")
    assert response["status"] == 200
    
    # Test a request to an unauthorized domain
    with pytest.raises(ValueError):
        await api_tool.make_request("https://unauthorized-api.com")

@pytest.mark.asyncio
async def test_direct_socket_tool(rate_limiter, security_manager):
    socket_tool = DirectSocketTool(rate_limiter, security_manager)
    
    # Test connection to an allowed domain
    await socket_tool.connect("python.org", 80)
    response = await socket_tool.send_data("GET / HTTP/1.0\r\nHost: python.org\r\n\r\n")
    assert "HTTP/" in response
    await socket_tool.close()
    
    # Test connection to an unauthorized domain
    with pytest.raises(ValueError):
        await socket_tool.connect("unauthorized-domain.com", 80)

if __name__ == "__main__":
    pytest.main(["-v", __file__])