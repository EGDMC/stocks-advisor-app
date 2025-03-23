const { spawn } = require('child_process');
const path = require('path');

// Handler for Netlify Functions
exports.handler = async (event, context) => {
  // Set Python path and script path
  const pythonPath = path.join(__dirname, '.python_env/bin/python');
  const scriptPath = path.join(__dirname, 'app.py');

  // Parse request details
  const { path: reqPath, httpMethod, body } = event;

  // Create environment for Python process
  const env = {
    ...process.env,
    PATH: process.env.PATH,
    PYTHONPATH: process.env.PYTHONPATH || '.',
    REQUEST_PATH: reqPath,
    REQUEST_METHOD: httpMethod,
    REQUEST_BODY: body || ''
  };

  try {
    // Spawn Python process
    const pythonProcess = spawn('python', [scriptPath], { env });

    // Collect data from Python process
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
              error: 'Internal Server Error',
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

      pythonProcess.on('error', (err) => {
        resolve({
          statusCode: 500,
          body: JSON.stringify({
            error: 'Failed to start Python process',
            details: err.message
          })
        });
      });
    });

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal Server Error',
        details: error.message
      })
    };
  }
};