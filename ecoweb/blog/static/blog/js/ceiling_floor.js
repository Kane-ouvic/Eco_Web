const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const maLength = document.getElementById('maLength').value;
    const maType = document.getElementById('maType').value;
    const method = document.getElementById('method').value;
    fetch(`${API_BASE_URL}/api/ceiling_floor/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode, startDate: startDate, maLength: maLength, maType: maType, method: method })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    ma: data.ma,
                    ceiling_price: data.ceiling_price,
                    floor_price: data.floor_price,
                    candlestick_data: data.candlestick_data,
                    ceiling_signals: data.ceiling_signals,
                    floor_signals: data.floor_signals
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
    Highcharts.chart('ceiling_floor-chart', {
        chart: { type: 'line' },
        title: { text: '天花板地板線結果' },
        xAxis: { categories: ['天花板地板線'] },
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
    Highcharts.stockChart('ceiling_floor-chart', {
        chart: {
            type: 'line',
            height: 600
        },
        title: { text: '天花板地板線' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '價格' },
            height: '60%',
            plotLines: [{
                value: 15,
                width: 1,
                color: '#808080'
            }]
        }, {
            title: { text: '漲跌幅度' },
            top: '65%',
            height: '35%',
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
                name: '移動平均線',
                data: data.ma.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#000000',
                lineWidth: 2
            },
            {
                name: '天花板線',
                data: data.ceiling_price.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#0000FF',
                lineWidth: 1
            },
            {
                name: '地板線',
                data: data.floor_price.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#FF0000',
                lineWidth: 1
            },
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
                name: '突破天花板訊號',
                type: 'scatter',
                data: data.ceiling_signals,
                color: '#000000',
                marker: {
                    symbol: 'triangle-down'
                }
            },
            {
                name: '突破地板訊號',
                type: 'scatter',
                data: data.floor_signals,
                color: '#000000',
                marker: {
                    symbol: 'triangle'
                }
            }
        ]
    });
}
