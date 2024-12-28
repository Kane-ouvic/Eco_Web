const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    // 模擬API回傳資料
    // const data = {
    //     latest_price: 1037.5,
    //     methods: [
    //         { name: '本益比河流圖', cheap: 200, fair: 400, expensive: 600 }
    //     ]
    // };
    // renderChart(data);
    fetch(`${API_BASE_URL}/api/pe_ratio_chart/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    latest_price: data.latest_price, // 這裡需要從API獲取最新價格
                    methods: data.pricing_data,
                    dates: data.dates,
                    pe_lines: data.pe_lines,
                    candlestick_data: data.candlestick_data
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
    Highcharts.chart('pe-ratio-chart', {
        chart: { type: 'bar' },
        title: { text: '本益比河流圖結果' },
        xAxis: { categories: ['本益比河流圖'] },
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
    document.getElementById('latest-price').innerHTML = `<h4>最新價格: ${data.latest_price}</h4>`;
    Highcharts.chart('pe-ratio-chart', {
        chart: { type: 'bar' },
        title: { text: '本益比河流圖結果' },
        xAxis: { categories: data.methods.map(m => m.name) },
        yAxis: { title: { text: '價格範圍' } },
        plotOptions: {
            series: {
                stacking: 'normal', // 堆疊模式
                dataLabels: {
                    enabled: false   // 顯示數值標籤
                }
            }
        },
        series: [
            {
                name: '昂貴價區間',
                data: data.methods.map(m => m.expensive),
                color: '#FF0000'
            }
            , {
                name: '合理價到昂貴價區間',
                data: data.methods.map(m => m.fair_expensive),
                color: '#FFC0CB'
            }, {
                name: '便宜到合理價區間',
                data: data.methods.map(m => m.fair),
                color: '#00FF00'
            }
            , {
                name: '便宜價區間',
                data: data.methods.map(m => m.cheap),
                color: '#FFFF00'
            },
            {
                name: '最新價格',
                data: data.methods.map(() => data.latest_price),
                type: 'line',
                color: '#000000'
            }]
    });
    Highcharts.stockChart('pe-ratio-chart-2', {
        chart: {
            type: 'line',
            height: 600 // 增加圖表高度
        },
        title: { text: '本益比河流圖' },
        xAxis: {
            type: 'datetime',
            title: { text: '時間' },
            ordinal: false
        },
        yAxis: {
            title: { text: '價格' },
            height: '75%', // 增加y軸高度比例
            plotLines: [{
                value: 15, // 設定中間值
                width: 1,
                color: '#808080'
            }]
        },
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
            height: 50 // 調整導航列高度
        },
        scrollbar: {
            enabled: true
        },
        plotOptions: {
            candlestick: {
                lineWidth: 2, // 加粗K線
                color: '#00FF00',
                upColor: '#FF0000',
                lineColor: '#00FF00',
                upLineColor: '#FF0000'
            },
            area: {
                fillOpacity: 0.4, // 設定區域填充透明度
                lineWidth: 1,
                marker: {
                    enabled: false
                },
                color: 'rgba(124, 181, 236, 0.5)' // 設定預設顏色
            }
        },
        series: [
            // 先繪製區域
            ...Object.keys(data.pe_lines).slice(0, -1).map((multiplier, index) => ({
                type: 'area',
                name: `區間 ${multiplier}-${Object.keys(data.pe_lines)[index + 1]}`,
                data: data.dates.map((date, i) => [
                    new Date(date).getTime(),
                    data.pe_lines[multiplier][i],
                    data.pe_lines[Object.keys(data.pe_lines)[index + 1]][i]
                ]),
                fillColor: `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.2)`,
            })),
            // 再繪製線段
            ...Object.keys(data.pe_lines).map(multiplier => ({
                name: `EPS * ${multiplier}`,
                data: data.pe_lines[multiplier].map((value, index) => [
                    new Date(data.dates[index]).getTime(),
                    value
                ]),
                type: 'line',
                lineWidth: 1 // 讓其他線條較細
            })),
            {
                type: 'candlestick',
                name: '股價',
                data: data.candlestick_data,
                color: '#00FF00',
                upColor: '#FF0000',
                lineColor: '#00FF00',
                upLineColor: '#FF0000'
            }
        ]
    });
    // Highcharts.chart('pe-ratio-chart-2', {
    //     chart: {
    //         type: 'arearange'
    //     },
    //     title: {
    //         text: '本益比河流圖'
    //     },
    //     xAxis: {
    //         categories: data.methods.map(m => m.name)
    //     },
    //     yAxis: {
    //         title: {
    //             text: '價格範圍'
    //         }
    //     },
    //     plotOptions: {
    //         arearange: {
    //             fillOpacity: 0.3,
    //             lineWidth: 0
    //         }
    //     },
    //     series: [{
    //         name: '便宜區間',
    //         data: data.methods.map(m => [0, m.cheap]),
    //         color: '#FFFF00'
    //     }, {
    //         name: '合理區間',
    //         data: data.methods.map(m => [m.cheap, m.cheap + m.fair]),
    //         color: '#00FF00'
    //     }, {
    //         name: '昂貴區間',
    //         data: data.methods.map(m => [m.cheap + m.fair, m.cheap + m.fair + m.expensive]),
    //         color: '#FF0000'
    //     }, {
    //         name: '最新價格',
    //         type: 'line',
    //         data: data.methods.map(() => data.latest_price),
    //         color: '#000000',
    //         lineWidth: 2
    //     }]
    // });
}
