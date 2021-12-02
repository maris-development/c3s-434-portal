const indicatorTypes = ['overview', 'detail'];

$(function () {
    let delay = 0;
    if (typeof window.c3sIndicatorData == 'undefined') {
        window.c3sIndicatorData = {};
    }

    window.c3sMetadata.forEach(function (indicator, index) {
        setTimeout(showHistoryOfIndicator, delay * index, indicator.c3s_identifier);
    });

    $('.view_graph_btn').click(function () {
        const indicatorId = this.dataset.id;
        $('html, body')
            .animate(
                {
                    scrollTop: $('#' + indicatorId).offset().top - 100,
                },
                'slow'
            )
            .promise()
            .done(function () {
                $('#' + indicatorId).animateHighlight('rgba(0,0,255,0.2)');
            });
    });

    $('.history_open').click(function () {
        const indicatorId = this.dataset.id;
        const history = window.c3sIndicatorHistory[indicatorId];
        const historyIndex = $('#'+indicatorId+'_history_select').val();
        const item = history[historyIndex];
        const url = item.ecde_url + "/?" + item.request_content_qs + "#detail" ;

        window.open(url, '_blank').focus();
    });

    setTimeout(function () {
        location.reload();
    }, 10 * 60 * 1000);
});

function showHistoryOfIndicator(indicator) {
    $.get(
        '/statistics/history/' + indicator + '/workflow_execution',
        function (data) {
            if (!Array.isArray(data)) return;

            const dataOverview = data.filter((obj) => obj['c3s_indicator_type'] == 'overview');
            const dataDetail = data.filter((obj) => obj['c3s_indicator_type'] == 'detail');

            data = {};
            data[indicatorTypes[0]] = dataOverview;
            data[indicatorTypes[1]] = dataDetail;

            createHistoryChart(indicator, data);
        },
        'json'
    );
}

function createHistoryChart(indicator, data = {}) {
    const ctx = document.getElementById('chart_' + indicator).getContext('2d');

    let chartData = {};

    indicatorTypes.forEach(function (type) {
        chartData[type] = data[type].map((log) => {
            log.request_content = JSON.parse(log.request_content);
            return {
                x: log['input_date'],
                y: Number(log['response_duration']) / 1000,
                feature: log,
            };
        });
    });

    window.c3sIndicatorData[indicator] = {};
    window.c3sIndicatorData[indicator]['chart'] = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Overview response time (seconds)',
                    data: chartData['overview'],
                    backgroundColor: '#CCCCCC',
                    borderColor: '#CCCCCC',
                    borderWidth: 1,
                    pointRadius: 2
                },
                {
                    label: 'Detail response time (seconds)',
                    data: chartData['detail'],
                    backgroundColor: '#0000AA',
                    borderColor: '#0000AA',
                    borderWidth: 1,
                    pointRadius: 2
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    suggestedMax: 900,
                },
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                    },
                    // reverse: true
                },
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }

                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                            }

                            if (context.raw.feature.request_content !== null) {
                                label = [label];
                                label.push(context.raw.feature.c3s_indicator_type);
                                label.push('Configuration:');
                                for (var arg in context.raw.feature.request_content) {
                                    label.push(
                                        arg + ': ' + context.raw.feature.request_content[arg]
                                    );
                                }
                            }

                            return label;
                        },
                    },
                },
            },
        },
    });
}

$(document).ready(function () {
    $.fn.animateHighlight = function (highlightColor, duration) {
        var highlightBg = highlightColor || '#FFFF9C';
        var animateMs = duration || 'slow'; // edit is here
        var originalBg = this.css('background-color');

        if (!originalBg || originalBg == highlightBg) originalBg = '#FFFFFF'; // default to white

        jQuery(this)
            .css('backgroundColor', highlightBg)
            .animate({ backgroundColor: originalBg }, animateMs, null, function () {
                jQuery(this).css('backgroundColor', originalBg);
            });
    };
});
