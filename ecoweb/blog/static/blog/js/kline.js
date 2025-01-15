const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    fetch(`${API_BASE_URL}/api/kline/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode, startDate: startDate, endDate: endDate })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    candlestick_data: data.candlestick_data,
                    volume_data: data.volume_data,
                    kline_patterns: data.kline_patterns
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
    Highcharts.chart('kline-chart', {
        chart: { type: 'line' },
        title: { text: 'K線型態' },
        xAxis: { categories: ['K線型態'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '最新價格',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
}

function renderChart(data) {
    Highcharts.stockChart('kline-chart', {
        chart: {
            type: 'line',
            height: 800
        },
        title: { text: 'K線型態' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '價格' },
            height: '40%',
            plotLines: [{
                value: 15,
                width: 1,
                color: '#808080'
            }]
        }, {
            title: { text: '漲跌幅度' },
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
            },
            scatter: {
                marker: {
                    symbol: 'triangle',
                    radius: 5
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
                type: 'column',
                name: '漲跌幅',
                data: data.candlestick_data.map((value, index, arr) => {
                    if (index === 0) return [value[0], 0];
                    const prevClose = arr[index - 1][4];
                    const currClose = value[4];
                    return [value[0], ((currClose - prevClose) / prevClose) * 100];
                }),
                yAxis: 1
            },
            {
                name: 'K線型態',
                data: data.kline_patterns.map(pattern => ({
                    x: pattern[0],
                    y: pattern[1],
                    pattern: pattern[2],
                    additionalInfo: pattern[3],
                    marker: {
                        symbol: pattern[2] === 'bullish' ? 'triangle' : (pattern[2] === 'bearish' ? 'triangle-down' : 'circle'),
                        fillColor: pattern[2] === 'bullish' ? '#00FF00' : (pattern[2] === 'bearish' ? '#FF0000' : '#0000FF')
                    }
                })),
                tooltip: {
                    pointFormat: '型態: {point.pattern}<br/>時間: {point.additionalInfo}<br/>價格: {point.y}'
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
}
