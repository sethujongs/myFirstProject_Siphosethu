// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const chartControls = document.getElementById('chart-controls');
    const statisticsSection = document.getElementById('statistics-section');
    const chartSection = document.getElementById('chart-section');
    const welcomeSection = document.getElementById('welcome-section');
    const generateChartBtn = document.getElementById('generate-chart');
    const chartTypeSelect = document.getElementById('chart-type');
    const xColumnSelect = document.getElementById('x-column');
    const yColumnSelect = document.getElementById('y-column');
    const yColumnContainer = document.getElementById('y-column-container');

    // Handle file upload
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showStatus('Please select a file to upload.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        showStatus('<span class="loading"></span>Uploading and analyzing file...', 'info');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                showStatus('File uploaded successfully!', 'success');
                displayAnalytics(result);
                populateColumnSelects(result.columns);
                showSection('statistics');
            } else {
                showStatus(`Error: ${result.error}`, 'error');
            }
        } catch (error) {
            showStatus(`Error: ${error.message}`, 'error');
        }
    });

    // Handle chart generation
    generateChartBtn.addEventListener('click', async function() {
        const chartType = chartTypeSelect.value;
        const xColumn = xColumnSelect.value;
        const yColumn = yColumnSelect.value;

        // Validation
        if (!xColumn) {
            alert('Please select an X-axis column');
            return;
        }

        if (needsYColumn(chartType) && !yColumn) {
            alert('Please select a Y-axis column');
            return;
        }

        const requestData = {
            chart_type: chartType,
            x_column: xColumn,
            y_column: yColumn
        };

        try {
            generateChartBtn.innerHTML = '<span class="loading"></span>Generating chart...';
            generateChartBtn.disabled = true;

            const response = await fetch('/generate_chart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.chart) {
                const chartData = JSON.parse(result.chart);
                Plotly.newPlot('chart-container', chartData.data, chartData.layout, {responsive: true});
                showSection('chart');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            generateChartBtn.innerHTML = 'Generate Chart';
            generateChartBtn.disabled = false;
        }
    });

    // Handle chart type changes
    chartTypeSelect.addEventListener('change', function() {
        updateYColumnVisibility();
    });

    function showStatus(message, type) {
        uploadStatus.innerHTML = `<div class="alert alert-${getAlertClass(type)}" role="alert">${message}</div>`;
    }

    function getAlertClass(type) {
        switch(type) {
            case 'success': return 'success';
            case 'error': return 'danger';
            case 'info': return 'info';
            default: return 'secondary';
        }
    }

    function displayAnalytics(data) {
        // Display basic statistics
        const statsContainer = document.getElementById('basic-stats');
        statsContainer.innerHTML = `
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.total_rows}</div>
                    <div class="stat-label">Total Rows</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.total_columns}</div>
                    <div class="stat-label">Total Columns</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.numeric_columns}</div>
                    <div class="stat-label">Numeric Columns</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="stat-value">${data.stats.missing_values}</div>
                    <div class="stat-label">Missing Values</div>
                </div>
            </div>
        `;

        // Display data preview
        document.getElementById('data-preview').innerHTML = data.preview;

        // Display column information
        const columnInfoContainer = document.getElementById('column-info');
        let columnInfoHtml = '';
        
        data.stats.column_info.forEach(col => {
            columnInfoHtml += `
                <div class="column-card">
                    <div class="column-name">${col.name}</div>
                    <div class="column-details">
                        <span class="badge bg-primary">${col.type}</span>
                        <span class="badge bg-info">${col.unique_values} unique values</span>
                        ${col.missing > 0 ? `<span class="badge bg-warning">${col.missing} missing</span>` : ''}
                        ${col.mean !== undefined ? `<span class="badge bg-success">Mean: ${col.mean}</span>` : ''}
                        ${col.min !== undefined ? `<span class="badge bg-secondary">Min: ${col.min}</span>` : ''}
                        ${col.max !== undefined ? `<span class="badge bg-secondary">Max: ${col.max}</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        columnInfoContainer.innerHTML = columnInfoHtml;
    }

    function populateColumnSelects(columns) {
        // Clear existing options
        xColumnSelect.innerHTML = '<option value="">Select column...</option>';
        yColumnSelect.innerHTML = '<option value="">Select column...</option>';

        // Add column options
        columns.forEach(column => {
            const optionX = new Option(column, column);
            const optionY = new Option(column, column);
            xColumnSelect.add(optionX);
            yColumnSelect.add(optionY);
        });
    }

    function needsYColumn(chartType) {
        return ['bar', 'line', 'scatter', 'box'].includes(chartType);
    }

    function updateYColumnVisibility() {
        const chartType = chartTypeSelect.value;
        if (needsYColumn(chartType)) {
            yColumnContainer.style.display = 'block';
        } else {
            yColumnContainer.style.display = 'none';
        }
    }

    function showSection(section) {
        // Hide all sections
        welcomeSection.style.display = 'none';
        statisticsSection.style.display = 'none';
        chartSection.style.display = 'none';
        
        // Show requested section
        if (section === 'statistics') {
            statisticsSection.style.display = 'block';
            chartControls.style.display = 'block';
        } else if (section === 'chart') {
            statisticsSection.style.display = 'block';
            chartSection.style.display = 'block';
            chartControls.style.display = 'block';
        }
    }

    // Initialize Y-column visibility
    updateYColumnVisibility();
});