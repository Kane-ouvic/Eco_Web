const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const fastk_period = document.getElementById('fastk_period').value;
    const slowk_period = document.getElementById('slowk_period').value;
    const slowd_period = document.getElementById('slowd_period').value;
    const fastperiod = document.getElementById('fastperiod').value;
    const slowperiod = document.getElementById('slowperiod').value;
    const signalperiod = document.getElementById('signalperiod').value;
    const timeperiod = document.getElementById('timeperiod').value;
    const nbdevup = document.getElementById('nbdevup').value;
    const nbdevdn = document.getElementById('nbdevdn').value;
    fetch(`${API_BASE_URL}/api/kd_macd_bool/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode, startDate: startDate, endDate: endDate, fastk_period: fastk_period, slowk_period: slowk_period, slowd_period: slowd_period, fastperiod: fastperiod, slowperiod: slowperiod, signalperiod: signalperiod, timeperiod: timeperiod, nbdevup: nbdevup, nbdevdn: nbdevdn })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    ma: data.ma,
                    candlestick_data: data.candlestick_data,
                    volume_data: data.volume_data,
                    kd_K: data.kd_K,
                    kd_D: data.kd_D,
                    macd_data: data.macd_data,
                    macd_signal: data.macd_signal,
                    macd_hist: data.macd_hist,
                    bool_mid: data.bool_mid,
                    bool_upper: data.bool_upper,
                    bool_lower: data.bool_lower,
                    kd_signals: data.kd_signals,
                    macd_signals: data.macd_signals,
                    bool_signals: data.bool_signals
                };
                console.log(chartData);
                renderChart(chartData);
            } else {
                console.error('API回傳錯誤:', data.error);
            }
        })
        .catch(error => {
            console.error('請求錯誤:', error);
            alert('獲取數據時發生錯誤，請稍後再試');
        });
});

function renderInitialChart() {
    Highcharts.stockChart('kd-chart', {
        chart: { type: 'line' },
        title: { text: 'KD線結果' },
        xAxis: { categories: ['KD'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
    Highcharts.stockChart('macd-chart', {
        chart: { type: 'line' },
        title: { text: 'MACD線結果' },
        xAxis: { categories: ['MACD'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
    Highcharts.stockChart('bool-chart', {
        chart: { type: 'line' },
        title: { text: '布林通道結果' },
        xAxis: { categories: ['布林通道'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
}

function renderChart(data) {
    // 繪製KD圖
    Highcharts.stockChart('kd-chart', {
        chart: {
            type: 'line',
            height: 800
        },
        title: { text: 'KD線' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '股價' },
            height: '40%'
        }, {
            title: { text: 'KD值' },
            top: '45%',
            height: '20%',
            offset: 0,
            plotBands: [{
                from: 80,
                to: 100,
                color: 'rgba(255, 0, 0, 0.1)',
                label: {
                    text: '超買區'
                }
            }, {
                from: 0,
                to: 20,
                color: 'rgba(0, 255, 0, 0.1)',
                label: {
                    text: '超賣區'
                }
            }],
            plotLines: [{
                value: 80,
                width: 2,
                color: '#FF0000',
                dashStyle: 'dash'
            }, {
                value: 20,
                width: 2,
                color: '#00FF00',
                dashStyle: 'dash'
            }]
        },
        {
            title: { text: '成交量' },
            top: '70%',
            height: '30%',
            offset: 0
        }],
        rangeSelector: {
            enabled: true,
            selected: 4,
            inputDateFormat: '%Y-%m-%d',
            inputEditDateFormat: '%Y-%m-%d',
            buttonTheme: {
                width: 60
            }
        },
        navigator: {
            enabled: true,
            height: 50
        },
        scrollbar: {
            enabled: true
        },
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            }
        },
        series: [
            {
                type: 'candlestick',
                name: '股價',
                data: data.candlestick_data,
                yAxis: 0,
                color: '#00FF00',
                upColor: '#FF0000',
                lineColor: '#00FF00',
                upLineColor: '#FF0000'
            },
            {
                name: 'K值',
                data: data.kd_K.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#FF0000',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'D值',
                data: data.kd_D.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#00FF00',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'KD進出場訊號',
                data: data.kd_signals.map(signal => ({
                    x: signal[0],
                    y: signal[1],
                    action: signal[2],
                    additionalInfo: signal[3],
                    marker: {
                        symbol: signal[2] === 'buy' ? 'triangle' : 'triangle-down',
                        fillColor: signal[2] === 'buy' ? '#000000' : '#000000'
                    }
                })),
                tooltip: {
                    pointFormat: 'action: {point.action}<br/>時間: {point.additionalInfo}<br/>價格: {point.y}'
                },
                type: 'scatter'
            },
            {
                type: 'column',
                name: '成交量',
                data: data.volume_data,
                yAxis: 2,
                color: '#888888'
            }
        ]
    });

    // 繪製MACD圖表
    Highcharts.stockChart('macd-chart', {
        chart: {
            type: 'line',
            height: 800
        },
        title: {
            text: 'MACD指標'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: '時間'
            },
            ordinal: false
        },
        yAxis: [{
            title: {
                text: '股價'
            },
            height: '40%'
        }, {
            title: {
                text: 'MACD'
            },
            top: '45%',
            height: '20%',
            offset: 0
        }, {
            title: { text: '成交量' },
            top: '70%',
            height: '30%',
            offset: 0
        }],
        rangeSelector: {
            enabled: true,
            selected: 4,
            inputDateFormat: '%Y-%m-%d',
            inputEditDateFormat: '%Y-%m-%d',
            buttonTheme: {
                width: 60
            }
        },
        navigator: {
            enabled: true,
            height: 50
        },
        scrollbar: {
            enabled: true
        },
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            },
            column: {
                negativeColor: '#00FF00',
                color: '#FF0000'
            }
        },
        series: [
            {
                type: 'candlestick',
                name: '股價',
                data: data.candlestick_data,
                yAxis: 0,
                color: '#00FF00',
                upColor: '#FF0000',
                lineColor: '#00FF00',
                upLineColor: '#FF0000'
            },
            {
                name: 'MACD',
                data: data.macd_data.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#0000FF',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'Signal',
                data: data.macd_signal.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#FF0000',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'Histogram',
                type: 'column',
                data: data.macd_hist.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                yAxis: 1
            },
            {
                name: 'MACD進出場訊號',
                data: data.macd_signals.map(signal => ({
                    x: signal[0],
                    y: signal[1],
                    action: signal[2],
                    additionalInfo: signal[3],
                    marker: {
                        symbol: signal[2] === 'buy' ? 'triangle' : 'triangle-down',
                        fillColor: signal[2] === 'buy' ? '#000000' : '#000000'
                    }
                })),
                tooltip: {
                    pointFormat: 'action: {point.action}<br/>時間: {point.additionalInfo}<br/>價格: {point.y}'
                },
                type: 'scatter'
            },
            {
                type: 'column',
                name: '成交量',
                data: data.volume_data,
                yAxis: 2,
                color: '#888888'
            }
        ]
    });

    // 繪製布林通道圖
    Highcharts.stockChart('bool-chart', {
        chart: {
            type: 'line',
            height: 600
        },
        title: { text: '布林通道' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '價格' },
            height: '70%',
            plotLines: [{
                value: 15,
                width: 1,
                color: '#808080'
            }]
        }, {
            title: { text: '成交量' },
            top: '70%',
            height: '30%',
            offset: 0
        }],
        rangeSelector: {
            enabled: true,
            selected: 4,
            inputDateFormat: '%Y-%m-%d',
            inputEditDateFormat: '%Y-%m-%d',
            buttonTheme: {
                width: 60
            }
        },
        navigator: {
            enabled: true,
            height: 50
        },
        scrollbar: {
            enabled: true
        },
        plotOptions: {
            line: {
                marker: {
                    enabled: false
                }
            }
        },
        series: [
            {
                type: 'candlestick',
                name: '股價',
                data: data.candlestick_data,
                color: '#00FF00',
                upColor: '#FF0000',
                lineColor: '#00FF00',
                upLineColor: '#FF0000'
            },
            {
                name: '中線',
                data: data.bool_mid.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#000000',
                lineWidth: 2
            },
            {
                name: '上軌',
                data: data.bool_upper.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#0000FF',
                lineWidth: 1
            },
            {
                name: '下軌',
                data: data.bool_lower.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#FF0000',
                lineWidth: 1
            },
            {
                name: '布林通道進出場訊號',
                data: data.bool_signals.map(signal => ({
                    x: signal[0],
                    y: signal[1],
                    action: signal[2],
                    additionalInfo: signal[3],
                    marker: {
                        symbol: signal[2] === 'buy' ? 'triangle' : 'triangle-down',
                        fillColor: signal[2] === 'buy' ? '#000000' : '#000000'
                    }
                })),
                tooltip: {
                    pointFormat: 'action: {point.action}<br/>時間: {point.additionalInfo}<br/>價格: {point.y}'
                },
                type: 'scatter'
            },
            {
                type: 'column',
                name: '成交量',
                data: data.volume_data,
                yAxis: 1,
                color: '#888888'
            }
        ]
    });
}
