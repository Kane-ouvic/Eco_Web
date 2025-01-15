$(document).ready(function () {
    const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
    // 初始化 DataTable
    $('#entryExitTable').DataTable({
        "pageLength": 20,
        "lengthMenu": [[5, 10, 20, -1], [5, 10, 20, "All"]],
        "language": {
            "lengthMenu": "Show _MENU_ entries",
            "zeroRecords": "No matching records found",
            "info": "Showing _START_ to _END_ of _TOTAL_ entries",
            "infoEmpty": "Showing 0 to 0 of 0 entries",
            "infoFiltered": "(filtered from _MAX_ total entries)",
            "search": "Search:",
            "paginate": {
                "first": "First",
                "last": "Last",
                "next": "Next",
                "previous": "Previous"
            }
        }
    });

    // 取消追蹤按鈕點擊事件
    function setupUntrackButtons2() {
        $('.untrack-btn2').click(function () {
            var trackId = $(this).data('track-id');
            if (confirm('Are you sure you want to untrack?')) {
                untrackRecord2(trackId);
            }
        });
    }

    function untrackRecord2(trackId) {
        $.ajax({
            url: `${API_BASE_URL}/api/add_entry_exit_track/`,  // 使用與添加追蹤相同的 URL
            type: 'DELETE',
            data: JSON.stringify({ track_id: trackId }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('shared_csrftoken') // 攜帶 CSRF Token
            },
            xhrFields: {
                withCredentials: true // 攜帶共享的 Cookie
            },
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    // 重新加載頁面或從表格中移除該行
                    location.reload();
                } else {
                    alert('Unfollow failed: ' + response.error);
                }
            },
            error: function (xhr) {
                alert('發生錯誤，請稍後再試。錯誤：' + (xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error'));
            }
        });
    }

    // 結果按鈕點擊事件
    function setupResultButtons2() {
        $('.results-btn2').click(function () {
            var trackId = $(this).data('track-id');
            showResults_entry_exit(trackId);
        });
    }

    function showResults_entry_exit(trackId) {
        var trackDetails = {
            stock1: $(`#stock1-${trackId}`).text(),
            start_date: $(`#start_date-${trackId}`).text(),
            end_date: $(`#end_date-${trackId}`).text(),
            ma_length: $(`#ma_length-${trackId}`).text(),
            ma_type: $(`#ma_type-${trackId}`).text(),
            method: $(`#method-${trackId}`).text(),
            fastk_period: $(`#fastk_period-${trackId}`).text(),
            slowk_period: $(`#slowk_period-${trackId}`).text(),
            slowd_period: $(`#slowd_period-${trackId}`).text(),
            fastperiod: $(`#fastperiod-${trackId}`).text(),
            slowperiod: $(`#slowperiod-${trackId}`).text(),
            signalperiod: $(`#signalperiod-${trackId}`).text(),
            timeperiod: $(`#timeperiod-${trackId}`).text(),
            nbdevup: $(`#nbdevup-${trackId}`).text(),
            nbdevdn: $(`#nbdevdn-${trackId}`).text(),
            rsi_period: $(`#rsi_period-${trackId}`).text(),
            adx_period: $(`#adx_period-${trackId}`).text(),
            created_at: $(`#created_at-${trackId}`).text()
        };
        console.log(trackDetails);

        $.ajax({
            url: `${API_BASE_URL}/api/entry_exit/`,
            type: 'POST',
            data: {
                stockCode: trackDetails.stock1,
                startDate: trackDetails.start_date,
                endDate: trackDetails.end_date,
                maLength: trackDetails.ma_length,
                maType: trackDetails.ma_type,
                method: trackDetails.method,

                fastk_period: trackDetails.fastk_period,
                slowk_period: trackDetails.slowk_period,
                slowd_period: trackDetails.slowd_period,
                fastperiod: trackDetails.fastperiod,
                slowperiod: trackDetails.slowperiod,
                signalperiod: trackDetails.signalperiod,
                timeperiod: trackDetails.timeperiod,
                nbdevup: trackDetails.nbdevup,
                nbdevdn: trackDetails.nbdevdn,

                rsi_period: trackDetails.rsi_period,
                adx_period: trackDetails.adx_period
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                console.log(response);
                console.log(response.success);
                if (response.success) {
                    showResultsModal_entry_exit(response, trackDetails);
                } else {
                    alert('Calculation failed: ' + (response.error || 'Incorrect data format'));
                }
            },
            error: function (xhr, status, error) {
                console.error('AJAX error:', status, error);
                console.error('Response text:', xhr.responseText);
                alert('An error occurred, please try again later. Error: ' + (xhr.responseJSON ? xhr.responseJSON.error : error));
            }
        });
    }

    function showResultsModal_entry_exit(response, trackDetails) {
        // 檢查是否已存在模態框
        var existingModal = $('#resultsModal');
        if (existingModal.length) {
            existingModal.remove();
        }

        // 創建模態框
        var modal = $(`
            <div class="modal fade" id="resultsModal" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-xl" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Strategy Results</h5>
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <h6>參數設定</h6>
                            <table class="table table-bordered table-striped">
                                <thead>
                                    <tr>
                                        <th>參數</th>
                                        <th>值</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>stock1</td>
                                        <td>${trackDetails.stock1}</td>
                                    </tr>
                                    <tr>
                                        <td>MA length</td>
                                        <td>${trackDetails.ma_length}</td>
                                    </tr>
                                    <tr>
                                        <td>MA type</td>
                                        <td>${trackDetails.ma_type}</td>
                                    </tr>
                                    <tr>
                                        <td>method</td>
                                        <td>${trackDetails.method}</td>
                                    </tr>
                                    <tr>
                                        <td>fastk_period</td>
                                        <td>${trackDetails.fastk_period}</td>
                                    </tr>
                                    <tr>
                                        <td>slowk_period</td>
                                        <td>${trackDetails.slowk_period}</td>
                                    </tr>
                                    <tr>
                                        <td>slowd_period</td>
                                        <td>${trackDetails.slowd_period}</td>
                                    </tr>
                                    <tr>
                                        <td>fastperiod</td>
                                        <td>${trackDetails.fastperiod}</td>
                                    </tr>
                                    <tr>
                                        <td>slowperiod</td>
                                        <td>${trackDetails.slowperiod}</td>
                                    </tr>
                                    <tr>
                                        <td>signalperiod</td>
                                        <td>${trackDetails.signalperiod}</td>
                                    </tr>
                                    <tr>
                                        <td>timeperiod</td>
                                        <td>${trackDetails.timeperiod}</td>
                                    </tr>
                                    <tr>
                                        <td>nbdevup</td>
                                        <td>${trackDetails.nbdevup}</td>
                                    </tr>
                                    <tr>
                                        <td>nbdevdn</td>
                                        <td>${trackDetails.nbdevdn}</td>
                                    </tr>
                                    <tr>
                                        <td>rsi_period</td>
                                        <td>${trackDetails.rsi_period}</td>
                                    </tr>
                                    <tr>
                                        <td>adx_period</td>
                                        <td>${trackDetails.adx_period}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="modal-body">
                            <div id="ceiling_floor-chart" class="mt-3"></div>
                            <div id="kd-chart" class="mt-3"></div>
                            <div id="macd-chart" class="mt-3"></div>
                            <div id="bool-chart" class="mt-3"></div>
                            <div id="rsi-chart" class="mt-3"></div>
                            <div id="adx-dmi-chart" class="mt-3"></div>
                            <div id="kline-chart" class="mt-3"></div>
                        </div>
                    </div>
                </div>
            </div>
        `);

        // 將模態框添加到頁面
        $('body').append(modal);

        // 顯示模態框
        modal.modal('show');

        // 模態框完全顯示後繪製圖表和填��表格
        modal.on('shown.bs.modal', function () {
            drawCharts_entry_exit(response, trackDetails);
        });

        // 模態框隱藏後清理
        modal.on('hidden.bs.modal', function () {
            $(this).remove();
        });
    }

    function drawCharts_entry_exit(data, trackDetails) {
        // function prepareData(dates, values) {
        //     return dates.map((timestamp, index) => [new Date(timestamp).getTime(), (values[index] === -2147483648) ? null : values[index]]);
        // }

        // let candlestickData = prepareData(response.dates, response.candlestick_data);
        // let maData = prepareData(response.dates, response.ma);
        // let ceilingPriceData = prepareData(response.dates, response.ceiling_price);
        // let floorPriceData = prepareData(response.dates, response.floor_price);
        // let ceilingSignals = response.ceilingfloor_signals.map(signal => ({
        //     x: new Date(signal[0]).getTime(),
        //     y: signal[1],
        //     action: signal[2],
        //     additionalInfo: signal[3],
        //     marker: {
        //         symbol: signal[2] === 'buy' ? 'triangle' : 'triangle-down',
        //         fillColor: signal[2] === 'buy' ? '#000000' : '#000000'
        //     }
        // }));

        // 繪製天花板地板線圖表
        Highcharts.stockChart('ceiling_floor-chart', {
            chart: {
                type: 'line',
                height: 800
            },
            title: { text: '天花板地板線' },
            xAxis: {
                type: 'datetime',
                title: { text: '時間' },
                ordinal: false
            },
            yAxis: [{
                title: { text: '股價' },
                height: '40%',
                plotLines: [{
                    value: 15,
                    width: 1,
                    color: '#808080'
                }]
            }, {
                title: { text: '漲跌幅度' },
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
                    type: 'column',
                    name: '成交量',
                    data: data.volume_data,
                    yAxis: 2,
                    color: '#888888'
                },
                {
                    name: '天花板地板進出場訊號',
                    data: data.ceilingfloor_signals.map(signal => ({
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
                }
            ]
        });

        Highcharts.stockChart('kd-chart', {
            chart: {
                type: 'line',
                height: 800
            },
            title: { text: 'KD線' },
            xAxis: {
                type: 'datetime',
                title: { text: '時間' },
                ordinal: false
            },
            yAxis: [{
                title: { text: '股價' },
                height: '40%'
            }, {
                title: { text: 'KD值' },
                top: '45%',
                height: '20%',
                offset: 0,
                plotBands: [{
                    from: 80,
                    to: 100,
                    color: 'rgba(255, 0, 0, 0.1)',
                    label: {
                        text: '超買區'
                    }
                }, {
                    from: 0,
                    to: 20,
                    color: 'rgba(0, 255, 0, 0.1)',
                    label: {
                        text: '超賣區'
                    }
                }],
                plotLines: [{
                    value: 80,
                    width: 2,
                    color: '#FF0000',
                    dashStyle: 'dash'
                }, {
                    value: 20,
                    width: 2,
                    color: '#00FF00',
                    dashStyle: 'dash'
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
                }
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
                    name: 'K值',
                    data: data.kd_K.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#FF0000',
                    lineWidth: 2,
                    yAxis: 1
                },
                {
                    name: 'D值',
                    data: data.kd_D.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#00FF00',
                    lineWidth: 2,
                    yAxis: 1
                },
                {
                    name: 'KD進出場訊號',
                    data: data.kd_signals.map(signal => ({
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
        // } else if (strategy === 'macd') {
        // 繪製MACD圖表
        Highcharts.stockChart('macd-chart', {
            chart: {
                type: 'line',
                height: 800
            },
            title: {
                text: 'MACD指標'
            },
            xAxis: {
                type: 'datetime',
                title: {
                    text: '時間'
                },
                ordinal: false
            },
            yAxis: [{
                title: {
                    text: '股價'
                },
                height: '40%'
            }, {
                title: {
                    text: 'MACD'
                },
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
                }
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
                    name: 'MACD',
                    data: data.macd_data.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#0000FF',
                    lineWidth: 2,
                    yAxis: 1
                },
                {
                    name: 'Signal',
                    data: data.macd_signal.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#FF0000',
                    lineWidth: 2,
                    yAxis: 1
                },
                {
                    name: 'Histogram',
                    type: 'column',
                    data: data.macd_hist.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    yAxis: 1
                },
                {
                    name: 'MACD進出場訊號',
                    data: data.macd_signals.map(signal => ({
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
        // } else if (strategy === 'booling') {
        // 繪製布林通道圖
        Highcharts.stockChart('bool-chart', {
            chart: {
                type: 'line',
                height: 600
            },
            title: { text: '布林通道' },
            xAxis: {
                type: 'datetime',
                title: { text: '時間' },
                ordinal: false
            },
            yAxis: [{
                title: { text: '股價' },
                height: '70%',
                plotLines: [{
                    value: 15,
                    width: 1,
                    color: '#808080'
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
                }
            },
            series: [
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
                    name: '中線',
                    data: data.bool_mid.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#000000',
                    lineWidth: 2
                },
                {
                    name: '上軌',
                    data: data.bool_upper.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#0000FF',
                    lineWidth: 1
                },
                {
                    name: '下軌',
                    data: data.bool_lower.map((value, index) => [
                        data.candlestick_data[index][0],
                        value === -2147483648 ? null : value
                    ]),
                    color: '#FF0000',
                    lineWidth: 1
                },
                {
                    name: '布林通道進出場訊號',
                    data: data.bool_signals.map(signal => ({
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
                    yAxis: 1,
                    color: '#888888'
                }
            ]
        });
        // } else if (strategy === 'rsi') {
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
        // } else if (strategy === 'adx_dmi') {

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


        Highcharts.stockChart('kline-chart', {
            chart: {
                type: 'line',
                height: 800
            },
            title: { text: 'K線型態' },
            xAxis: {
                type: 'datetime',
                title: { text: '時間' },
                ordinal: false
            },
            yAxis: [{
                title: { text: '價格' },
                height: '40%',
                plotLines: [{
                    value: 15,
                    width: 1,
                    color: '#808080'
                }]
            }, {
                title: { text: '漲跌幅度' },
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
                    name: 'K線型態',
                    data: data.kline_patterns.map(pattern => ({
                        x: pattern[0],
                        y: pattern[1],
                        pattern: pattern[2],
                        additionalInfo: pattern[3],
                        marker: {
                            symbol: pattern[2] === 'bullish' ? 'triangle' : (pattern[2] === 'bearish' ? 'triangle-down' : 'circle'),
                            fillColor: pattern[2] === 'bullish' ? '#00FF00' : (pattern[2] === 'bearish' ? '#FF0000' : '#0000FF')
                        }
                    })),
                    tooltip: {
                        pointFormat: '型態: {point.pattern}<br/>時間: {point.additionalInfo}<br/>價格: {point.y}'
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
        // Populate table with signals
        // let signalTableBody = $('#signal-table tbody');
        // signalTableBody.empty();
        // response.signals.forEach(signal => {
        //     signalTableBody.append(`
        //          <tr>
        //              <td>${signal.date}</td>
        //              <td>${signal.type}</td>
        //              <td>${signal.action_aapl}</td>
        //              <td>${signal.price_aapl}</td>
        //              <td>${signal.action_gld}</td>
        //              <td>${signal.price_gld}</td>
        //          </tr>
        //      `);
        // });

        // // 初始化或重新初始化 DataTable
        // if ($.fn.dataTable.isDataTable('#signal-table')) {
        //     $('#signal-table').DataTable().clear().rows.add(signalTableBody.children()).draw();
        // } else {
        //     $('#signal-table').DataTable({
        //         pageLength: 5, // Show 5 entries by default
        //         lengthMenu: [5, 10, 20, "All"],
        //         responsive: true,
        //         searching: true
        //     });
        // }
    }

    // 獲取 CSRF token 的輔助函數
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setupUntrackButtons2();
    setupResultButtons2();
});
