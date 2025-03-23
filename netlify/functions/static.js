// Navigation handling
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = item.getAttribute('data-page');
            
            // Update navigation
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update pages
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.getElementById(pageId + '-page').classList.add('active');
        });
    });
}

// File upload handling
function initFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const selectedFileText = document.getElementById('selectedFile');
    const uploadForm = document.getElementById('uploadForm');
    const loading = document.querySelector('.loading');

    // Prevent defaults for drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Handle file selection
    fileInput.addEventListener('change', handleFileSelect);
    dropZone.addEventListener('drop', handleDrop);

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            selectedFileText.textContent = file.name;
            handleFileUpload(file);
        }
    }

    function handleDrop(e) {
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            selectedFileText.textContent = file.name;
            handleFileUpload(file);
        }
    }

    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        loading.classList.add('active');
        
        try {
            const response = await fetch('/api', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'success') {
                updateAnalysis(result.analysis);
                // Switch to price analysis page
                document.querySelector('[data-page="price"]').click();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error processing file: ' + error.message);
        } finally {
            loading.classList.remove('active');
        }
    }
}

// Drag and drop styling
function initDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('highlight');
    }
}

// Analysis updates
function updateAnalysis(analysis) {
    // Create charts
    createCharts(analysis.chart_configs);
    
    // Update all sections
    document.getElementById('technicalSignals').innerHTML = 
        formatTechnicalSignals(analysis.technical_signals);
    formatPatterns(analysis.patterns);
    formatTrendAnalysis(analysis.trend_analysis);
    
    // Update SMC analysis
    const smcAnalysis = document.getElementById('smc-analysis');
    if (analysis.smc_analysis) {
        smcAnalysis.style.display = 'block';
        document.getElementById('smcContent').innerHTML = 
            formatSMCAnalysis(analysis.smc_analysis);
    } else {
        smcAnalysis.style.display = 'none';
    }
    
    // Update price statistics
    document.getElementById('resultContent').innerHTML = 
        formatMetrics(analysis);
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFileUpload();
    initDragAndDrop();
});