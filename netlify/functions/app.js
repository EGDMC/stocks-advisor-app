
const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
  // Handle health checks
  if (event.httpMethod === 'GET' && event.path === '/.netlify/functions/app/health') {
    return {
      statusCode: 200,
      body: JSON.stringify({
        status: 'healthy',
        version: '1.0.0',
        timestamp: new Date().toISOString()
      })
    };
  }

  // Parse request details
  const requestPath = event.path.replace('/.netlify/functions/app', '');
  
  try {
    // Spawn Python process
    const pythonPath = path.join(__dirname, '.python_env/bin/python');
    const scriptPath = path.join(__dirname, 'handler.py');
    
    const pythonProcess = spawn('python', [scriptPath], {
      env: {
        ...process.env,
        REQUEST_PATH: requestPath,
        REQUEST_METHOD: event.httpMethod,
        REQUEST_BODY: event.body || ''
      }
    });

    // Get response from Python
    return new Promise((resolve, reject) => {
      let result = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          resolve({
            statusCode: 500,
            body: JSON.stringify({
              error: 'Internal server error',
              details: error
            })
          });
        } else {
          try {
            const response = JSON.parse(result);
            resolve({
              statusCode: 200,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(response)
            });
          } catch (e) {
            resolve({
              statusCode: 200,
              headers: { 'Content-Type': 'text/html' },
              body: result
            });
          }
        }
      });
    });
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message
      })
    };
  }
};
