// Nexus Market Analytics Dashboard Chart Initializer

document.addEventListener('DOMContentLoaded', () => {
    initSalesForecastChart();
});

function initSalesForecastChart() {
    const ctx = document.getElementById('salesForecastChart');
    if (!ctx) return;
    
    // Fetch analytics metrics from API
    fetch('/api/sales/forecast-data')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error("Dashboard statistics retrieval failed:", data.error);
                return;
            }
            
            renderChart(ctx, data);
        })
        .catch(err => console.error("Error fetching forecast dataset:", err));
}

function renderChart(canvasElement, data) {
    const ctx = canvasElement.getContext('2d');
    
    // Gradient color fills
    const actualGradient = ctx.createLinearGradient(0, 0, 0, 300);
    actualGradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
    actualGradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');
    
    const forecastGradient = ctx.createLinearGradient(0, 0, 0, 300);
    forecastGradient.addColorStop(0, 'rgba(168, 85, 247, 0.2)');
    forecastGradient.addColorStop(1, 'rgba(168, 85, 247, 0.0)');
    
    // Prepare arrays matching forecast_labels
    // Actual sales should be null for dates in the future so the line stops
    const actualRevenueDataset = [];
    const forecastRevenueDataset = [];
    
    const historyCount = data.history_labels.length;
    const totalCount = data.forecast_labels.length;
    
    for (let i = 0; i < totalCount; i++) {
        if (i < historyCount) {
            actualRevenueDataset.push(data.history_revenue[i]);
            // Forecast line overlaps the history for continuity
            forecastRevenueDataset.push(data.history_revenue[i]);
        } else {
            actualRevenueDataset.push(null);
            forecastRevenueDataset.push(data.forecast_revenue[i]);
        }
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.forecast_labels,
            datasets: [
                {
                    label: 'Actual Revenue ($)',
                    data: actualRevenueDataset,
                    borderColor: '#6366f1',
                    backgroundColor: actualGradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#6366f1',
                    pointRadius: 4
                },
                {
                    label: 'AI Sales Forecast ($)',
                    data: forecastRevenueDataset,
                    borderColor: '#a855f7',
                    backgroundColor: forecastGradient,
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#a855f7',
                    pointRadius: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-primary').trim() || '#333',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--border-color').trim() || 'rgba(0,0,0,0.05)'
                    },
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-muted').trim() || '#888'
                    }
                },
                y: {
                    grid: {
                        color: getComputedStyle(document.body).getPropertyValue('--border-color').trim() || 'rgba(0,0,0,0.05)'
                    },
                    ticks: {
                        color: getComputedStyle(document.body).getPropertyValue('--text-muted').trim() || '#888',
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}
