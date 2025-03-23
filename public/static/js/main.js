$(document).ready(function() {
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        
        const fileInput = $('#dataFile')[0];
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file');
            return;
        }
        
        // Show loading state
        $('#loading').show();
        $('#results').hide();
        
        // Read the file content
        const reader = new FileReader();
        reader.onload = function(event) {
            const csvContent = event.target.result;
            
            // Send the CSV content directly
            fetch('/.netlify/functions/app', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'analysis',
                    data: csvContent
                })
            })
            .then(response => response.json())
            .then(data => {
                $('#loading').hide();
                $('#results').show();
                
                if (data.status === 'error') {
                    throw new Error(data.error || 'Analysis failed');
                }
                
                // Update trend
                const trend = data.trend || 'Unknown';
                $('#trendResult')
                    .text(trend)
                    .removeClass('alert-success alert-danger alert-warning')
                    .addClass(getTrendClass(trend));
                
                // Update chart
                if (data.chart_data && data.chart_data.length > 0) {
                    const layout = {
                        title: 'Market Analysis',
                        xaxis: { title: 'Date' },
                        yaxis: { title: 'Price' },
                        height: 500,
                        margin: { t: 40 }
                    };
                    Plotly.newPlot('priceChart', data.chart_data, layout);
                }
                
                // Update indicators
                if (data.indicators) {
                    const indicatorsHtml = Object.entries(data.indicators)
                        .map(([key, value]) => {
                            const formattedKey = key.split('_')
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(' ');
                            return `
                                <div class="col-md-3 mb-3">
                                    <div class="card">
                                        <div class="card-body">
                                            <h6 class="card-title">${formattedKey}</h6>
                                            <p class="card-text">${formatValue(value)}</p>
                                        </div>
                                    </div>
                                </div>
                            `;
                        })
                        .join('');
                    $('#technicalIndicators').html(`
                        <div class="row">${indicatorsHtml}</div>
                    `);
                }
                
                // Update prediction
                if (data.prediction) {
                    const predictionHtml = `
                        <div class="alert ${getPredictionClass(data.prediction.direction)}">
                            <h5>Market Prediction</h5>
                            <p><strong>Direction:</strong> ${data.prediction.direction}</p>
                            <p><strong>Confidence:</strong> ${data.prediction.confidence}%</p>
                            <p><strong>Recommendation:</strong> ${data.prediction.recommendation}</p>
                        </div>
                    `;
                    $('#prediction').html(predictionHtml);
                }
            })
            .catch(error => {
                $('#loading').hide();
                alert('Error analyzing data: ' + error.message);
            });
        };
        
        reader.readAsText(file);
    });
    
    // Helper functions
    function getTrendClass(trend) {
        switch(trend.toLowerCase()) {
            case 'bullish': return 'alert-success';
            case 'bearish': return 'alert-danger';
            default: return 'alert-warning';
        }
    }
    
    function getPredictionClass(direction) {
        switch(direction.toLowerCase()) {
            case 'up': return 'alert-success';
            case 'down': return 'alert-danger';
            default: return 'alert-warning';
        }
    }
    
    function formatValue(value) {
        if (typeof value === 'number') {
            if (value > 1000000) {
                return (value / 1000000).toFixed(2) + 'M';
            } else if (value > 1000) {
                return (value / 1000).toFixed(2) + 'K';
            }
            return value.toFixed(2);
        }
        return value;
    }
});