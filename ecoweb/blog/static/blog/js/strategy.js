$('#strategy-form').on('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    $.ajax({
        url: '/calculate-strategy/',  // Submit to your Django backend URL
        type: 'POST',
        data: $(this).serialize(),
        headers: { 'X-CSRFToken': csrfToken },
        success: function(response) {
            console.log(response); // Check if the returned data is correct

            // Prepare data for Highcharts
            let stock1Data = response.dates.map((timestamp, index) => [timestamp, response.stock1_prices[index]]);
            let stock2Data = response.dates.map((timestamp, index) => [timestamp, response.stock2_prices[index]]);
            let spreadData = response.dates.map((timestamp, index) => [timestamp, response.spread[index]]);
            let rollingMeanData = response.dates.map((timestamp, index) => [timestamp, response.rolling_mean[index]]);
            let upperBandData = response.dates.map((timestamp, index) => [timestamp, response.upper_band[index]]);
            let lowerBandData = response.dates.map((timestamp, index) => [timestamp, response.lower_band[index]]);
            let profitAndLossData = response.dates.map((timestamp, index) => [timestamp, response.profit_and_loss[index]]);

            // Prepare signals for marking
            let buyAAPLSignals = response.signals.filter(signal => signal.action_aapl === 'BUY').map(signal => [new Date(signal.date).getTime(), signal.price_aapl]);
            let sellAAPLSignals = response.signals.filter(signal => signal.action_aapl === 'SELL').map(signal => [new Date(signal.date).getTime(), signal.price_aapl]);

            let buyGLDSignals = response.signals.filter(signal => signal.action_gld === 'BUY').map(signal => [new Date(signal.date).getTime(), signal.price_gld]);
            let sellGLDSignals = response.signals.filter(signal => signal.action_gld === 'SELL').map(signal => [new Date(signal.date).getTime(), signal.price_gld]);

            // Plot Price & Spread chart with signals
            Highcharts.stockChart('price-chart', {
                title: { text: 'Price & Spread' },
                xAxis: {
                    type: 'datetime'
                },
                series: [{
                    name: response.stock1,
                    data: stock1Data
                }, {
                    name: response.stock2,
                    data: stock2Data
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
                        symbol: 'circle',
                        fillColor: 'green'
                    }
                }, {
                    name: 'GLD Sell Signals',
                    type: 'scatter',
                    data: sellGLDSignals,
                    marker: {
                        symbol: 'circle',
                        fillColor: 'red'
                    }
                }]
            });

            // Plot Bollinger Bands chart with signals
            Highcharts.stockChart('bollinger-chart', {
                title: { text: 'Bollinger Bands & Signals' },
                xAxis: {
                    type: 'datetime'
                },
                series: [{
                    name: 'Spread',
                    data: spreadData
                }, {
                    name: 'Rolling Mean',
                    data: rollingMeanData
                }, {
                    name: 'Upper Band',
                    data: upperBandData
                }, {
                    name: 'Lower Band',
                    data: lowerBandData
                }]
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
                  data: buyAAPLSignals,
                  marker: {
                    symbol: 'circle',
                    fillColor: 'green'
                  }
                }, {
                  name: 'Exit Points',
                  type: 'scatter',
                  data: sellAAPLSignals,
                  marker: {
                    symbol: 'circle',
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
        error: function(error) {
            console.error(error);
        }
    });
});
