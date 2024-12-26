const API_BASE_URL = 'http://web.nightcover.com.tw:55556';

document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

// document.getElementById('search-button').addEventListener('click', function () {
//     const stockCode = document.getElementById('stockCode').value;
//     const year = document.getElementById('year').value;
//     // 模擬API回傳資料
//     const data = {
//         latest_price: 1037.5,
//         methods: [
//             { name: '股利法', cheap: 200, fair: 400, expensive: 600 },
//             { name: '高低價法', cheap: 250, fair: 450, expensive: 650 },
//             { name: '本淨比法', cheap: 300, fair: 500, expensive: 700 },
//             { name: '本益比法', cheap: 350, fair: 550, expensive: 750 }
//         ]
//     };
//     renderChart(data);
// });

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const year = document.getElementById('year').value;

    fetch(`${API_BASE_URL}/api/stock_pricing/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({ stockCode: stockCode, year: year })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const chartData = {
                    latest_price: data.latest_price, // 這裡需要從API獲取最新價格
                    methods: data.pricing_data
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
        xAxis: { categories: ['股利法', '高低價法', '本淨比法', '本益比法'] },
        yAxis: { title: { text: '價格範圍' } },
        series: [{
            name: '最新價格',
            data: [0, 0, 0, 0],
            type: 'line',
            color: '#000000'
        }]
    });
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
                name: '昂貴價',
                data: data.methods.map(m => m.expensive),
                color: '#FF0000'
            }
            , {
                name: '合理價到昂貴價',
                data: data.methods.map(m => m.fair_expensive),
                color: '#FFC0CB'
            }, {
                name: '合理價',
                data: data.methods.map(m => m.fair),
                color: '#00FF00'
            }
            , {
                name: '便宜價',
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
}