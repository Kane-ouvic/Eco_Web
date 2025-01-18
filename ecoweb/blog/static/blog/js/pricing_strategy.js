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