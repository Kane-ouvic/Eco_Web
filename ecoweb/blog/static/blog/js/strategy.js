$('#strategy-form').on('submit', function (event) {
    event.preventDefault(); // Prevent default form submission

    $.ajax({
        url: '/api/calculate_strategy/',  // Submit to your Django backend URL
        type: 'POST',
        data: $(this).serialize(),
        headers: { 'X-CSRFToken': csrfToken },
        success: function (response) {
            console.log(response); // Check if the returned data is correct

            // 準備數據，將 NaN 轉換為 null
            function prepareData(dates, values) {
                return dates.map((timestamp, index) => [timestamp, (values[index] === -2147483648) ? null : values[index]]);
            }

            let stock1Data = prepareData(response.dates, response.stock1_prices);
            let stock2Data = prepareData(response.dates, response.stock2_prices);
            let spreadData = prepareData(response.dates, response.spread);
            let rollingMeanData = prepareData(response.dates, response.rolling_mean);
            let upperBandData = prepareData(response.dates, response.upper_band);
            let lowerBandData = prepareData(response.dates, response.lower_band);
            let profitAndLossData = prepareData(response.dates, response.profit_and_loss);

            console.log(stock1Data);
            console.log(stock2Data);
            console.log(spreadData);
            console.log(rollingMeanData);
            console.log(upperBandData);
            console.log(lowerBandData);
            console.log(profitAndLossData);

            // Prepare signals for marking
            let buyAAPLSignals = response.signals.filter(signal => signal.action_aapl === 'BUY').map(signal => [new Date(signal.date).getTime(), signal.price_aapl]);
            let sellAAPLSignals = response.signals.filter(signal => signal.action_aapl === 'SELL').map(signal => [new Date(signal.date).getTime(), signal.price_aapl]);

            let buyGLDSignals = response.signals.filter(signal => signal.action_gld === 'BUY').map(signal => [new Date(signal.date).getTime(), signal.price_gld]);
            let sellGLDSignals = response.signals.filter(signal => signal.action_gld === 'SELL').map(signal => [new Date(signal.date).getTime(), signal.price_gld]);

            let openSignals = response.signals.filter(signal => signal.type === 'OPEN').map(signal => [new Date(signal.date).getTime(), signal.profit_loss]);
            let closeSignals = response.signals.filter(signal => signal.type === 'CLOSE').map(signal => [new Date(signal.date).getTime(), signal.profit_loss]);
            // Plot Price & Spread chart with signals
            Highcharts.stockChart('price-chart', {
                title: { text: 'Price & Spread' },
                xAxis: {
                    type: 'datetime',
                    ordinal: false
                },
                yAxis: { title: { text: 'Price' } },
                series: [{
                    name: response.stock1,
                    data: stock1Data,
                    connectNulls: false
                }, {
                    name: response.stock2,
                    data: stock2Data,
                    connectNulls: false
                }, {
                    name: 'AAPL Buy Signals',
                    type: 'scatter',
                    data: buyAAPLSignals,
                    marker: {
                        symbol: 'triangle',
                        fillColor: 'green'
                    }
                }, {
                    name: 'AAPL Sell Signals',
                    type: 'scatter',
                    data: sellAAPLSignals,
                    marker: {
                        symbol: 'triangle-down',
                        fillColor: 'red'
                    }
                }, {
                    name: 'GLD Buy Signals',
                    type: 'scatter',
                    data: buyGLDSignals,
                    marker: {
                        symbol: 'triangle',
                        fillColor: 'green'
                    }
                }, {
                    name: 'GLD Sell Signals',
                    type: 'scatter',
                    data: sellGLDSignals,
                    marker: {
                        symbol: 'triangle-down',
                        fillColor: 'red'
                    }
                }]
            });

            // Plot Bollinger Bands chart with signals
            Highcharts.stockChart('bollinger-chart', {
                title: { text: 'Bollinger Bands & Signals' },
                xAxis: {
                    type: 'datetime',
                    ordinal: false
                },
                series: [{
                    name: 'Spread',
                    data: spreadData,
                    connectNulls: false
                }, {
                    name: 'Rolling Mean',
                    data: rollingMeanData,
                    connectNulls: false
                }, {
                    name: 'Upper Band',
                    data: upperBandData,
                    connectNulls: false
                }, {
                    name: 'Lower Band',
                    data: lowerBandData,
                    connectNulls: false
                },]
            });

            // Plot Profit & Loss chart
            Highcharts.stockChart('profit-chart', {
                title: { text: 'Unrealized Profit & Loss' },
                xAxis: {
                    type: 'datetime'
                },
                series: [{
                    name: 'Profit & Loss',
                    data: profitAndLossData
                }, {
                    name: 'Entry Points',
                    type: 'scatter',
                    data: openSignals,
                    marker: {
                        symbol: 'triangle',
                        fillColor: 'green'
                    }
                }, {
                    name: 'Exit Points',
                    type: 'scatter',
                    data: closeSignals,
                    marker: {
                        symbol: 'triangle-down',
                        fillColor: 'red'
                    }
                }]
            });


            // Populate table with signals
            let signalTableBody = $('#signal-table tbody');
            signalTableBody.empty();
            response.signals.forEach(signal => {
                signalTableBody.append(`
                    <tr>
                        <td>${signal.date}</td>
                        <td>${signal.type}</td>
                        <td>${signal.action_aapl}</td>
                        <td>${signal.price_aapl}</td>
                        <td>${signal.action_gld}</td>
                        <td>${signal.price_gld}</td>
                    </tr>
                `);
            });

            // Initialize or Reinitialize DataTable
            if ($.fn.dataTable.isDataTable('#signal-table')) {
                $('#signal-table').DataTable().clear().draw();
                $('#signal-table').DataTable().rows.add(signalTableBody).draw();
            } else {
                $('#signal-table').DataTable({
                    pageLength: 5, // Show 5 entries by default
                    lengthMenu: [5, 10, 20, "All"],
                    responsive: true,
                    searching: true
                });
            }
        },
        error: function (error) {
            console.log("error");
            console.error(error);
        }
    });
});

// 新增 Add Track 按鈕的點擊事件處理
$('#add-track-btn').on('click', function () {
    let formData = $('#strategy-form').serialize();
    formData += '&method=' + "Distance";  // 假設您有一個 id 為 'method' 的選擇框
    console.log(formData);
    $.ajax({
        url: '/api/add_track/',
        type: 'POST',
        data: formData,
        headers: { 'X-CSRFToken': csrfToken },
        success: function (response) {
            if (response.success) {
                alert('成功添加追蹤：' + response.message);
            } else {
                alert('添加追蹤失敗：' + response.error);
            }
        },
        error: function (error) {
            console.error('添加追蹤時發生錯誤：', error);
            alert('添加追蹤時發生錯誤。');
        }
    });
});
