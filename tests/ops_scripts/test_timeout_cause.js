const https = require('https');
const http = require('http');

function testEndpoint(url) {
  console.log(`\nTesting ${url}...`);
  const req = https.get(url, { timeout: 10000 }, (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
    res.setEncoding('utf8');
    let rawData = '';
    res.on('data', (chunk) => { rawData += chunk; });
    res.on('end', () => {
      console.log(`BODY: ${rawData.substring(0, 100)}...`);
    });
  });

  req.on('timeout', () => {
    console.log('REQUEST TIMED OUT');
    req.destroy();
  });

  req.on('error', (e) => {
    console.error(`ERROR: ${e.message}`);
  });
}

// Test Frontend Auth (which proxies to backend)
testEndpoint('https://marffet-app.zeabur.app/auth/debug');
// Test Backend Directly
testEndpoint('https://marffet-api.zeabur.app/healthz');
