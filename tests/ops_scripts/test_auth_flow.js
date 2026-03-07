const https = require('https');

function fetchCookieAndRedirect(url, cookies = '') {
  console.log(`\n[GET] ${url}`);
  const options = {
    headers: { 'Cookie': cookies, 'User-Agent': 'node-fetch' }
  };
  
  const req = https.get(url, options, (res) => {
    console.log(`Status: ${res.statusCode}`);
    console.log(`Set-Cookie: ${res.headers['set-cookie'] || 'none'}`);
    console.log(`Location: ${res.headers['location'] || 'none'}`);
    
    // Step 2: Follow redirect
    if (res.statusCode === 302 || res.statusCode === 303 || res.statusCode === 307) {
        console.log(`Redirecting to: ${res.headers['location']}`);
    } else {
        res.setEncoding('utf8');
        let rawData = '';
        res.on('data', (chunk) => { rawData += chunk; });
        res.on('end', () => console.log(`Body snippet: ${rawData.substring(0, 150)}`));
    }
  });
  req.on('error', (e) => console.error(e));
}

// Emulate user clicking "Sign in with Google" -> hits Next.js Rewrite -> hits backend /auth/login
fetchCookieAndRedirect('https://marffet-app.zeabur.app/auth/login');

// Note: Oauth callbacks are hard to script without a real browser. I'll test the initial redirect first.
