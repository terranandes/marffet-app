const https = require('https');
https.get('https://marffet-app.zeabur.app/auth/test-cookie-set', (res) => {
    console.log("Status:", res.statusCode);
    console.log("Set-Cookie:", res.headers['set-cookie']);
});
