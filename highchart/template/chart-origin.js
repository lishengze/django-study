$(function () {
    // Create the chart

    var timeIterVal = [1,1,1,1,1,
                       5,5,5,5,5,
                       30,30,30,30,30, 
                       60,60,60,60,60, 
                       300,300,300,300,300,
                       1800,1800,1800,1800,1800, 
                       3600,3600,3600,3600,3600];



    var  cplusBandwidth = [16.3666, 19.5179, 16.8915, 12.8952, 13.4720,
                           20.2533, 14.0900, 13.9993, 13.9746, 15.2748,
                           13.4022, 18.0188, 17.6447, 17.2069, 17.8542,
                           17.7374, 18.4933, 17.3154, 17.7888, 17.5741,
                           18.1153, 17.8781, 20.2750, 18.5768, 18.4956,
                           18.9000, 18.6198, 20.3170, 22.3379, 24.0760,
                           23.0717, 23.7305, 14.1724, 16.7679, 20.8466];

    var nodejsBandwidth = [16.2051, 16.0147, 15.6262, 15.6275, 16.4663, 
                           15.9384, 15.7885, 15.7377, 15.8419, 15.8905,
                           15.5214, 15.3816, 15.3701, 15.4470, 15.2616,
                           14.9319, 15.3805, 15.3814, 15.5795, 15.1035,
                           15.3273, 15.1707, 15.2477, 14.3100, 17.7113,
                           21.1948, 21.2200, 20.9214, 20.6939, 20.4914,
                           20.3412, 20.2045, 18.4296, 20.2005, 20.2025];

    
    $('#CplusAndNodejs').highcharts(
    {
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: 'Test Communication BandWith in C++ and Nodejs',
            style: { "fontSize": "24px" } 
        },        
        xAxis: [{
            categories: timeIterVal,
            crosshair: true,
            labels: {
                format: '{value}S',
                style: {
                    "fontSize": "16px"
                }
            }
        }],
        yAxis: [{ 
            lineWidth: 0,
            gridLineWidth: 0,
            title: {
                text: 'Bandwidth',
                style: {
                    color: Highcharts.getOptions().colors[0],
                     "fontSize": "20px"
                }
            },
            labels: {
                format: '{value}',
                style: {
                    color: Highcharts.getOptions().colors[0],
                    "fontSize": "18px"
                }
            }
        }],
        tooltip: {
            formatter: function () {
                var s = '<b> Test Time: ' + this.x + 's</b>';
                $.each(this.points, function () {
                    s += '<br/>' + this.series.name + ': ' +
                        this.y + ' MB/s';
                });
                return s;
            },
            shared: true
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            x: 80,
            verticalAlign: 'top',
            y: 55,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
        },
        series: [{
            name: 'C++     ',
            type: 'spline',
            data: cplusBandwidth,
            marker: {
                enabled: false
            },
        }, {
            name: 'Nodejs   ',
            type: 'spline',
            data: nodejsBandwidth,
        }]
    });

});

