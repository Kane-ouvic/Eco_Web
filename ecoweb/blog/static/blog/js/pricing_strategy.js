const API_BASE_URL = 'http://web.nightcover.com.tw:55556';

document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    fetch(`${API_BASE_URL}/api/pricing_strategy/`, {
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
                    latest_price: data.latest_price, // 這裡需要從API獲取最新價格
                    methods: data.pricing_data,
                    date: data.date,
                    heatmap_data: data.heatmap_data,
                    div_expensive: data.div_expensive,
                    hl_expensive: data.hl_expensive,
                    pb_expensive: data.pb_expensive,
                    pe_expensive: data.pe_expensive
                };
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
    Highcharts.chart('stock-pricing-chart', {
        chart: { type: 'bar' },
        title: { text: '股票定價結果' },
        xAxis: { categories: ['股利法', '高低價法', '本淨比法', '本益比法', '本益比河流圖'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '最新價格',
            data: [0, 0, 0, 0],
            type: 'line',
            color: '#000000'
        }]
    });

    // Highcharts.chart('heatmap', {

    //     chart: {
    //         type: 'heatmap',
    //         marginTop: 40,
    //         marginBottom: 80,
    //         plotBorderWidth: 1
    //     },

    //     title: {
    //         text: 'Sales per employee per weekday',
    //         style: {
    //             fontSize: '1em'
    //         }
    //     },

    //     xAxis: {
    //         categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    //         title: null,
    //         reversed: false
    //     },

    //     yAxis: {
    //         categories: ['股利法', '高低價法', '本淨比法', '本益比法', '本益比河流圖']
    //     },

    //     accessibility: {
    //         point: {
    //             descriptionFormat: '{(add index 1)}. ' +
    //                 '{series.yAxis.categories.(y)} sales ' +
    //                 '{series.xAxis.categories.(x)}, {value}.'
    //         }
    //     },

    //     colorAxis: [{
    //         min: 0,
    //         max: 50,
    //         stops: [
    //             [0, '#FFFFFF'], // 白色
    //             [0.5, '#FFFF00'], // 黃色
    //             [1, '#FF0000']   // 紅色
    //         ]
    //     }, {
    //         min: 50,
    //         max: 100,
    //         stops: [
    //             [0, '#FFFFFF'], // 白色
    //             [0.5, '#00FF00'], // 綠色
    //             [1, '#0000FF']   // 藍色
    //         ]
    //     }],

    //     legend: {
    //         align: 'right',
    //         layout: 'vertical',
    //         margin: 0,
    //         verticalAlign: 'top',
    //         y: 25,
    //         symbolHeight: 280
    //     },

    //     tooltip: {
    //         format: '<b>{series.yAxis.categories.(point.y)}</b> sold<br>' +
    //             '<b>{point.value}</b> items on <br>' +
    //             '<b>{series.xAxis.categories.(point.x)}</b>'
    //     },

    //     series: [{
    //         name: 'Sales per employee',
    //         borderWidth: 1,
    //         data: [
    //             [0, 0, 10], [1, 0, 19], [2, 0, 8], [3, 0, 24], [4, 0, 67], [5, 0, 10], [6, 0, 10],
    //             [0, 1, 92], [1, 1, 58], [2, 1, 78], [3, 1, 117], [4, 1, 48], [5, 1, 10], [6, 1, 10],
    //             [0, 2, 35], [1, 2, 15], [2, 2, 123], [3, 2, 64], [4, 2, 52], [5, 2, 10], [6, 2, 10],
    //             [0, 3, 72], [1, 3, 132], [2, 3, 114], [3, 3, 19], [4, 3, 16], [5, 3, 10], [6, 3, 10],
    //             [0, 4, 38], [1, 4, 5], [2, 4, 8], [3, 4, 117], [4, 4, 115], [5, 4, 10], [6, 4, 10],
    //         ],
    //         dataLabels: {
    //             enabled: true,
    //             color: '#000000'
    //         },
    //         colorAxis: 0
    //     }],

    //     responsive: {
    //         rules: [{
    //             condition: {
    //                 maxWidth: 500
    //             },
    //             chartOptions: {
    //                 xAxis: {
    //                     labels: {
    //                         format: '{substr value 0 1}'
    //                     }
    //                 }
    //             }
    //         }]
    //     }

    // });

    // Highcharts.chart('heatmap1', {

    //     chart: {
    //         type: 'heatmap',
    //         marginTop: 40,
    //         marginBottom: 80,
    //         plotBorderWidth: 4
    //     },

    //     title: {
    //         text: '',
    //     },

    //     xAxis: {
    //         categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    //         title: null,
    //         reversed: false,
    //         visible: true
    //     },

    //     yAxis: {
    //         categories: ['股利法']
    //     },


    //     colorAxis: [{
    //         min: 0,
    //         max: 100,
    //         stops: [
    //             [0, '#FFFFFF'], // 白色
    //             [0.5, '#FFFF00'], // 黃色
    //             [1, '#FF0000']   // 紅色
    //         ]
    //     }],

    //     legend: {
    //         align: 'right',
    //         layout: 'vertical',
    //         margin: 0,
    //         verticalAlign: 'top',
    //         y: 10,
    //         symbolHeight: 200,
    //         visible: false
    //     },

    //     tooltip: {
    //         format: '<b>{series.yAxis.categories.(point.y)}</b> sold<br>' +
    //             '<b>{point.value}</b> items on <br>' +
    //             '<b>{series.xAxis.categories.(point.x)}</b>'
    //     },

    //     series: [{
    //         name: 'Sales per employee',
    //         borderWidth: 1,
    //         data: [
    //             [0, 0, 10], [1, 0, 19], [2, 0, 8], [3, 0, 24], [4, 0, 67], [5, 0, 10], [6, 0, 10],
    //         ],
    //         dataLabels: {
    //             enabled: true,
    //             color: '#000000'
    //         },
    //         colorAxis: 0
    //     }],


    // });

    // Highcharts.chart('heatmap2', {

    //     chart: {
    //         type: 'heatmap',
    //         marginTop: 40,
    //         marginBottom: 80,
    //         plotBorderWidth: 1
    //     },

    //     title: {
    //         text: '',
    //     },

    //     xAxis: {
    //         categories: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    //         title: null,
    //         reversed: false,
    //         visible: true
    //     },

    //     yAxis: {
    //         categories: ['股利法']
    //     },


    //     colorAxis: [{
    //         min: 0,
    //         max: 100,
    //         stops: [
    //             [0, '#FFFFFF'], // 白色
    //             [0.5, '#FFFF00'], // 黃色
    //             [1, '#FF0000']   // 紅色
    //         ]
    //     }],

    //     legend: {
    //         align: 'right',
    //         layout: 'vertical',
    //         margin: 0,
    //         verticalAlign: 'top',
    //         y: 10,
    //         symbolHeight: 200,
    //         visible: false
    //     },

    //     tooltip: {
    //         format: '<b>{series.yAxis.categories.(point.y)}</b> sold<br>' +
    //             '<b>{point.value}</b> items on <br>' +
    //             '<b>{series.xAxis.categories.(point.x)}</b>'
    //     },

    //     series: [{
    //         name: 'Sales per employee',
    //         borderWidth: 1,
    //         data: [
    //             [0, 0, 10], [1, 0, 19], [2, 0, 8], [3, 0, 24], [4, 0, 67], [5, 0, 10], [6, 0, 10],
    //         ],
    //         dataLabels: {
    //             enabled: true,
    //             color: '#000000'
    //         },
    //         colorAxis: 0
    //     }],


    // });
}

function renderChart(data) {
    document.getElementById('latest-price').innerHTML = `<h4>最新價格: ${data.latest_price}</h4>`;
    Highcharts.chart('stock-pricing-chart', {
        chart: { type: 'bar' },
        title: { text: '股票定價結果' },
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

    function renderHeatmap(containerId, category, expensive, heatmap_data, visible) {
        Highcharts.chart(containerId, {
            chart: {
                type: 'heatmap',
                marginTop: 20,
                marginBottom: 30,
                plotBorderWidth: 4
            },
            title: {
                text: '',
            },
            xAxis: {
                categories: data.date,
                title: null,
                reversed: false,
                visible: visible

            },
            yAxis: {
                categories: [category]
            },
            colorAxis: [{
                min: 0,
                max: expensive,
                stops: [
                    [0, '#FFFFFF'], // 白色
                    [0.5, '#FFFF00'], // 黃色
                    [1, '#FF0000']   // 紅色
                ],
                visible: false
            }],
            // legend: {
            //     align: 'right',
            //     layout: 'vertical',
            //     margin: 0,
            //     verticalAlign: 'top',
            //     y: 10,
            //     symbolHeight: 200,
            //     visible: false
            // },
            // tooltip: {
            //     format: '<b>{series.yAxis.categories.(point.y)}</b> sold<br>' +
            //         '<b>{point.value}</b> items on <br>' +
            //         '<b>{series.xAxis.categories.(point.x)}</b>'
            // },
            series: [{
                tooltip: {
                    headerFormat: '',
                    pointFormat: '{point.x}, {point.y}: {point.value}'
                },
                borderWidth: 1,
                data: heatmap_data,
                dataLabels: {
                    enabled: true,
                    color: '#000000'
                },
                colorAxis: 0
            }],
        });
    }

    // 使用範例
    renderHeatmap('heatmap1', '股利法', data.div_expensive, data.heatmap_data, false);
    renderHeatmap('heatmap2', '高低價法', data.hl_expensive, data.heatmap_data, false);
    renderHeatmap('heatmap3', '本淨比法', data.pb_expensive, data.heatmap_data, false);
    renderHeatmap('heatmap4', '本益比法', data.pe_expensive, data.heatmap_data, true);



}