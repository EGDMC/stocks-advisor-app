const { spawn } = require('child_process');
const path = require('path');

exports.handler = async (event, context) => {
    // Set CORS headers
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
    };

    // Handle preflight requests
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    // Handle GET requests (health check)
    if (event.httpMethod === 'GET') {
        return {
            statusCode: 200,
            headers: { ...headers, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: 'healthy',
                timestamp: new Date().toISOString()
            })
        };
    }

    // Handle POST requests
    if (event.httpMethod === 'POST') {
        try {
            // Parse request body
            const requestBody = JSON.parse(event.body);
            console.log('Request body:', requestBody);

            // Extract CSV content
            const csvContent = requestBody.csv_content;
            if (!csvContent) {
                throw new Error('No CSV content provided');
            }

            // Parse CSV content to extract data
            const lines = csvContent.split('\n').map(line => line.trim()).filter(line => line);
            const header = lines[0].split(',').map(col => col.trim());

            // Verify required columns
            const requiredColumns = ['date', 'open', 'high', 'low', 'close', 'volume'];
            const missingColumns = requiredColumns.filter(col => !header.includes(col));
            if (missingColumns.length > 0) {
                throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
            }

            // Extract column indices
            const dateIndex = header.indexOf('date');
            const openIndex = header.indexOf('open');
            const highIndex = header.indexOf('high');
            const lowIndex = header.indexOf('low');
            const closeIndex = header.indexOf('close');
            const volumeIndex = header.indexOf('volume');

            // Process data rows
            const data = lines.slice(1).map(line => {
                const values = line.split(',').map(val => val.trim());
                return {
                    date: values[dateIndex],
                    open: parseFloat(values[openIndex]),
                    high: parseFloat(values[highIndex]),
                    low: parseFloat(values[lowIndex]),
                    close: parseFloat(values[closeIndex]),
                    volume: parseInt(values[volumeIndex])
                };
            });

            // Prepare input for Python script
            const analysisData = {
                type: requestBody.type || 'standard',
                data: {
                    dates: data.map(row => row.date),
                    open: data.map(row => row.open),
                    high: data.map(row => row.high),
                    low: data.map(row => row.low),
                    close: data.map(row => row.close),
                    volume: data.map(row => row.volume)
                }
            };

            // Call Python script
            const pythonProcess = spawn('python', [
                path.join(__dirname, 'smc_analyzer.py')
            ], {
                env: {
                    ...process.env,
                    INPUT_DATA: JSON.stringify(analysisData)
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
                        console.error('Python error:', error);
                        reject(new Error(error || 'Python process failed'));
                    } else {
                        try {
                            resolve(JSON.parse(output));
                        } catch (e) {
                            console.error('JSON parse error:', e);
                            reject(new Error('Invalid JSON output from Python script'));
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
                statusCode: 400,
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    error: error.message,
                    details: error.stack
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
