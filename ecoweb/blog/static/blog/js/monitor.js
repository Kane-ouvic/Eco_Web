$(document).ready(function () {
    $('.untrack-btn').click(function () {
        var trackId = $(this).data('track-id');
        // 發送 AJAX 請求來取消追蹤
        $.ajax({
            url: '/api/untrack/',
            type: 'POST',
            data: {
                track_id: trackId,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
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