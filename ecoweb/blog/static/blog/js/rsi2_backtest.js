$(document).ready(function () {
    $('#backtest-form').on('submit', function (e) {
        e.preventDefault();
        console.log("表單提交");
        $.ajax({
            url: '/rsi-backtest/',
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            success: function (response) {
                console.log("收到回應:", response);
                if (response && response.trades && response.equity_curve && response.drawdowns && response.dates) {
                    $('#backtest-results').show();
                    updateTradeTable(response.trades);
                    updateReturnMDDChart(response.equity_curve, response.drawdowns, response.dates);
                    updatePriceRSIChart(response.price_data, response.rsi1, response.rsi2, response.dates);
                    updatePerformanceMetrics(response.performance);
                } else {
                    console.error("回測數據不完整:", response);
                    alert("回測數據不完整，請檢查後端返回的數據。");
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX 請求失敗:", status, error);
                console.error("回應內容:", xhr.responseText);
                alert("回測執行失敗，請檢查控制台以獲取更多信息。");
            }
        });
    });
});

function updateTradeTable(trades) {
    $('#trade-table').DataTable({
        data: trades,
        columns: [
            { data: 'entry_time', title: '進場時間' },
            { data: 'entry_price', title: '進場價格' },
            { data: 'exit_time', title: '出場時間' },
            { data: 'exit_price', title: '出場價格' },
            { data: 'returns', title: '報酬率', render: function (data) { return (data * 100).toFixed(2) + '%'; } }
        ],
        destroy: true
    });
}

function updateReturnMDDChart(equityCurve, drawdowns, dates) {
    Highcharts.stockChart('return-mdd-chart', {
        rangeSelector: { selected: 1 },
        title: { text: '報酬率 & MDD 走勢圖' },
        yAxis: [{
            title: { text: '報酬率' },
            height: '60%'
        }, {
            title: { text: 'MDD' },
            top: '65%',
            height: '35%',
            offset: 0
        }],
        series: [{
            name: '報酬率',
            data: equityCurve.map((value, index) => [Date.parse(dates[index]), value]),
            type: 'line'
        }, {
            name: 'MDD',
            data: drawdowns.map((value, index) => [Date.parse(dates[index]), value * 100]),
            yAxis: 1,
            type: 'line'
        }]
    });
}

function updatePriceRSIChart(priceData, rsi1, rsi2, dates) {
    Highcharts.stockChart('price-rsi-chart', {
        rangeSelector: { selected: 1 },
        title: { text: '股價走勢圖 & RSI 指標' },
        yAxis: [{
            title: { text: '價格' },
            height: '60%'
        }, {
            title: { text: 'RSI' },
            top: '65%',
            height: '35%',
            offset: 0
        }],
        series: [{
            name: '價格',
            data: priceData.map((value, index) => [Date.parse(dates[index]), value]),
            type: 'line'
        }, {
            name: '短期RSI',
            data: rsi1.map((value, index) => [Date.parse(dates[index]), value]),
            yAxis: 1,
            type: 'line'
        }, {
            name: '長期RSI',
            data: rsi2.map((value, index) => [Date.parse(dates[index]), value]),
            yAxis: 1,
            type: 'line'
        }]
    });
}

function updatePerformanceMetrics(performance) {

    $('#total-return').text(performance.total_return + '%');
    $('#avg-return').text(performance.avg_return + '%');
    $('#win-rate').text(performance.win_rate + '%');
    $('#avg-profit').text(performance.avg_profit + '%');
    $('#avg-loss').text(performance.avg_loss + '%');
    $('#profit-loss-ratio').text(performance.profit_loss_ratio);
    $('#expectancy').text(performance.expectancy + '%');
    // $('#max-drawdown').text(performance.max_drawdown + '%');
    $('#profitable-hold-days').text(performance.profitable_hold_days);
    $('#loss-hold-days').text(performance.loss_hold_days);
    $('#max-consecutive-loss').text(performance.max_consecutive_loss + '%');
    $('#max-consecutive-profit').text(performance.max_consecutive_profit + '%');
}