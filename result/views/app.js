var app = angular.module('BidenvsTrump', []);
var socket = io.connect(); // Modify this as per your server

app.controller('statsCtrl', function($scope){
    $scope.aPercent = 50;
    $scope.bPercent = 50;
    $scope.total = 0;

    var pieChart = null;

    socket.on('scores', function (json) {
        var data = JSON.parse(json);
        var a = parseInt(data.a || 0);
        var b = parseInt(data.b || 0);

        $scope.$apply(function () {
            $scope.aPercent = a / (a + b) * 100;
            $scope.bPercent = b / (a + b) * 100;
            $scope.total = a + b;
            updatePieChart();
        });
    });

    function updatePieChart() {
        if (pieChart) {
            pieChart.data.datasets[0].data = [$scope.total * $scope.aPercent / 100, $scope.total * $scope.bPercent / 100];
            pieChart.update();
        }
    }

    function initChart() {
        var ctx = document.getElementById("pieChart").getContext('2d');
        pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ["Biden", "Trump"],
                datasets: [{
                    data: [50, 50], // Default values
                    backgroundColor: ['#3498db', '#e74c3c'],
                    hoverBackgroundColor: ['#2980b9', '#c0392b']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    position: 'bottom'
                }
            }
        });
    }

    initChart();
});
