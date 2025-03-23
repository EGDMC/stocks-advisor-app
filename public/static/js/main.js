$(document).ready(function() {
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        
        const fileInput = $('#dataFile')[0];
        if (!fileInput.files[0]) {
            alert('Please select a file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        $('#loading').show();
        $('#results').hide();
        
        $.ajax({
            url: '/.netlify/functions/app/analyze',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#loading').hide();
                $('#results').show();
                
                // Update trend
                const trend = response.trend || 'Unknown';
                $('#trendResult')
                    .text(trend)
                    .removeClass('alert-success alert-danger')
                    .addClass(trend === 'Bullish' ? 'alert-success' : 'alert-danger');
                
                // Update price chart
                if (response.chart_data) {
                    Plotly.newPlot('priceChart', response.chart_data);
                }
                
                // Update technical indicators
                if (response.indicators) {
                    $('#technicalIndicators').html(
                        Object.entries(response.indicators)
                            .map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`)
                            .join('')
                    );
                }
                
                // Update patterns
                if (response.patterns) {
                    $('#patterns').html(
                        Object.entries(response.patterns)
                            .map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`)
                            .join('')
                    );
                }
                
                // Update prediction
                if (response.prediction) {
                    $('#prediction').html(`
                        <p><strong>Direction:</strong> ${response.prediction.direction}</p>
                        <p><strong>Confidence:</strong> ${response.prediction.confidence}%</p>
                        <p><strong>Recommendation:</strong> ${response.prediction.recommendation}</p>
                    `);
                }
            },
            error: function(xhr, status, error) {
                $('#loading').hide();
                alert('Error analyzing data: ' + error);
            }
        });
    });
});