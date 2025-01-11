// 新增 Add Track 按鈕的點擊事件處理
$(document).ready(function () {
    $('#add-track-btn').on('click', function () {
        // var formData = $('#strategyForm').serialize();
        // formData += '&method=' + "Distance";  // 假設您有一個 id 為 'method' 的選擇框
        var formData = {
            stockCode: $('#stockCode').val(),
            startDate: $('#startDate').val(),
            endDate: $('#endDate').val(),
            maLength: $('#maLength').val(),
            maType: $('#maType').val(),
            method: $('#method').val(),

            fastk_period: $('#fastk_period').val(),
            slowk_period: $('#slowk_period').val(),
            slowd_period: $('#slowd_period').val(),
            fastperiod: $('#fastperiod').val(),
            slowperiod: $('#slowperiod').val(),
            signalperiod: $('#signalperiod').val(),
            timeperiod: $('#timeperiod').val(),
            nbdevup: $('#nbdevup').val(),
            nbdevdn: $('#nbdevdn').val(),

            rsi_period: $('#rsi_period').val(),
            adx_period: $('#adx_period').val()
        };
        console.log(formData);
        $.ajax({
            url: `${API_BASE_URL}/api/add_entry_exit_track/`,
            type: 'POST',
            data: formData,
            headers: {
                'X-CSRFToken': getCookie('shared_csrftoken') // 攜帶 CSRF Token
            },
            xhrFields: {
                withCredentials: true // 攜帶共享的 Cookie
            },
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
    });
});