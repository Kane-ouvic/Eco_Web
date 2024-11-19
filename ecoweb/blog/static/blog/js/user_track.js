$(document).ready(function () {
    $('.untrack-btn').click(function () {
        const API_BASE_URL = 'http://web.nightcover.com.tw:55556';
        var trackId = $(this).data('track-id');
        // 發送 AJAX 請求來取消追蹤
        $.ajax({
            url: `${API_BASE_URL}/api/untrack/`,
            type: 'POST',
            data: {
                track_id: trackId
            },
            xhrFields: {
                withCredentials: true // 確保攜帶 Cookie
            },
            success: function (response) {
                if (response.success) {
                    alert('成功取消追蹤');
                    location.reload();
                } else {
                    alert('取消追蹤失敗：' + response.error);
                }
            }
        });
    });

    $('.results-btn').click(function () {
        var trackId = $(this).data('track-id');
        // 跳轉到結果頁面
        window.location.href = '/track-results/' + trackId + '/';
    });
});