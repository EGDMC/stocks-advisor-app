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
            
            // Log request for debugging
            console.log('Received request:', {
                method: event.httpMethod,
                path: event.path,
                bodyLength: event.body.length
            });

            // Check if CSV content is provided
            if (!requestBody.csv_content) {
                throw new Error('No CSV content provided');
            }

            // Basic CSV validation
            const lines = requestBody.csv_content.split('\n');
            if (lines.length < 2) {
                throw new Error('CSV must contain at least a header and one data row');
            }

            // Parse header
            const header = lines[0].split(',');
            if (!header.includes('Date') || !header.includes('Close') || !header.includes('Volume')) {
                throw new Error('CSV must contain Date, Close, and Volume columns');
            }

            // Return a test response
            return {
                statusCode: 200,
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: 'CSV received and validated',
                    rows: lines.length - 1,
                    columns: header,
                    sample: {
                        header: lines[0],
                        firstRow: lines[1]
                    }
                })
            };

        } catch (error) {
            console.error('Error:', error);
            return {
                statusCode: 400,
                headers: { ...headers, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    error: error.message || 'Invalid request',
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
