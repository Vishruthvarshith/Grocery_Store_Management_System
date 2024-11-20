$(function () {
    // JSON data by API call for order table
    $.get(orderListApiUrl, function (response) {
        if (response) {
            var table = '';
            var totalCost = 0;
            $.each(response, function(index, order) {
                // Ensure order.total is a number before adding to totalCost and formatting
                var orderTotal = parseFloat(order.total) || 0;
                totalCost += orderTotal;
                table += '<tr>' +
                    '<td>' + order.datetime + '</td>' +
                    '<td>' + order.order_id + '</td>' +
                    '<td>' + order.customer_name + '</td>' +
                    '<td>' + orderTotal.toFixed(2) + ' Rs</td>' +
                    '<td><span class="btn btn-xs btn-primary see-button" data-order-id="' + order.order_id + '">click to see</span></td>' +
                    '</tr>';
            });
            table += '<tr><td colspan="3" style="text-align: end"><b>Total</b></td><td><b>' + totalCost.toFixed(2) + ' Rs</b></td></tr>';
            $("table").find('tbody').empty().html(table);

            // Click event for the "See" button
            $("table").on("click", ".see-button", function() {
                var orderId = $(this).data("order-id");
                localStorage.setItem('orderId', orderId);
                window.location.href = "order_details.html";
            });
        }
    });
});
