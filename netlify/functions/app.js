
const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
    // Set CORS headers
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
    };

    try {
        const requestBody = JSON.parse(event.body || '{}');
        const { data } = requestBody;

        // Call Python script for analysis
        const pythonProcess = spawn('python', [
            path.join(__dirname, 'smc_analyzer.py')
        ], {
            env: {
                ...process.env,
                INPUT_DATA: JSON.stringify(data)
            }
        });

        // Get response from Python
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
                    reject(new Error(error || 'Process failed'));
                } else {
                    try {
                        resolve(JSON.parse(output));
                    } catch (e) {
                        reject(new Error('Invalid JSON output'));
                    }
                }
            });
        });

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
                error: error.message || 'Internal server error'
            })
        };
    }
};
