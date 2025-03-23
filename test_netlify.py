import requests
import json
import sys
from pathlib import Path

def test_netlify_deployment(site_url):
    """Test Netlify deployment endpoints"""
    print(f"=== Testing Netlify Deployment: {site_url} ===\n")
    
    tests = [
        {
            'name': 'Homepage',
            'endpoint': '/',
            'method': 'GET',
            'expected_type': 'text/html'
        },
        {
            'name': 'Health Check',
            'endpoint': '/.netlify/functions/health',
            'method': 'GET',
            'expected_type': 'application/json'
        },
        {
            'name': 'Analysis Endpoint',
            'endpoint': '/.netlify/functions/analyze',
            'method': 'POST',
            'data': {
                'type': 'bullish',
                'data': {
                    'dates': ['2024-01-01', '2024-01-02'],
                    'prices': [100, 102],
                    'volumes': [1000, 1100]
                }
            },
            'expected_type': 'application/json'
        }
    ]
    
    success_count = 0
    
    for test in tests:
        print(f"\nTesting {test['name']}...")
        try:
            if test['method'] == 'GET':
                response = requests.get(f"{site_url}{test['endpoint']}")
            else:
                response = requests.post(
                    f"{site_url}{test['endpoint']}", 
                    json=test['data']
                )
            
            # Check status code
            if response.status_code == 200:
                print(f"✓ Status: {response.status_code}")
            else:
                print(f"✗ Status: {response.status_code}")
                continue
                
            # Check content type
            content_type = response.headers.get('content-type', '')
            if test['expected_type'] in content_type:
                print(f"✓ Content-Type: {content_type}")
            else:
                print(f"✗ Expected {test['expected_type']}, got {content_type}")
                continue
                
            # Check response
            if 'application/json' in content_type:
                data = response.json()
                print("Response:", json.dumps(data, indent=2))
            else:
                print(f"Response length: {len(response.text)} chars")
                
            success_count += 1
            
        except requests.RequestException as e:
            print(f"✗ Request failed: {str(e)}")
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests passed: {success_count}/{len(tests)}")
    
    return success_count == len(tests)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_netlify.py <site-url>")
        print("Example: python test_netlify.py https://your-site.netlify.app")
        sys.exit(1)
        
    site_url = sys.argv[1].rstrip('/')
    if not test_netlify_deployment(site_url):
        sys.exit(1)

if __name__ == "__main__":
    main()