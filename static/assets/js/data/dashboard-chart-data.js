/* ====== Chart ====== */

(function ($) {
    "use strict";

    function initializeChart(chartId, chartOptions) {
        var chartElement = document.getElementById(chartId);
        if (chartElement) {
            var chart = new ApexCharts(chartElement, chartOptions);
            chart.render();
        } else {
            console.warn(`Chart element ${chartId} not found. Skipping chart initialization.`);
        }
    }

    function userNumbers() {
        var options = {
            chart: {
                type: "bar",
                height: 50,
                stacked: true,
                sparkline: {
                    enabled: true
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 5,
                    blur: 3,
                    color: '#000',
                    opacity: 0.1
                }
            },
            stroke: {
                width: 0
            },
            dataLabels: {
                enabled: false
            },
            series: [{
                name: "Organic",
                data: [1070, 2250, 1565, 4560, 2850, 5658, 7854, 1565, 4560, 2850, 5658, 7854]
            }, {
                name: "Referal",
                data: [950, 2100, 1265, 4160, 2350, 5258, 7354, 1265, 4160, 2350, 5358, 7554]
            }],
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: 25,
                    borderRadius: 0
                }
            },
            xaxis: {
                categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                },
                labels: {
                    show: false
                }
            },
            yaxis: {
                labels: {
                    show: false
                }
            },
            colors: ["#485568", "#71757b"],
        };
        initializeChart("userNumbers", options);
    }

    function bookingNumbers() {
        var options = {
            chart: {
                type: "line",
                height: 50,
                sparkline: {
                    enabled: true
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 5,
                    blur: 3,
                    color: '#000',
                    opacity: 0.1
                }
            },
            series: [{
                data: [1362, 3954, 7152, 4254, 3485, 4956, 3568, 2365, 1050, 1920, 4785, 6856]
            }],
            stroke: {
                curve: "smooth",
                width: 2
            },
            colors: ["#485568"],
            xaxis: {
                categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                }
            },
            tooltip: {
                fixed: {
                    enabled: false
                },
                y: {
                    title: {
                        formatter: function (e) {
                            return ""
                        }
                    }
                }
            },
        };
        initializeChart("bookingNumbers", options);
    }

    function revenueNumbers() {
        var options = {
            series: [{
                data: [1070, 2250, 1565, 4560, 2850, 5658, 7854, 1565, 4560, 2850, 5658, 7854]
            }],
            chart: {
                type: "bar",
                height: 50,
                sparkline: {
                    enabled: true
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 5,
                    blur: 3,
                    color: '#000',
                    opacity: 0.1
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: 25,
                    borderRadius: 0
                }
            },
            xaxis: {
                categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                }
            },
            tooltip: {
                fixed: {
                    enabled: false
                },
                y: {
                    title: {
                        formatter: function (e) {
                            return ""
                        }
                    }
                }
            },
            colors: ["#485568"]
        };
        initializeChart("revenueNumbers", options);
    }

    function expensesNumbers() {
        var options = {
            chart: {
                type: "line",
                height: 50,
                sparkline: {
                    enabled: true
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 5,
                    blur: 3,
                    color: '#000',
                    opacity: 0.1
                }
            },
            series: [{
                data: [850, 1920, 1362, 3954, 2485, 4956, 7152, 1254, 3568, 2365, 4785, 6856]
            }],
            stroke: {
                curve: "smooth",
                width: 2
            },
            colors: ["#485568"],
            xaxis: {
                categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                }
            },
            tooltip: {
                fixed: {
                    enabled: false
                },
                y: {
                    title: {
                        formatter: function (e) {
                            return ""
                        }
                    }
                }
            },
        };
        initializeChart("expensesNumbers", options);
    }

    function overviewChart() {
        var options = {
            series: [{
                name: 'Bookings',
                type: 'area',
                data: [23, 12, 23, 22, 15, 42, 31, 27, 45, 28, 37]
            }, {
                name: 'Revenue',
                type: 'line',
                data: [44.64, 55.48, 20.15, 30.62, 12.57, 30.38, 41.85, 41.44, 40.56, 25.84, 43.78]
            }, {
                name: 'Expence',
                type: 'line',
                data: [30.55, 24.67, 36.85, 37.08, 42.85, 38.85, 46.64, 45.42, 49.89, 36.56, 38.49]
            }],
            chart: {
                height: 365,
                type: 'line',
                stacked: false,
                foreColor: '#373d3f',
                sparkline: {
                    enabled: false
                },
                dropShadow: {
                    enabled: true,
                    enabledOnSeries: undefined,
                    top: 5,
                    left: 5,
                    blur: 3,
                    color: '#000',
                    opacity: 0.1
                },
                toolbar: {
                    show: false
                }
            },
            stroke: {
                width: [2, 2, 2],
                curve: 'smooth'
            },
            fill: {
                opacity: [0.5, 1, 1],
            },
            colors: ['#485568', '#87909e', '#7ea0fb'],
            xaxis: {
                categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                axisTicks: {
                    show: false
                },
                axisBorder: {
                    show: false
                }
            },
            legend: {
                show: true,
                horizontalAlign: "center",
                offsetX: 0,
                offsetY: -5,
                markers: {
                    width: 15,
                    height: 10,
                    radius: 6
                },
                itemMargin: {
                    horizontal: 10,
                    vertical: 0
                }
            },
            grid: {
                show: false,
                xaxis: {
                    lines: {
                        show: false
                    }
                },
                yaxis: {
                    lines: {
                        show: false
                    }
                },
                padding: {
                    top: 0,
                    right: -2,
                    bottom: 15,
                    left: 0
                },
            },
            tooltip: {
                shared: true,
                y: [{
                    formatter: function (e) {
                        return void 0 !== e ? e.toFixed(0) : e
                    }
                }, {
                    formatter: function (e) {
                        return void 0 !== e ? "$" + e.toFixed(2) + "k" : e
                    }
                }, {
                    formatter: function (e) {
                        return void 0 !== e ? "$" + e.toFixed(2) + "k" : e
                    }
                }]
            },
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        height: '300px',
                    },
                    yaxis: {
                        show: false,
                    },
                }
            }]
        };
        initializeChart("overviewChart", options);
    }

    $(window).on('load', function () {
        try {
            userNumbers();
            bookingNumbers();
            revenueNumbers();
            expensesNumbers();
            overviewChart();
        } catch (error) {
            console.error("Error initializing charts:", error);
        }
    });

})(jQuery);

