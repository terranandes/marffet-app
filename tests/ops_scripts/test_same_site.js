const https = require('https');

const options = {
  hostname: 'marffet-app.zeabur.app',
  path: '/auth/test-cookie-set',
  method: 'GET',
};

const req = https.request(options, (res) => {
  console.log(`STATUS: ${res.statusCode}`);
  const cookies = res.headers['set-cookie'];
  console.log(`SET-COOKIE: ${cookies}`);
  
  if (res.statusCode === 302 || res.statusCode === 303 || res.statusCode === 307) {
      console.log(`LOCATION: ${res.headers.location}`);
      if (cookies) {
          // Attempt the redirect representing the browser
          const redirectOptions = {
             hostname: 'marffet-app.zeabur.app',
             path: res.headers.location,
             method: 'GET',
             headers: { 'Cookie': cookies.map(c => c.split(';')[0]).join('; ') }
          };
          const req2 = https.request(redirectOptions, (res2) => {
             console.log(`REDIRECT STATUS: ${res2.statusCode}`);
             res2.setEncoding('utf8');
             res2.on('data', console.log);
          });
          req2.end();
      }
  }
});
req.end();
