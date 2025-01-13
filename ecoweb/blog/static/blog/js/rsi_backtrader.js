const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
document.addEventListener('DOMContentLoaded', function () {
    renderInitialChart();
});

document.getElementById('search-button').addEventListener('click', function () {
    const stockCode = document.getElementById('stockCode').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const short_rsi = document.getElementById('rsi_short_period').value;
    const long_rsi = document.getElementById('rsi_long_period').value;
    const rsi_upper = document.getElementById('rsi_upper').value;
    const rsi_lower = document.getElementById('rsi_lower').value;
    const stake = document.getElementById('stake').value;
    const initial_cash = document.getElementById('initial_cash').value;
    const commission = document.getElementById('commission').value;
    fetch(`${API_BASE_URL}/api/rsi_backtrader/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'  // 確保Django的CSRF保護
        },
        body: JSON.stringify({
            stockCode: stockCode,
            startDate: startDate,
            endDate: endDate,
            short_rsi: short_rsi,
            long_rsi: long_rsi,
            rsi_upper: rsi_upper,
            rsi_lower: rsi_lower,
            stake: stake,
            initial_cash: initial_cash,
            commission: commission
        })
    })
        .then(response => response.blob())
        .then(imageBlob => {
            console.log(imageBlob);
            const imageUrl = URL.createObjectURL(imageBlob);
            const imgElement = document.getElementById('backtest-result');
            imgElement.src = imageUrl;
            imgElement.style.display = 'block';
        })
        .catch(error => {
            console.error('請求錯誤:', error);
            alert('獲取數據時發生錯誤，請稍後再試');
        });
});

function renderInitialChart() {
    const imgElement = document.getElementById('backtest-result');
    imgElement.style.display = 'none';
}

function renderChart(data) {
    // 此函數目前不需要實作，因為回傳的數據是圖片
}
