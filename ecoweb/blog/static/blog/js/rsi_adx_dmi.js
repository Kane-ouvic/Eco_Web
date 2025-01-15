const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const rsi_period = document.getElementById('rsi_period').value;
    const adx_period = document.getElementById('adx_period').value;
    fetch(`${API_BASE_URL}/api/rsi_adx_dmi/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode, startDate: startDate, endDate: endDate, rsi_period: rsi_period, adx_period: adx_period })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    candlestick_data: data.candlestick_data,
                    volume_data: data.volume_data,
                    rsi: data.rsi,
                    adx: data.adx,
                    plus_di: data.plus_di,
                    minus_di: data.minus_di,
                    rsi_signals: data.rsi_signals,
                    adx_signals: data.adx_signals
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
    Highcharts.stockChart('rsi-chart', {
        chart: { type: 'line' },
        title: { text: 'RSI線結果' },
        xAxis: { categories: ['RSI'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
    Highcharts.stockChart('adx-dmi-chart', {
        chart: { type: 'line' },
        title: { text: 'ADX與DMI線結果' },
        xAxis: { categories: ['ADX'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '',
            data: [0],
            type: 'line',
            color: '#000000'
        }]
    });
    // Highcharts.stockChart('dmi-chart', {
    //     chart: { type: 'line' },
    //     title: { text: 'DMI線結果' },
    //     xAxis: { categories: ['DMI'] },
    //     yAxis: { title: { text: '價格範圍' } },
    //     series: [{
    //         name: '',
    //         data: [0],
    //         type: 'line',
    //         color: '#000000'
    //     }]
    // });
}

function renderChart(data) {

    // 繪製RSI圖表
    Highcharts.stockChart('rsi-chart', {
        chart: {
            type: 'line',
            height: 800
        },
        title: { text: 'RSI指標' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '股價' },
            height: '40%'
        }, {
            title: { text: 'RSI值' },
            top: '45%',
            height: '20%',
            offset: 0,
            plotBands: [{
                from: 70,
                to: 100,
                color: 'rgba(255, 0, 0, 0.1)',
                label: { text: '超買區' }
            }, {
                from: 0,
                to: 30,
                color: 'rgba(0, 255, 0, 0.1)',
                label: { text: '超賣區' }
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
            buttonTheme: { width: 60 }
        },
        navigator: {
            enabled: true,
            height: 50
        },
        scrollbar: { enabled: true },
        plotOptions: {
            line: { marker: { enabled: false } }
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
                name: 'RSI',
                data: data.rsi.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#0000FF',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'RSI進出場訊號',
                data: data.rsi_signals.map(signal => ({
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

    // 繪製ADX-DMI圖表
    Highcharts.stockChart('adx-dmi-chart', {
        chart: {
            type: 'line',
            height: 800
        },
        title: { text: 'ADX與DMI指標' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: [{
            title: { text: '股價' },
            height: '40%'
        }, {
            title: { text: 'ADX與DMI值' },
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
            buttonTheme: { width: 60 }
        },
        navigator: {
            enabled: true,
            height: 50
        },
        scrollbar: { enabled: true },
        plotOptions: {
            line: { marker: { enabled: false } }
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
                name: 'ADX',
                data: data.adx.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#0000FF',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: '+DI',
                data: data.plus_di.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#00FF00',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: '-DI',
                data: data.minus_di.map((value, index) => [
                    data.candlestick_data[index][0],
                    value === -2147483648 ? null : value
                ]),
                color: '#FF0000',
                lineWidth: 2,
                yAxis: 1
            },
            {
                name: 'ADX進出場訊號',
                data: data.adx_signals.map(signal => ({
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

    // 繪製DMI圖表
    // Highcharts.stockChart('dmi-chart', {
    //     chart: {
    //         type: 'line',
    //         height: 600
    //     },
    //     title: { text: 'DMI指標' },
    //     xAxis: {
    //         type: 'datetime',
    //         title: { text: '時間' },
    //         ordinal: false
    //     },
    //     yAxis: [{
    //         title: { text: '股價' },
    //         height: '60%'
    //     }, {
    //         title: { text: 'DMI值' },
    //         top: '65%',
    //         height: '35%',
    //         offset: 0
    //     }],
    //     rangeSelector: {
    //         enabled: true,
    //         selected: 4,
    //         inputDateFormat: '%Y-%m-%d',
    //         inputEditDateFormat: '%Y-%m-%d',
    //         buttonTheme: { width: 60 }
    //     },
    //     navigator: {
    //         enabled: true,
    //         height: 50
    //     },
    //     scrollbar: { enabled: true },
    //     plotOptions: {
    //         line: { marker: { enabled: false } }
    //     },
    //     series: [
    //         {
    //             type: 'candlestick',
    //             name: '股價',
    //             data: data.candlestick_data,
    //             yAxis: 0,
    //             color: '#00FF00',
    //             upColor: '#FF0000',
    //             lineColor: '#00FF00',
    //             upLineColor: '#FF0000'
    //         },
    //         {
    //             name: '+DI',
    //             data: data.plus_di.map((value, index) => [
    //                 data.candlestick_data[index][0],
    //                 value === -2147483648 ? null : value
    //             ]),
    //             color: '#FF0000',
    //             lineWidth: 2,
    //             yAxis: 1
    //         },
    //         {
    //             name: '-DI',
    //             data: data.minus_di.map((value, index) => [
    //                 data.candlestick_data[index][0],
    //                 value === -2147483648 ? null : value
    //             ]),
    //             color: '#00FF00',
    //             lineWidth: 2,
    //             yAxis: 1
    //         }
    //     ]
    // });

}
