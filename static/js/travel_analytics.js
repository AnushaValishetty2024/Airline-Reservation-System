(function () {
    const spendingCtx = document.getElementById('spendingChart');
    if (spendingCtx) {
        const mLabels = monthlyLabels;
        const mData = monthlySpending;
        new Chart(spendingCtx, {
            type: 'line',
            data: {
                labels: mLabels,
                datasets: [{
                    label: 'Monthly Spending (INR)',
                    data: mData,
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    const bookingTrendCtx = document.getElementById('bookingTrendChart');
    if (bookingTrendCtx) {
        const confirmed = typeof confirmedBookings !== 'undefined' ? confirmedBookings : 0;
        const pending = typeof pendingBookings !== 'undefined' ? pendingBookings : 0;
        const cancelled = typeof cancelledBookings !== 'undefined' ? cancelledBookings : 0;
        const completed = typeof completedBookings !== 'undefined' ? completedBookings : 0;
        new Chart(bookingTrendCtx, {
            type: 'bar',
            data: {
                labels: ['Confirmed', 'Pending', 'Cancelled', 'Completed'],
                datasets: [{
                    label: 'Bookings',
                    data: [confirmed, pending, cancelled, completed],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#06b6d4'],
                    borderColor: ['#10b981', '#f59e0b', '#ef4444', '#06b6d4'],
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    const paymentMethodCtx = document.getElementById('paymentMethodChart');
    if (paymentMethodCtx && typeof window.paymentMethodDistribution !== 'undefined') {
        const labels = Object.keys(window.paymentMethodDistribution);
        const data = Object.values(window.paymentMethodDistribution);
        new Chart(paymentMethodCtx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#4f46e5',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#06b6d4',
                        '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    const airlineCtx = document.getElementById('airlineChart');
    if (airlineCtx && typeof window.airlineDistribution !== 'undefined') {
        const labels = Object.keys(window.airlineDistribution);
        const data = Object.values(window.airlineDistribution);
        new Chart(airlineCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#4f46e5',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#06b6d4',
                        '#8b5cf6',
                        '#ec4899',
                        '#14b8a6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
})();
