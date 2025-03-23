const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const formidable = require('formidable');

exports.handler = async (event, context) => {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
  };

  // Handle preflight OPTIONS request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  // Handle GET request (health check)
  if (event.httpMethod === 'GET') {
    if (event.path.endsWith('/health')) {
      return {
        statusCode: 200,
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'healthy',
          version: '1.0.0',
          timestamp: new Date().toISOString()
        })
      };
    }
  }

  // Handle POST request (file analysis)
  if (event.httpMethod === 'POST') {
    try {
      // Parse multipart form data
      const form = new formidable.IncomingForm();
      form.uploadDir = os.tmpdir();
      form.keepExtensions = true;

      // Get the uploaded file
      const [fields, files] = await new Promise((resolve, reject) => {
        form.parse(event, (err, fields, files) => {
          if (err) reject(err);
          resolve([fields, files]);
        });
      });

      const file = files.file;
      if (!file) {
        throw new Error('No file uploaded');
      }

      // Read file content
      const fileContent = fs.readFileSync(file.path, 'utf-8');

      // Call Python script for analysis
      const pythonProcess = spawn('python', [
        path.join(__dirname, 'handler.py')
      ], {
        env: {
          ...process.env,
          FILE_CONTENT: fileContent
        }
      });

      // Get response from Python script
      const result = await new Promise((resolve, reject) => {
        let output = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
          output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
          error += data.toString();
        });

        pythonProcess.on('close', (code) => {
          if (code !== 0) {
            reject(new Error(`Python process exited with code ${code}: ${error}`));
          } else {
            try {
              resolve(JSON.parse(output));
            } catch (e) {
              reject(new Error('Invalid JSON response from Python script'));
            }
          }
        });
      });

      // Clean up temporary file
      fs.unlinkSync(file.path);

      // Return analysis results
      return {
        statusCode: 200,
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      };

    } catch (error) {
      console.error('Error:', error);
      return {
        statusCode: 500,
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: 'Internal server error',
          message: error.message
        })
      };
    }
  }

  // Handle unsupported methods
  return {
    statusCode: 405,
    headers,
    body: JSON.stringify({ error: 'Method not allowed' })
  };
};
