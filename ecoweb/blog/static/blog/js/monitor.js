$(document).ready(function () {
    // 初始化 DataTable
    $('#trackTable').DataTable({
        "pageLength": 10,
        "lengthMenu": [[5, 10, 20, -1], [5, 10, 20, "全部"]],
        "language": {
            "lengthMenu": "顯示 _MENU_ 條目",
            "zeroRecords": "沒有找到匹配的記錄",
            "info": "顯示第 _START_ 至 _END_ 項結果，共 _TOTAL_ 項",
            "infoEmpty": "顯示第 0 至 0 項結果，共 0 項",
            "infoFiltered": "(由 _MAX_ 項結果過濾)",
            "search": "搜索:",
            "paginate": {
                "first": "首頁",
                "last": "末頁",
                "next": "下一頁",
                "previous": "上一頁"
            }
        }
    });

    // 取消追蹤按鈕點擊事件
    function setupUntrackButtons() {
        $('.untrack-btn').click(function () {
            var trackId = $(this).data('track-id');
            if (confirm('確定要取消追蹤嗎？')) {
                untrackRecord(trackId);
            }
        });
    }

    function untrackRecord(trackId) {
        $.ajax({
            url: '/api/add_track/',  // 使用與添加追蹤相同的 URL
            type: 'DELETE',
            data: JSON.stringify({ track_id: trackId }),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                    // 重新加載頁面或從表格中移除該行
                    location.reload();
                } else {
                    alert('取消追蹤失敗：' + response.error);
                }
            },
            error: function (xhr) {
                alert('發生錯誤，請稍後再試。錯誤：' + (xhr.responseJSON ? xhr.responseJSON.error : '未知錯誤'));
            }
        });
    }

    // 結果按鈕點擊事件
    function setupResultButtons() {
        $('.results-btn').click(function () {
            var trackId = $(this).data('track-id');
            showResults(trackId);
        });
    }

    function showResults(trackId) {
        var trackDetails = {
            method: $(`#method-${trackId}`).text(),
            stock1: $(`#stock1-${trackId}`).text(),
            stock2: $(`#stock2-${trackId}`).text(),
            start_date: $(`#start_date-${trackId}`).text(),
            end_date: new Date().toISOString().split('T')[0],
            window_size: parseInt($(`#window_size-${trackId}`).text()),
            n_std: parseFloat($(`#n_std-${trackId}`).text()),
            created_at: $(`#created_at-${trackId}`).text()
        };

        $.ajax({
            url: '/api/calculate_strategy/',
            type: 'POST',
            data: {
                stock1: trackDetails.stock1,
                stock2: trackDetails.stock2,
                start_date: trackDetails.start_date,
                end_date: trackDetails.end_date,
                n_std: trackDetails.n_std,
                window_size: trackDetails.window_size
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                console.log(response);
                if (response.dates && response.stock1_prices) {
                    showResultsModal(response, trackDetails);
                } else {
                    alert('計算策略失敗：' + (response.error || '返回的數據格式不正確'));
                }
            },
            error: function (xhr, status, error) {
                console.error('AJAX 錯誤:', status, error);
                console.error('響應文本:', xhr.responseText);
                alert('發生錯誤，請稍後再試。錯誤：' + (xhr.responseJSON ? xhr.responseJSON.error : error));
            }
        });
    }

    function showResultsModal(response, trackDetails) {
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
                            <h5 class="modal-title">策略結果</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <div id="price-chart" style="height: 400px;"></div>
                            <div id="bollinger-chart" style="height: 400px;"></div>
                            <div id="profit-chart" style="height: 400px;"></div>
                            <div class="mt-4">
                                <h6>Details</h6>
                                    <table id="signal-table" class="table table-bordered table-striped">
                                    <thead>
                                        <tr>
                                        <th>Date</th>
                                        <th>Type</th>
                                        <th>Action of AAPL</th>
                                        <th>Price of AAPL</th>
                                        <th>Action of GLD</th>
                                        <th>Price of GLD</th>
                                        </tr>
                                    </thead>
                                    <tbody></tbody>
                                    </table>
                            </div>
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
            drawCharts(response, trackDetails);
            populateSignalTable(response, trackDetails);
        });

        // 模態框隱藏後清理
        modal.on('hidden.bs.modal', function () {
            $(this).remove();
        });
    }

    function drawCharts(response, trackDetails) {
        function prepareData(dates, values) {
            return dates.map((timestamp, index) => [new Date(timestamp).getTime(), (values[index] === -2147483648) ? null : values[index]]);
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

        // 初始化或重新初始化 DataTable
        if ($.fn.dataTable.isDataTable('#signal-table')) {
            $('#signal-table').DataTable().clear().rows.add(signalTableBody.children()).draw();
        } else {
            $('#signal-table').DataTable({
                pageLength: 5, // Show 5 entries by default
                lengthMenu: [5, 10, 20, "All"],
                responsive: true,
                searching: true
            });
        }
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

    setupUntrackButtons();
    setupResultButtons();
});
