(function ($) {
    "use strict";
    /*========== Loader ===========*/
    $(window).on("load", function () {
        $(".lh-loader").fadeOut("slow");
    });

    /*========== Sticky header ===========*/
    window.addEventListener("scroll", () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 70) {
            $(".lh-horizontal-nav").addClass("header-fixed");
        } else {
            $(".lh-horizontal-nav").removeClass("header-fixed");
        }
    });

    /*========== Mobile side menu (demo-2, demo-3) ===========*/
    $('.lh-toggle-sidebar-2, .lh-toggle-sidebar-3').on("click", function () {
        $('.lh-mobile-menu-overlay').fadeIn();
        $('.lh-mobile-menu').addClass("lh-menu-open");
    });

    $('.lh-mobile-menu-overlay, .lh-close-menu').on("click", function () {
        $('.lh-mobile-menu-overlay').fadeOut();
        $('.lh-mobile-menu').removeClass("lh-menu-open");
    });

    function ResponsiveMobilemsMenu() {
        var $msNav = $(".lh-menu-content, .overlay-menu"),
            $msNavSubMenu = $msNav.find(".sub-menu");
        $msNavSubMenu.parent().prepend('<span class="menu-toggle"></span>');

        $msNav.on("click", "li a, .menu-toggle", function (e) {
            var $this = $(this);
            if ($this.attr("href") === "#" || $this.hasClass("menu-toggle")) {
                e.preventDefault();
                if ($this.siblings("ul:visible").length) {
                    $this.parent("li").removeClass("active");
                    $this.siblings("ul").slideUp();
                    $this.parent("li").find("li").removeClass("active");
                    $this.parent("li").find("ul:visible").slideUp();
                } else {
                    $this.parent("li").addClass("active");
                    $this.closest("li").siblings("li").removeClass("active").find("li").removeClass("active");
                    $this.closest("li").siblings("li").find("ul:visible").slideUp();
                    $this.siblings("ul").slideDown();
                }
            }
        });
    }
    ResponsiveMobilemsMenu();

    /*========== Nav Sidebar ===========*/
    $(document).ready(function () {

        // /*========== Tooltips ===========*/
        // if ($.fn.tooltip) {
        //     $('[title]').attr('data-bs-toggle', 'tooltip');
        //     $('[title]').tooltip();
        // } else {
        //     console.warn("Bootstrap's tooltip function is not available.");
        // }
        
        // $('[title]').attr('data-bs-toggle', 'tooltip');
        // $('[title]').tooltip();
        /*========== Sidebar ===========*/
        // mobileAndTabletCheck       
        window.mobileAndTabletCheck = function () {
            let check = false;
            (function (a) { if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true; })(navigator.userAgent || navigator.vendor || window.opera);
            return check;
        };

        function winSizeWidth() {
            var width = $(window).width();
            width = isMobTab ? width : width + 17;
            return width;
        }

        var currentActiveTab = localStorage.getItem('currentActiveTab') ?? null;
        var currentActiveSubTab = localStorage.getItem('currentActiveSubTab') ?? null;
        var currentSubLink = localStorage.getItem('currentSubLink') ?? null;

        var isMobTab = mobileAndTabletCheck();
        var screenSize = winSizeWidth();

        var sSize = {
            min: 576,
            max: 992,
        }

        function hideShowSidebar(el, activeEl, className, type) {
            if (sSize.max > screenSize) {
                if (sSize.min >= screenSize) {
                    $(el).show();
                    $(activeEl).addClass(className);
                } else {
                    if ($(".wrapper").hasClass("sb-default")) {
                        if (type == "click") {
                            $(el).show();
                            $(activeEl).addClass(className);
                        } else {
                            $(el).hide();
                            $(activeEl).removeClass(className);
                        }
                    }

                    if ($(".wrapper").hasClass("sb-collapse")) {
                        if (type == "resize" || type == "click") {
                            $(el).hide();
                            $(activeEl).removeClass(className);
                        } else {
                            $(el).show();
                            $(activeEl).addClass(className);
                        }
                    }

                }

            } else {
                if ($(".wrapper").hasClass("sb-default")) {
                    $(el).show();
                    $(activeEl).addClass(className);
                }

                if ($(".wrapper").hasClass("sb-collapse")) {
                    if (type == "mouseenter") {
                        $(el).show();
                        $(activeEl).addClass(className);
                    } else {
                        $(el).hide();
                        $(activeEl).removeClass(className);
                    }

                }
            }
        }

        function sidebarActiveTabs(type = '') {
            screenSize = winSizeWidth();
            $(".lh-sb-drop").hide();
            $(".lh-sb-subdrop.condense").hide();

            if (currentActiveTab != '') {
                var currentActiveEle = $(`span.condense:contains('${currentActiveTab}')`).filter(function () {
                    return $(this).text() === currentActiveTab;
                });
                var activeEl = $(currentActiveEle).parents('.lh-sb-item');
                var dropEl = $(currentActiveEle).parents('.lh-sb-item').find('.lh-sb-drop');
                hideShowSidebar(dropEl, activeEl, 'load-active', type);
            }

            if (currentActiveSubTab != '') {
                var currentSubTabActiveEle = $(`span.condense:contains('${currentActiveSubTab}')`).filter(function () {
                    return $(this).text() === currentActiveSubTab;
                });
                $(currentSubTabActiveEle).parents('.sb-subdrop-item').find('.lh-sb-subdrop.condense').show();
                var activeEl = $(currentSubTabActiveEle).parents('.sb-subdrop-item');
                var dropEl = $(currentSubTabActiveEle).parents('.sb-subdrop-item').find('.lh-sb-subdrop');
                hideShowSidebar(dropEl, activeEl, 'load-sub-active', type);
            }

            if (currentSubLink != '') {
                var currentSubActiveEle = $(`a.lh-page-link:contains('${currentSubLink}')`).filter(function () {
                    return $(this).text() === currentSubLink;
                });
                $(currentSubActiveEle).addClass('active-link');
                var activeEl = $(currentSubActiveEle).parents('.lh-sb-item');
                var dropEl = $(currentSubActiveEle).parents('.lh-sb-drop');
                hideShowSidebar(dropEl, activeEl, 'load-active', type);
            }
        }

        var newURL = window.location.pathname;
        var newURL = newURL.split("https://maraviyainfotech.com/").pop();
        $(".lh-sb-drop").hide();

        if (sSize.max > screenSize) {
            if (sSize.min >= screenSize) {

                $(".condense:not(.lh-sb-drop)").hide();
            } else {
                $(".wrapper").toggleClass("sb-collapse sb-default");

                $(".condense:not(.lh-sb-drop)").hide();
            }
        }

        if ($(".wrapper").hasClass("sb-default")) {
            $('.lh-sb-drop').hide();
            $("a.lh-page-link").filter(`[href='${newURL}']`).parent().parent().show();

            $("a.lh-page-link").filter(`[href='${newURL}']`).parent().parent().parent().addClass('load-active');
            $("a.lh-page-link").filter(`[href='${newURL}']`).addClass('active-link');

            var currentActiveLnk = $("a.lh-page-link").filter(`[href='${newURL}']`);

            if (currentActiveLnk.length > 0) {
                setlhPagelink($(currentActiveLnk));
            }

            var lastURL = localStorage.getItem('URL');

            sidebarActiveTabs();

            localStorage.setItem('URL', newURL);
        }

        $(".lh-drop-toggle").on("click", function (e) {
            var senderElement = e.target;

            if ($(senderElement).hasClass('lh-sub-drop-toggle')) return;
            if ($(senderElement).hasClass('lh-page-link')) return;
            if ($(senderElement).hasClass('condense') && $(senderElement).parents('.lh-sub-drop-toggle').length > 0) return;

            var parent = $(this).parents('.sb-drop-item');
            currentActiveTab = $(parent).find('.lh-drop-toggle span.condense').text();

            if ($(parent).hasClass('load-active')) {
                $(parent).find(".lh-sb-drop").slideUp();
                $(parent).removeClass('load-active');
                currentSubLink = currentActiveSubTab = currentActiveTab = '';
                localStorage.setItem('currentActiveTab', '');
                localStorage.setItem('currentActiveSubTab', '');
                localStorage.setItem('currentSubLink', '');
            } else {
                $('.load-active').removeClass('load-active');
                $(".lh-sb-drop").slideUp();
                $(parent).addClass('load-active');
                $(parent).find(".lh-sb-drop").slideDown();
                localStorage.setItem('currentActiveTab', currentActiveTab);
                currentSubLink = '';
                localStorage.setItem('currentSubLink', '');
            }
        });

        $(".lh-sub-drop-toggle").on("click", function (e) {
            var senderElement = e.target;

            var parent = $(this).parents('.sb-subdrop-item');
            currentActiveSubTab = $(parent).find('.lh-sub-drop-toggle span.condense').text();

            if ($(parent).hasClass('load-sub-active')) {
                $(parent).find(".lh-sb-subdrop").slideUp();
                $(parent).removeClass('load-sub-active');
                currentActiveSubTab = currentSubLink = '';
                localStorage.setItem('currentActiveSubTab', '');
                localStorage.setItem('currentSubLink', '');
            } else {
                $('.load-sub-active').removeClass('load-sub-active');
                $(".lh-sb-subdrop").hide();
                $(parent).addClass('load-sub-active');
                $(parent).find(".lh-sb-subdrop").slideDown();
                localStorage.setItem('currentActiveSubTab', currentActiveSubTab);
            }
        });

        function setlhPagelink(_this) {
            $('.active-link').removeClass('active-link');

            currentSubLink = $(_this).text();

            if (currentSubLink != '') {
                localStorage.setItem('currentSubLink', currentSubLink);
            }

            $(_this).addClass('active-link');

            // sb-drop-item
            const mainParentHas = $(_this).parents('.sb-drop-item');

            if (mainParentHas) {
                currentActiveTab = $(mainParentHas).find('.lh-drop-toggle span.condense').text();

                localStorage.setItem('currentActiveTab', currentActiveTab);
            }

            // Sub Parent Item
            const subParentHas = $(_this).parents('.sb-subdrop-item');
            if (subParentHas) {
                currentActiveSubTab = $(subParentHas).find('.lh-sub-drop-toggle span.condense').text();

                localStorage.setItem('currentActiveSubTab', currentActiveSubTab);
            }
        }

        $(".lh-page-link").on("click", function (e) {
            setlhPagelink($(this));
        });

        $(window).resize(function (e) {
            screenSize = winSizeWidth();
            if (sSize.max >= screenSize) {
                if ($(".wrapper").hasClass("sb-default")) {
                    $(".lh-sidebar-overlay").fadeOut();

                    if (sSize.min <= screenSize) {
                        if ($(".lh-toggle-sidebar").hasClass('active')) {
                            $(".lh-toggle-sidebar").removeClass('active');
                        }
                    } else {
                        if (!$(".lh-toggle-sidebar").hasClass('active')) {
                            $(".lh-toggle-sidebar").addClass('active');
                        }
                    }

                    $(".wrapper").removeClass("sb-default").addClass('sb-collapse');

                    $(".condense:not(.lh-sb-drop)").hide();
                    sidebarActiveTabs(e.type);
                }
            }
            if (sSize.max < screenSize || sSize.min >= screenSize) {
                if ($(".wrapper").hasClass("sb-collapse")) {
                    $(".lh-sidebar-overlay").fadeOut();

                    if (sSize.min >= screenSize) {
                        if ($(".lh-toggle-sidebar").hasClass('active')) {
                            $(".lh-toggle-sidebar").removeClass('active');
                        }
                    } else {
                        if (!$(".lh-toggle-sidebar").hasClass('active')) {
                            $(".lh-toggle-sidebar").addClass('active');
                        }
                    }

                    $(".wrapper").removeClass('sb-collapse').addClass("sb-default");
                    $(".condense:not(.lh-sb-drop)").show();
                    sidebarActiveTabs(e.type);
                }
            }


        });

        $(".lh-sidebar-overlay").on('click', function (e) {
            $(".lh-sidebar-overlay").fadeOut();

            $(".wrapper").toggleClass("sb-collapse sb-default");

            $(".condense:not(.lh-sb-drop)").hide();

            $(".lh-toggle-sidebar").removeClass('active');

            sidebarActiveTabs(e.type);
        });

        // On click Toggle sidebar collapse
        $(".lh-toggle-sidebar").on("click", function (e) {
            screenSize = winSizeWidth();
            if (sSize.max > screenSize) {
                $(".lh-sidebar-overlay").fadeIn();
            }
            $(".wrapper").toggleClass("sb-collapse sb-default");
            $(this).toggleClass("active");
            if ($(".wrapper").hasClass("sb-default")) {
                $(".condense").show();
                $(".lh-sb-drop").hide();

                sidebarActiveTabs(e.type);

            } else {
                if (sSize.max < screenSize) {
                    $(".condense:not(.lh-sb-drop)").hide();
                } else {
                    $(".condense:not(.lh-sb-drop)").show();
                    $(".condense.lh-sb-drop").hide();
                }
                sidebarActiveTabs(e.type);
            }

        });
        $('.lh-sidebar, .sb-collapse').on("mouseenter", function (e) {
            screenSize = winSizeWidth();
            if (sSize.max < screenSize) {
                if (!$(".wrapper").hasClass("sb-default")) {
                    $(".condense:not(.lh-sb-drop)").show();
                }
                sidebarActiveTabs(e.type);
            }
        });

        $('.lh-sidebar').on("mouseleave", function (e) {
            screenSize = winSizeWidth();
            if (sSize.max < screenSize) {
                if (!$(".wrapper").hasClass("sb-default")) {
                    $(".condense:not(.lh-sb-drop)").hide();

                }
                sidebarActiveTabs(e.type);
            }
        });

        /*========== Header tools ===========*/
        $(".lh-screen.full").on("click", function () {
            $(this).css("display", "none");
            $(".lh-screen.reset").css("display", "flex");

            // current working methods
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.documentElement.msRequestFullscreen) {
                document.documentElement.msRequestFullscreen();
            } else if (document.documentElement.mozRequestFullScreen) {
                document.documentElement.mozRequestFullScreen();
            } else if (document.documentElement.webkitRequestFullscreen) {
                document.documentElement.webkitRequestFullscreen(
                    Element.ALLOW_KEYBOARD_INPUT
                );
            }
        });
        $(".lh-screen.reset").on("click", function () {
            $(this).css("display", "none");
            $(".lh-screen.full").css("display", "flex");
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        });
        var $addLink = $('<link>', {
            rel: 'stylesheet',
            href: 'assets/css/dark.css',
            id: 'dark'
        });

        $(".lh-mode.dark").on("click", function () {
            $(this).css("display", "none");
            $(".lh-mode.light").css("display", "flex");

            $("body").attr("data-lh-mode", "dark");
            $("#mainCss").after($addLink);
            var headerModes = $(".lh-tools-item.header").attr("data-header-mode");
            if (headerModes == "light") {
                $(".lh-tools-item.header[data-header-mode='dark']").addClass("active");
                $(".lh-tools-item.header[data-header-mode='light']").removeClass("active");
                $(".lh-header").attr("data-header-mode-tool", "dark");
            }
            $(".lh-tools-item.mode[data-lh-mode-tool='light']").removeClass("active");
            $(".lh-tools-item.mode[data-lh-mode-tool='dark']").addClass("active");
        });
        $(".lh-mode.light").on("click", function () {
            $(this).css("display", "none");
            $(".lh-mode.dark").css("display", "flex");
            $(".lh-header").attr("data-header-mode-tool", "light");

            $("body").attr("data-lh-mode", "light");
            $("#dark").remove();
            var headerModes = $(".lh-tools-item.header").attr("data-header-mode");
            if (headerModes == "light") {
                $(".lh-tools-item.header[data-header-mode='light']").addClass("active");
                $(".lh-tools-item.header[data-header-mode='dark']").removeClass("active");
                $(".lh-header").attr("data-header-mode-tool", "light");
            }
            $(".lh-tools-item.mode[data-lh-mode-tool='dark']").removeClass("active");
            $(".lh-tools-item.mode[data-lh-mode-tool='light']").addClass("active");
        });

        $(".lh-notify").on("click", function () {
            $(".lh-notify-bar").addClass("lh-notify-bar-open");
            $(".lh-notify-bar-overlay").fadeIn();
        });
        $(".lh-notify-bar-overlay, .close-notify").on("click", function () {
            $(".lh-notify-bar").removeClass("lh-notify-bar-open");
            $(".lh-notify-bar-overlay").fadeOut();
        });

        $(".open-search").on("click", function () {
            $(".lh-search").fadeIn();
        });

        /*========== Vector map ===========*/
        /* Basic styling for the map */
        var regionStyling = { initial: { fill: 'rgba(121, 159, 254, .2)' }, hover: { fill: '#495567' }, selected: { fill: 'rgba(121, 159, 254, .1)' } };
        /* Data that is passed to the map */
        var gbData = {
            "IN": 6.0,
            "BR": 5.0,
            "CA": 4.0,
            "MA": 3.0,
            "TZ": 2.0,
            "AU": 1.0,
        };
        var wrld = {
            map: 'world_mill_en',
            normalizeFunction: 'polynomial',
            regionStyle: regionStyling,
            backgroundColor: 'transparent',
            markers: [
                {
                    latLng: [23.7041, 77.96],
                    name: "India",
                }, {
                    latLng: [31.7917, -7.41],
                    name: 'Morocco'
                }, {
                    latLng: [-14.2350, -51.9253],
                    name: "Brazil",
                }, {
                    latLng: [-25.2744, 133.7751],
                    name: "Australia "
                }, {
                    latLng: [56.1304, -106.3468],
                    name: "Canada"
                }, {
                    latLng: [-6.3690, 34.8888],
                    name: 'Tanzania'
                },
            ],
            markerStyle: {
                initial: {
                    r: 1,
                    fill: "transparent",
                    "fill-opacity": .3,
                    stroke: "transparent",
                    "stroke-width": 0,
                    "stroke-opacity": .6
                },
                hover: {
                    stroke: "transparent",
                    "fill-opacity": .6,
                    "stroke-width": 0
                }
            },
            series: {
                regions: [{
                    values: gbData,
                    attribute: 'fill',
                    scale: ['#9ab5ff', '#7ea0fb']
                }
                ]
            },
            onRegionTipShow: function (e, el, code) {
                el.html('In ' + el.html() + ', GB proposes ' + gbData[code] + ' products : <ul>' + getProducts(gbData[code]) + '</ul>  Click to know more');
                $(".lbl-hover").html('Hovered country value: ' + gbData[code]);
            }
        };

        /* Setting up of the map */
        if ($('#world-map').length > 0) {
            $('#world-map').vectorMap(wrld);
        }

        /*========== Search Remix icon page ===========*/
        $('[data-search-icon]').on('keyup', function () {
            var searchVal = $(this).val().toLowerCase();
            var filterItems = $('[data-search-item]');
            var filterItemsText = $('[data-search-item]').text().toLowerCase();
            var a = $('[data-search-item]:contains(' + searchVal + ')');
            if (searchVal != '') {
                filterItems.closest(".remix-unicode-icon").addClass('hide');
                $('[data-search-item]:contains(' + searchVal + ')').closest(".remix-unicode-icon").removeClass('hide');
            } else {
                filterItems.closest(".remix-unicode-icon").removeClass('hide');
            }
        });

        /*========== Search Material icon page ===========*/
        $('[data-search-material]').on('keyup', function () {
            var searchVal = $(this).val().toLowerCase();
            var filterItems = $('.material-search-item');
            var filterItemsText = $('.material-search-item').text().toLowerCase();
            var a = $('.material-search-item:contains(' + searchVal + ')');
            if (searchVal != '') {
                filterItems.closest(".material-icon-item").addClass('hide');
                $('.material-search-item:contains(' + searchVal + ')').closest(".material-icon-item").removeClass('hide');
            } else {
                filterItems.closest(".material-icon-item").removeClass('hide');
            }
        });
    });

    /*========== Booking TABLE ===========*/
    var responsiveDataTable = $("#booking_table");
    if (responsiveDataTable.length !== 0) {
        responsiveDataTable.DataTable({
            "aLengthMenu": [[5, 20, 30, 50, 75, -1], [5, 20, 30, 50, 75, "All"]],
            "pageLength": 5,
            "dom": '<"row justify-content-between top-information"lf>rt<"row justify-content-between bottom-information"ip><"clear">'
        });
    }
    /*========== Guest TABLE ===========*/
    var responsiveDataTable = $("#guest_table");
    if (responsiveDataTable.length !== 0) {
        responsiveDataTable.DataTable({
            "aLengthMenu": [[6, 20, 30, 50, 75, -1], [6, 20, 30, 50, 75, "All"]],
            "pageLength": 6,
            "dom": '<"row justify-content-between top-information"lf>rt<"row justify-content-between bottom-information"ip><"clear">'
        });
    }

    /*========== Upload image preview ===========*/
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#imageUpload").change(function () {
        readURL(this);
    });

    /*========== On click card zoom (full screen) ===========*/
    $(".lh-full-card").on("click", function () {
        $(this).hide();
        $(this).parent(".header-tools").append('<a href="javascript:void(0)" class="m-l-10 lh-full-card-close"><i class="ri-close-fill"></i></a>');
        $(this).closest(".lh-card").parent().toggleClass("lh-full-screen");
        $(this).closest(".lh-card").parent().parent().append('<div class="lh-card-overlay"></div>');
    });
    $("body").on("click", ".lh-card-overlay, .lh-full-card-close", function () {
        $(".lh-card").find(".lh-full-card-close").remove();
        $(".lh-card").find(".lh-full-card").show();
        $(".lh-card").parent().removeClass("lh-full-screen");
        $(".lh-card-overlay").remove();
        // console.log("click");
    });

    /*======== Ripple button animation ========*/
    $('.ripple-btn, .ripple-default-btn').click(function (e) {
        // Create a ripple element
        var ripple = $('<span class="ripple"></span>');

        // Append the ripple element to the button
        $(this).append(ripple);

        // Position the ripple element at the click position
        ripple.css({
            top: e.pageY - $(this).offset().top,
            left: e.pageX - $(this).offset().left
        });

        // Remove the ripple element after the animation completes
        setTimeout(function () {
            ripple.remove();
        }, 1000);
    });

    /*======== Popup alert ========*/
    $('.pop-basic').on("click", function () {
        Swal.fire('Any fool can use a computer')
    });
    $('.pop-text-under').on("click", function () {
        Swal.fire(
            'The Internet?',
            'That thing is still around?',
            'question'
        )
    });
    $('.pop-error-icon').on("click", function () {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Something went wrong!',
            footer: '<a href="">Why do I have this issue?</a>'
        })
    });
    $('.pop-long-content').on("click", function () {
        Swal.fire({
            imageUrl: 'https://placeholder.pics/svg/300x1500',
            imageHeight: 1500,
            imageAlt: 'A tall image'
        })
    });
    $('.pop-like').on("click", function () {
        Swal.fire({
            title: '<strong>HTML <u>example</u></strong>',
            icon: 'info',
            html:
                'You can use <b>bold text</b>, ' +
                '<a href="//sweetalert2.github.io">links</a> ' +
                'and other HTML tags',
            showCloseButton: true,
            showCancelButton: true,
            focusConfirm: false,
            confirmButtonText:
                '<i class="ri-thumb-up-line"></i> Great!',
            confirmButtonAriaLabel: 'Thumbs up, great!',
            cancelButtonText:
                '<i class="ri-thumb-down-line"></i>',
            cancelButtonAriaLabel: 'Thumbs down'
        })
    });
    $('.pop-save').on("click", function () {
        Swal.fire({
            title: 'Do you want to save the changes?',
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Save',
            denyButtonText: `Don't save`,
        }).then((result) => {
            /* Read more about isConfirmed, isDenied below */
            if (result.isConfirmed) {
                Swal.fire('Saved!', '', 'success')
            } else if (result.isDenied) {
                Swal.fire('Changes are not saved', '', 'info')
            }
        })
    });
    $('.pop-positioned-timeout').on("click", function () {
        Swal.fire({
            position: 'top-end',
            icon: 'success',
            title: 'Your work has been saved',
            showConfirmButton: false,
            timer: 1500
        })
    });
    $('.pop-fade-down').on("click", function () {
        Swal.fire({
            title: 'Custom animation with Animate.css',
            showClass: {
                popup: 'animate__animated animate__fadeInDown'
            },
            hideClass: {
                popup: 'animate__animated animate__fadeOutUp'
            }
        })
    });
    $('.pop-delete').on("click", function () {
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire(
                    'Deleted!',
                    'Your file has been deleted.',
                    'success'
                )
            }
        })
    });
    $('.pop-success').on("click", function () {
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
                confirmButton: 'btn btn-success',
                cancelButton: 'btn btn-danger'
            },
            buttonsStyling: false
        })
        swalWithBootstrapButtons.fire({
            title: 'Best work!',
            text: "You job is done!",
            icon: 'success',
            showCancelButton: true,
            confirmButtonText: 'Ok',
        })
    });
    $('.pop-delete-cancel').on("click", function () {
        const swalWithBootstrapButtons = Swal.mixin({
            customClass: {
                confirmButton: 'btn btn-success',
                cancelButton: 'btn btn-danger'
            },
            buttonsStyling: false
        })

        swalWithBootstrapButtons.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Yes, delete it!',
            cancelButtonText: 'No, cancel!',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                swalWithBootstrapButtons.fire(
                    'Deleted!',
                    'Your file has been deleted.',
                    'success'
                )
            } else if (
                /* Read more about handling dismissals below */
                result.dismiss === Swal.DismissReason.cancel
            ) {
                swalWithBootstrapButtons.fire(
                    'Cancelled',
                    'Your imaginary file is safe :)',
                    'error'
                )
            }
        })
    });
    $('.pop-img').on("click", function () {
        Swal.fire({
            title: 'Sweet!',
            text: 'Modal with a custom image.',
            imageUrl: 'https://unsplash.it/400/200',
            imageWidth: 400,
            imageHeight: 200,
            imageAlt: 'Custom image',
        })
    });
    $('.pop-custom').on("click", function () {
        Swal.fire({
            title: 'Custom width, padding, color, background.',
            width: 600,
            padding: '3em',
            color: '#716add',
            background: '#fff',
            backdrop: `
              rgba(0,0,123,0.4)
              left top
              no-repeat
            `
        })
    });
    $('.pop-auto-close').on("click", function () {

        let timerInterval
        Swal.fire({
            title: 'Auto close alert!',
            html: 'I will close in <b></b> milliseconds.',
            timer: 2000,
            timerProgressBar: true,
            didOpen: () => {
                Swal.showLoading()
                const b = Swal.getHtmlContainer().querySelector('b')
                timerInterval = setInterval(() => {
                    b.textContent = Swal.getTimerLeft()
                }, 100)
            },
            willClose: () => {
                clearInterval(timerInterval)
            }
        }).then((result) => {
            /* Read more about handling dismissals below */
            if (result.dismiss === Swal.DismissReason.timer) {
                // console.log('I was closed by the timer')
            }
        })
    });
    $('.pop-rtl').on("click", function () {
        Swal.fire({
            title: 'هل تريد الاستمرار؟',
            icon: 'question',
            iconHtml: '؟',
            confirmButtonText: 'نعم',
            cancelButtonText: 'لا',
            showCancelButton: true,
            showCloseButton: true
        })
    });
    $('.pop-ajax').on("click", function () {
        Swal.fire({
            title: 'Submit your Github username',
            input: 'text',
            inputAttributes: {
                autocapitalize: 'off'
            },
            showCancelButton: true,
            confirmButtonText: 'Look up',
            showLoaderOnConfirm: true,
            preConfirm: (login) => {
                return fetch(`//api.github.com/users/${login}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(response.statusText)
                        }
                        return response.json()
                    })
                    .catch(error => {
                        Swal.showValidationMessage(
                            `Request failed: ${error}`
                        )
                    })
            },
            allowOutsideClick: () => !Swal.isLoading()
        }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire({
                    title: `${result.value.login}'s avatar`,
                    imageUrl: result.value.avatar_url
                })
            }
        })
    });

    /*========== Tools Sidebar ===========*/
    $('.lh-tools-sidebar-toggle').on("click", function () {
        $('.lh-tools-sidebar').addClass("open-tools");
        $('.lh-tools-sidebar-overlay').fadeIn();
        $('.lh-tools-sidebar-toggle').hide();

    });
    $('.lh-tools-sidebar-overlay, .close-tools').on("click", function () {
        $('.lh-tools-sidebar').removeClass("open-tools");
        $('.lh-tools-sidebar-overlay').fadeOut();
        $('.lh-tools-sidebar-toggle').fadeIn();

    });

    // Mode 
    var $link = $('<link>', {
        rel: 'stylesheet',
        href: 'assets/css/dark.css',
        id: 'dark'
    });
    $('.lh-tools-item.mode').on("click", function () {
        var modes = $(this).attr("data-lh-mode-tool");
        if (modes == "light") {
            $("body").attr("data-lh-mode", "light");
            $("#dark").remove();
            var headerModes = $(".lh-tools-item.header").attr("data-header-mode");
            if (headerModes == "light") {
                $(".lh-tools-item.header[data-header-mode='light']").addClass("active");
                $(".lh-tools-item.header[data-header-mode='dark']").removeClass("active");
                $(".lh-header").attr("data-header-mode-tool", "light");
            }
            $(".lh-mode.light").css("display", "none");
            $(".lh-mode.dark").css("display", "flex");

        } else if (modes == "dark") {
            $("body").attr("data-lh-mode", "dark");
            $("#mainCss").after($link);
            var headerModes = $(".lh-tools-item.header").attr("data-header-mode");
            if (headerModes == "light") {
                $(".lh-tools-item.header[data-header-mode='dark']").addClass("active");
                $(".lh-tools-item.header[data-header-mode='light']").removeClass("active");
                $(".lh-header").attr("data-header-mode-tool", "dark");
            }
            $(".lh-mode.dark").css("display", "none");
            $(".lh-mode.light").css("display", "flex");
        }

        $(this).parents(".lh-tools-info").find('.lh-tools-item.mode').removeClass("active")
        $(this).addClass("active");
    });
    // Header 
    $('.lh-tools-item.header').on("click", function () {
        var headerModes = $(this).attr("data-header-mode");
        if (headerModes == "light") {
            $('.lh-header').attr('data-header-mode-tool', 'light');
        } else if (headerModes == "dark") {
            $('.lh-header').attr('data-header-mode-tool', 'dark');
        }
        $(this).parents(".lh-tools-info").find('.lh-tools-item.header').removeClass("active")
        $(this).addClass("active");
    });
    // Sidebar 
    $('.lh-tools-item.sidebar').on("click", function () {
        var sidebarModes = $(this).attr("data-sidebar-mode-tool");
        if (sidebarModes == "light") {
            $('.lh-sidebar').attr('data-mode', 'light');
        } else if (sidebarModes == "dark") {
            $('.lh-sidebar').attr('data-mode', 'dark');
        } else if (sidebarModes == "bg-1") {
            $('.lh-sidebar').attr('data-mode', 'bg-1');
        } else if (sidebarModes == "bg-2") {
            $('.lh-sidebar').attr('data-mode', 'bg-2');
        } else if (sidebarModes == "bg-3") {
            $('.lh-sidebar').attr('data-mode', 'bg-3');
        } else if (sidebarModes == "bg-4") {
            $('.lh-sidebar').attr('data-mode', 'bg-4');
        }
        $(this).parents(".lh-tools-info").find('.lh-tools-item.sidebar').removeClass("active")
        $(this).addClass("active");
    });
    // Backgrounds 
    $('.lh-tools-item.bg').on("click", function () {
        var bgModes = $(this).attr("data-bg-mode");
        if (bgModes == "default") {
            $('#mainBg').remove();
        } else if (bgModes == "bg-1") {
            $('#mainBg').remove();
            $("#mainCss").after("<link id='mainBg' href='assets/css/bg-1.css' rel='stylesheet'>");
        } else if (bgModes == "bg-2") {
            $('#mainBg').remove();
            $("#mainCss").after("<link id='mainBg' href='assets/css/bg-2.css' rel='stylesheet'>");
        } else if (bgModes == "bg-3") {
            $('#mainBg').remove();
            $("#mainCss").after("<link id='mainBg' href='assets/css/bg-3.css' rel='stylesheet'>");
        } else if (bgModes == "bg-4") {
            $('#mainBg').remove();
            $("#mainCss").after("<link id='mainBg' href='assets/css/bg-4.css' rel='stylesheet'>");
        } else if (bgModes == "bg-5") {
            $('#mainBg').remove();
            $("#mainCss").after("<link id='mainBg' href='assets/css/bg-5.css' rel='stylesheet'>");
        }
        $(this).parents(".lh-tools-info").find('.lh-tools-item.bg').removeClass("active")
        $(this).addClass("active");
    });
    // Box design
    $('.lh-tools-item.box').on("click", function () {
        var boxModes = $(this).attr("data-box-mode-tool");
        $("#box_design").remove();
        if (boxModes == "default") {
            $("#box_design").remove();
        } else if (boxModes == "box-1") {
            $("#mainCss").after('<link id="box_design" href="assets/css/box-1.css" rel="stylesheet">');
        } else if (boxModes == "box-2") {
            $("#mainCss").after('<link id="box_design" href="assets/css/box-2.css" rel="stylesheet">');
        } else if (boxModes == "box-3") {
            $("#mainCss").after('<link id="box_design" href="assets/css/box-3.css" rel="stylesheet">');
        }
        $(this).parents(".lh-tools-info").find('.lh-tools-item.box').removeClass("active")
        $(this).addClass("active");
    });
    /* Footer year */
    document.addEventListener("DOMContentLoaded", function() {
        const date = new Date().getFullYear(); // Get the current year
        const copyrightYearElement = document.getElementById("copyright_year");
        
        // if (copyrightYearElement) { // Check if the element exists
        //     copyrightYearElement.innerHTML = date; // Set the innerHTML
        // } else {
        //     console.error("Element with ID 'copyright_year' not found.");
        // }
    });
})(jQuery);


// deleteteamdesignation
    // $(document).on('click', '.btn-delete-designation', function() {
    //     var id = $(this).data('id');
    //     deleteDesignation(id);
    // });
        // function deleteDesignation(id) {
        //     Swal.fire({
        //         title: 'Are you sure?',
        //         text: "You won't be able to revert this action!",
        //         icon: 'warning',
        //         showCancelButton: true,
        //         confirmButtonColor: '#d33',
        //         cancelButtonColor: '#3085d6',
        //         confirmButtonText: 'Yes, delete it!'
        //     }).then((result) => {
        //         if (result.isConfirmed) {
        //             // Start the AJAX call
        //             $.ajax({
        //                 url: `/admin-panel/team-designation/${id}/delete/`,
        //                 type: 'POST',
        //                 data: {
        //                     'csrfmiddlewaretoken': '{{ csrf_token }}'
        //                 },
        //                 success: function(response) {
        //                     if (response.status === 'success') {
        //                         Swal.fire(
        //                             'Deleted!',
        //                             'Team Designation has been deleted successfully.',
        //                             'success'
        //                         );
        //                         $(`[data-member-id="${id}"]`).closest('.designation-item').fadeOut();
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please try again.',
        //                             'error'
        //                         );
        //                     }
        //                 },
        //                 error: function(xhr) {
        //                     Swal.fire(
        //                         'Error!',
        //                         'Something went wrong. Please contact support.',
        //                         'error'
        //                     );
        //                 }
        //             });
        //         }
        //     });
        // }

        // function deleteRoomType(id) {
        //     Swal.fire({
        //         title: 'Are you sure?',
        //         text: "You won't be able to undo this!",
        //         icon: 'warning',
        //         showCancelButton: true,
        //         confirmButtonColor: '#d33',
        //         cancelButtonColor: '#3085d6',
        //         confirmButtonText: 'Yes, delete it!'
        //     }).then((result) => {
        //         if (result.isConfirmed) {
        //             $.ajax({
        //                 url: `/admin-panel/room-type/${id}/delete/`, // URL to your Django delete view
        //                 type: 'POST',
        //                 data: {
        //                     'csrfmiddlewaretoken': '{{ csrf_token }}'
        //                 },
        //                 success: function(response) {
        //                     if (response.status === 'success') {
        //                         Swal.fire(
        //                             'Deleted!',
        //                             'The room type has been deleted successfully.',
        //                             'success'
        //                         );
        //                         // Remove the Room Type Card from the DOM
        //                         $(`[data-room-id="${id}"]`).fadeOut();
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please try again.',
        //                             'error'
        //                         );
        //                     }
        //                 },
        //                 error: function(xhr) {
        //                     if (xhr.status === 403) {
        //                         Swal.fire(
        //                             'Permission Denied!',
        //                             'You do not have permission to delete this.',
        //                             'error'
        //                         );
        //                     } else if (xhr.status === 404) {
        //                         Swal.fire(
        //                             'Not Found!',
        //                             'The room type does not exist.',
        //                             'error'
        //                         );
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please contact support.',
        //                             'error'
        //                         );
        //                     }
        //                 }
        //             });
        //         }
        //     });
        // }
        
        // function deleteEvent(id) {
        //     Swal.fire({
        //         title: 'Are you sure?',
        //         text: "This event will be permanently deleted!",
        //         icon: 'warning',
        //         showCancelButton: true,
        //         confirmButtonColor: '#d33',
        //         cancelButtonColor: '#3085d6',
        //         confirmButtonText: 'Yes, delete it!'
        //     }).then((result) => {
        //         if (result.isConfirmed) {
        //             $.ajax({
        //                 url: `/admin-panel/event/${id}/delete/`,
        //                 type: 'POST',
        //                 data: {
        //                     'csrfmiddlewaretoken': '{{ csrf_token }}'
        //                 },
        //                 success: function(response) {
        //                     if (response.status === 'success') {
        //                         Swal.fire(
        //                             'Deleted!',
        //                             'The event has been deleted successfully.',
        //                             'success'
        //                         );
        //                         // Remove the event card without page reload
        //                         $(`[data-event-id="${id}"]`).fadeOut();
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please try again.',
        //                             'error'
        //                         );
        //                     }
        //                 },
        //                 error: function(xhr) {
        //                     if (xhr.status === 403) {
        //                         Swal.fire(
        //                             'Permission Denied!',
        //                             'You do not have permission to delete this.',
        //                             'error'
        //                         );
        //                     } else if (xhr.status === 404) {
        //                         Swal.fire(
        //                             'Not Found!',
        //                             'The event does not exist.',
        //                             'error'
        //                         );
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please contact support.',
        //                             'error'
        //                         );
        //                     }
        //                 }
        //             });
        //         }
        //     });
        // }
        
        // function deleteFeature(id) {
        //     Swal.fire({
        //         title: 'Are you sure?',
        //         text: "This feature will be permanently deleted!",
        //         icon: 'warning',
        //         showCancelButton: true,
        //         confirmButtonColor: '#d33',
        //         cancelButtonColor: '#3085d6',
        //         confirmButtonText: 'Yes, delete it!'
        //     }).then((result) => {
        //         if (result.isConfirmed) {
        //             $.ajax({
        //                 url: `/admin-panel/feature/${id}/delete/`,
        //                 type: 'POST',
        //                 data: {
        //                     'csrfmiddlewaretoken': '{{ csrf_token }}'
        //                 },
        //                 success: function(response) {
        //                     if (response.status === 'success') {
        //                         Swal.fire(
        //                             'Deleted!',
        //                             'The feature has been deleted successfully.',
        //                             'success'
        //                         );
        //                         // Remove the feature card without page reload
        //                         $(`[data-feature-id="${id}"]`).fadeOut();
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please try again.',
        //                             'error'
        //                         );
        //                     }
        //                 },
        //                 error: function(xhr) {
        //                     if (xhr.status === 403) {
        //                         Swal.fire(
        //                             'Permission Denied!',
        //                             'You do not have permission to delete this.',
        //                             'error'
        //                         );
        //                     } else if (xhr.status === 404) {
        //                         Swal.fire(
        //                             'Not Found!',
        //                             'The feature does not exist.',
        //                             'error'
        //                         );
        //                     } else {
        //                         Swal.fire(
        //                             'Error!',
        //                             'Something went wrong. Please contact support.',
        //                             'error'
        //                         );
        //                     }
        //                 }
        //             });
        //         }
        //     });
        // }
        
        function deleteItem(url, id, itemName) {
            Swal.fire({
                title: 'Are you sure?',
                text: "You won't be able to revert this!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!'
            }).then((result) => {
                if (result.isConfirmed) {
                    $.ajax({
                        url: url,
                        type: 'POST',
                        data: {
                            'csrfmiddlewaretoken': '{{ csrf_token }}'
                        },
                        success: function(response) {
                            if (response.status === 'success') {
                                Swal.fire(
                                    'Deleted!',
                                    itemName + ' has been deleted successfully.',
                                    'success'
                                );
                                
                                // ✅ Remove the deleted item instantly from the page
                                $(`[data-item-id="${id}"]`).fadeOut('slow', function() {
                                    $(this).remove();
                                });
        
                                // ✅ Automatically refresh the list after deletion
                                setTimeout(function() {
                                    location.reload();
                                }, 1000); // Refresh after 1 second
                            } else {
                                Swal.fire(
                                    'Error!',
                                    'Something went wrong. Please try again.',
                                    'error'
                                );
                            }
                        },
                        error: function(xhr) {
                            if (xhr.status === 403) {
                                Swal.fire(
                                    'Permission Denied!',
                                    'You do not have permission to delete this.',
                                    'error'
                                );
                            } else if (xhr.status === 404) {
                                Swal.fire(
                                    'Not Found!',
                                    'The ' + itemName + ' does not exist.',
                                    'error'
                                );
                            } else {
                                Swal.fire(
                                    'Error!',
                                    'Something went wrong. Please contact support.',
                                    'error'
                                );
                            }
                        }
                    });
                }
            });
        }
        
        // document.getElementById('team-designation-form').addEventListener('submit', function(e) {
        //     e.preventDefault();
            
        //     const roomType = document.getElementById('Team Designation').value;
        //     const dateTime = document.getElementById('dateTimes').value;
    
        //     // You can handle the form submission here
        //     console.log('Room Type:', teamDesignation);
        //     console.log('Date and Time:', dateTimes);
            
        //     // Optional: Show success message
        //     alert('Booking submitted successfully!');
        //     this.reset();
        // });
        
        $(document).ready(function() {
            $("#team-designation-form").on("submit", function(event) {
                event.preventDefault();  // Prevent full page reload
        
                var formData = new FormData(this);  // Create FormData object
                var formURL = $(this).data('url');  // ✅ Fetch URL from form attribute


        
                $.ajax({
                    url: formURL,
                    type: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                        "X-CSRFToken": "{{ csrf_token }}"
                    },
                    success: function(response) {
                        if (response.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: 'Success!',
                                text: response.message || 'Team designation added successfully!',
                                showConfirmButton: false,
                                timer: 2000
                            });
        
                            // ✅ Clear the form fields
                            $("#team-designation-form")[0].reset();
        
                            // ✅ Auto-refresh the page to show the new designation
                            setTimeout(function() {
                                location.reload();
                            }, 2000);
                        } 
                        else if (response.status === 'error') {
                            Swal.fire({
                                icon: 'error',
                                title: 'Validation Error!',
                                text: response.message || "Please check the form fields.",
                            });
                        }
                    },
                    error: function(xhr) {
                        let errorMessage = "Something went wrong!";
        
                        if (xhr.responseJSON && xhr.responseJSON.error) {
                            errorMessage = xhr.responseJSON.error;
                        }
        
                        Swal.fire({
                            icon: 'error',
                            title: 'Server Error!',
                            text: errorMessage,
                        });
                    }
                });
            });
        });

        document.getElementById("room-type-form").addEventListener("submit", function(event) {
            event.preventDefault(); // Prevent full page reload
        
            let formData = new FormData(this);
            let url = this.getAttribute('data-url');

        
            fetch(url, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(response => response.json())
            .then(data => {
                // ✅ Handle success message
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: data.message || 'Room type added successfully!',
                        showConfirmButton: false,
                        timer: 2000
                    });
        
                    // ✅ Reset the form fields
                    document.getElementById("room-type-form").reset();
        
                    // ✅ Auto-refresh the page after submission
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } 
                
                // ✅ Handle form validation errors
                else if (data.errors) {
                    let errorMessage = "";
        
                    // ✅ Loop through form errors and display them in SweetAlert
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        errorMessage += `${errors.join(', ')}\n`;
                    });
        
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error!',
                        text: errorMessage,
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Server Error!',
                    text: 'Something went wrong! Please try again later.',
                });
            });
        });

        document.getElementById("eventform").addEventListener("submit", function(event) {
            event.preventDefault(); // Prevent full page reload
        
            let formData = new FormData(this);
            let url = this.getAttribute('data-url');

        
            // ✅ Prevent submission if End Date < Start Date
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            if (new Date(endDate) < new Date(startDate)) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: 'End date cannot be earlier than Start Date.',
                });
                return;
            }
        
            // ✅ Send the AJAX request using fetch API
            fetch(url, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(response => response.json())
            .then(data => {
                // ✅ Handle success response
                if (data.success === true) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: data.message,
                        showConfirmButton: false,
                        timer: 2000
                    });
        
                    // ✅ Reset the form fields
                    document.getElementById("eventform").reset();
        
                    // ✅ Auto-refresh the page after 2 seconds
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                }
                
                // ✅ Handle form validation errors
                else if (data.errors) {
                    let errorMessage = "";
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        errorMessage += `${errors.join('\n')}\n`;
                    });
        
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error!',
                        text: errorMessage,
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Server Error!',
                    text: 'Something went wrong! Please try again.',
                });
            });
        });
        
        document.addEventListener('DOMContentLoaded', function () {
            document.getElementById("featureForm").addEventListener("submit", function (event) {
                event.preventDefault();
        
                let formData = new FormData(this);
                let url = this.getAttribute('data-url');

        
                // ✅ Send the AJAX request using Fetch API
                fetch(url, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success === true) {
                        // ✅ Show SweetAlert Success
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: data.message,
                            showConfirmButton: false,
                            timer: 2000
                        });
        
                        // ✅ Reset the form fields
                        document.getElementById("featureForm").reset();
        
                        // ✅ Auto Refresh Page
                        setTimeout(() => {
                            location.reload();
                        }, 2000);
                    }
                    else if (data.errors) {
                        let errorMessage = "";
                        Object.entries(data.errors).forEach(([field, errors]) => {
                            errorMessage += `${errors.map(err => err.message).join('\n')}\n`;
                        });
        
                        // ✅ Show SweetAlert Validation Error
                        Swal.fire({
                            icon: 'error',
                            title: 'Validation Error!',
                            text: errorMessage,
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Server Error!',
                        text: 'Something went wrong! Please try again.',
                    });
                });
            });
        });
        
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = imagePreview.querySelector('img');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#1a73e8';
            dropZone.style.backgroundColor = 'rgba(26, 115, 232, 0.05)';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '#e0e0e0';
            dropZone.style.backgroundColor = 'transparent';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            const file = e.dataTransfer.files[0];
            handleFile(file);
        });

        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            handleFile(file);
        });

        function handleFile(file) {
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = () => {
                    previewImg.src = reader.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }

        
        

       
        
        
        // add rooms form in rooms1.html 

        // document.addEventListener('DOMContentLoaded', function() {
        //     const imageInput = document.querySelector('input[name="images"]');
        //     const preview = document.getElementById('imagePreview');
        //     const maxImages = 10;
            
        //     imageInput.addEventListener('change', function(event) {
        //         // Clear previous previews
        //         preview.innerHTML = '';
            
        //         const files = event.target.files;
                
        //         // Check image limit
        //         if (files.length > maxImages) {
        //             alert(`You can only upload up to ${maxImages} images.`);
        //             event.target.value = ''; // Clear the input
        //             return;
        //         }
            
        //         for (const file of files) {
        //             const reader = new FileReader();
        //             reader.onload = function(e) {
        //                 const imgContainer = document.createElement('div');
        //                 imgContainer.className = 'position-relative';
                        
        //                 const img = document.createElement('img');
        //                 img.src = e.target.result;
        //                 img.classList.add('preview-image', 'rounded');
        //                 img.style.maxWidth = '200px';
        //                 img.style.maxHeight = '200px';
        //                 img.style.objectFit = 'cover';
                        
        //                 const removeBtn = document.createElement('button');
        //                 removeBtn.innerHTML = '×';
        //                 removeBtn.type = 'button';
        //                 removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
        //                 removeBtn.onclick = function() {
        //                     imgContainer.remove();
        //                 };
                        
        //                 imgContainer.appendChild(img);
        //                 imgContainer.appendChild(removeBtn);
        //                 preview.appendChild(imgContainer);
        //             }
        //             reader.readAsDataURL(file);
        //         }
        //         });
        //     });
            
            
        //         function handleSubmit(event) {
        //             event.preventDefault();
        //             const formData = new FormData(event.target);
        //             const data = Object.fromEntries(formData.entries());
                    
        //             // Get selected features
        //             data.features = Array.from(formData.getAll('features'));
                    
        //             // Here you would typically send the data to your backend
        //             console.log('Form Data:', data);
                    
        //             // Show success message
        //             alert('Room added successfully!');
        //             event.target.reset();
        //             document.getElementById('imagePreview').innerHTML = '';
        //         }
            
        //         function resetForm() {
        //             // Reset the form
        //             document.getElementById('addRoomForm').reset();
                    
        //             // Clear image preview
        //             document.getElementById('imagePreview').innerHTML = '';
                    
        //             // Enable image input
        //             document.getElementById('imageInput').disabled = false;
                    
        //             // Reset room number display (show single room, hide bulk)
        //             document.getElementById('singleRoomNumber').style.display = 'block';
        //             document.getElementById('bulkRoomNumbers').style.display = 'none';
                    
        //             // Reset radio button to single room
        //             document.getElementById('singleRoom').checked = true;
                    
        //             // Reset required attributes
        //             document.querySelector('#singleRoomNumber input').required = true;
        //             document.querySelectorAll('#bulkRoomNumbers input').forEach(input => input.required = false);
                    
        //             // Reset room type related sections
        //             const bedTypeSection = document.getElementById('bedTypeSection');
        //             const seatingSection = document.getElementById('seatingSection');
        //             bedTypeSection.style.display = 'block';
        //             seatingSection.style.display = 'none';
                    
        //             // Reset bed type required attributes
        //             bedTypeSection.querySelectorAll('input[name="bedType"]').forEach(input => input.required = true);
        //             seatingSection.querySelector('input').required = false;
        //         }
            
        //         function editRoom(roomId) {
        //             // Change form title and button text
        //             document.querySelector('#addRoomOffcanvasLabel').textContent = 'Edit Room';
        //             document.querySelector('.btn-submit').textContent = 'Update Room';
                    
        //             // Update form action with correct URL namespace
        //             const form = document.getElementById('addRoomForm');
        //             form.action = `/admin-panel/rooms/${roomId}/edit/`;
                    
        //             // Hide bulk room options when editing
        //             document.querySelector('.radio-group').style.display = 'none';
        //             document.getElementById('bulkRoomNumbers').style.display = 'none';
        //             document.getElementById('singleRoomNumber').style.display = 'block';
                    
        //             // Add error handling for the fetch request
        //             fetch(`/admin-panel/rooms/${roomId}/edit/`)
        //                 .then(response => {
        //                     if (!response.ok) {
        //                         throw new Error('Network response was not ok');
        //                     }
        //                     return response.json();
        //                 })
        //                 .then(data => {
        //                     if (!data) {
        //                         throw new Error('No data received');
        //                     }
                            
        //                     // Populate form fields
        //                     document.querySelector('input[name="room_number"]').value = data.room_number || '';
        //                     document.querySelector('input[name="block"]').value = data.block || '';
        //                     document.querySelector('select[name="room_type"]').value = data.room_type || ''; // This line populates the room_type
        //                     document.querySelector('select[name="bed_type"]').value = data.bed_type || '';
                            
        //                     // Handle AC type radio buttons
        //                     const acTypeRadio = document.querySelector(`input[name="ac_type"][value="${data.ac_type}"]`);
        //                     if (acTypeRadio) {
        //                         acTypeRadio.checked = true;
        //                     }
                            
        //                     // Handle numeric fields
        //                     document.querySelector('input[name="base_price"]').value = data.base_price || '';
        //                     document.querySelector('input[name="weekend_price"]').value = data.weekend_price || '';
        //                     document.querySelector('input[name="holiday_price"]').value = data.holiday_price || '';
        //                     document.querySelector('input[name="hourly_price"]').value = data.hourly_price || '';
        //                     document.querySelector('input[name="max_occupancy"]').value = data.max_occupancy || '';
        //                     document.querySelector('textarea[name="description"]').value = data.description || '';
                            
        //                     // Handle features
        //                     const featureCheckboxes = document.querySelectorAll('input[name="features"]');
        //                     featureCheckboxes.forEach(checkbox => {
        //                         checkbox.checked = data.features && data.features.includes(checkbox.value);
        //                     });
                            
        //                     // Handle room type specific fields
        //                     const roomTypeSelect = document.querySelector('select[name="room_type"]');
        //                     if (data.room_type === 'conference') {
        //                         document.getElementById('bedTypeSection').style.display = 'none';
        //                         document.getElementById('seatingSection').style.display = 'block';
        //                         document.querySelector('input[name="seating_capacity"]').value = data.seating_capacity || '';
        //                     } else {
        //                         document.getElementById('bedTypeSection').style.display = 'block';
        //                         document.getElementById('seatingSection').style.display = 'none';
        //                     }
        //                     // Handle existing images
        //                     const imagePreview = document.getElementById('imagePreview');
        //                 imagePreview.innerHTML = ''; // Clear existing preview
                        
        //                 if (data.images && data.images.length > 0) {
        //                     data.images.forEach(image => {
        //                         const imgContainer = document.createElement('div');
        //                         imgContainer.className = 'position-relative d-inline-block me-2 mb-2';
                                
        //                         const img = document.createElement('img');
        //                         img.src = image.url;
        //                         img.classList.add('preview-image', 'rounded');
        //                         img.style.width = '100px';
        //                         img.style.height = '100px';
        //                         img.style.objectFit = 'cover';
                                
        //                         const removeBtn = document.createElement('button');
        //                         removeBtn.innerHTML = '×';
        //                         removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
        //                         removeBtn.onclick = function() {
        //                             if (confirm('Are you sure you want to remove this image?')) {
        //                                 imgContainer.remove();
        //                             }
        //                         };
                                
        //                         imgContainer.appendChild(img);
        //                         imgContainer.appendChild(removeBtn);
        //                         imagePreview.appendChild(imgContainer);
        //                     });
        //                 }
                            
        //                     // Trigger room type change event
        //                     roomTypeSelect.dispatchEvent(new Event('change'));
        //                 })
        //                 .catch(error => {
        //                     console.error('Error fetching room data:', error);
        //                     alert('Error loading room data. Please try again.');
        //                 });
        //         }
            
        //         function deleteRoom(roomId) {
        //             if (confirm('Are you sure you want to delete this room? This action cannot be undone.')) {
        //                 // Get CSRF token from the cookie
        //                 function getCookie(name) {
        //                     let cookieValue = null;
        //                     if (document.cookie && document.cookie !== '') {
        //                         const cookies = document.cookie.split(';');
        //                         for (let i = 0; i < cookies.length; i++) {
        //                             const cookie = cookies[i].trim();
        //                             if (cookie.substring(0, name.length + 1) === (name + '=')) {
        //                                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        //                                 break;
        //                             }
        //                         }
        //                     }
        //                     return cookieValue;
        //                 }
        //                 const csrftoken = getCookie('csrftoken');
            
        //                 // Make the delete request
        //                 fetch(`/admin-panel/rooms/${roomId}/delete/`, {
        //                     method: 'POST',
        //                     headers: {
        //                         'X-CSRFToken': csrftoken,
        //                         'Content-Type': 'application/json',
        //                     },
        //                     credentials: 'same-origin'  // This is important for cookies
        //                 })
        //                 .then(response => {
        //                     if (!response.ok) {
        //                         throw new Error('Network response was not ok');
        //                     }
        //                     return response.json();
        //                 })
        //                 .then(data => {
        //                     if (data.success) {
        //                         // Show success message using Bootstrap toast or alert
        //                         alert('Room deleted successfully!');
        //                         // Reload the page to reflect changes
        //                         window.location.reload();
        //                     } else {
        //                         alert('Error deleting room: ' + (data.error || 'Unknown error'));
        //                     }
        //                 })
        //                 .catch(error => {
        //                     console.error('Error:', error);
        //                     alert('Error deleting room. Please try again.');
        //                 });
        //             }
        //         }

        //         document.getElementById('addRoomForm').addEventListener('submit', function(event) {
        //             event.preventDefault(); // Prevent the default form submission
            
        //             const formData = new FormData(this);
            
        //             fetch(this.action, {
        //                 method: 'POST',
        //                 body: formData,
        //                 headers: {
        //                     'X-CSRFToken': '{{ csrf_token }}' // Include CSRF token
        //                 }
        //             })
        //             .then(response => response.json())
        //             .then(data => {
        //                 if (data.success === false) {
        //                     // Show SweetAlert for error message
        //                     Swal.fire({
        //                         icon: 'error',
        //                         title: 'Error',
        //                         text: data.message,
        //                         confirmButtonText: 'OK'
        //                     });
        //                 } else {
        //                     // Show success message
        //                     Swal.fire({
        //                         icon: 'success',
        //                         title: 'Success',
        //                         text: 'Room added successfully!',
        //                         confirmButtonText: 'OK'
        //                     }).then(() => {
        //                         window.location.href = "{% url 'admin-panel:room_list' %}"; // Redirect to rooms page
        //                     });
        //                 }
        //             })
        //             .catch(error => {
        //                 console.error('Error:', error);
        //                 Swal.fire({
        //                     icon: 'error',
        //                     title: 'Error',
        //                     text: 'An unexpected error occurred. Please try again.',
        //                     confirmButtonText: 'OK'
        //                 });
        //             });
        //         });
        

        // $(document).ready(function () {
		// 	function fetchRoomData() {
		// 		$.ajax({
		// 			url: "{% url 'admin-panel:fetch_room_data' %}",
		// 			type: "GET",
		// 			dataType: "json",
		// 			success: function (response) {
		// 				let roomTypeSelect = $("select[name='room_type']");

		// 				roomTypeSelect.empty();
		// 				roomTypeSelect.append(`<option value="">Select Room Type</option>`);

		// 				$.each(response.room_types, function (index, roomType) {
		// 					console.log("Room Type:", roomType.name, "| Bed Type:", roomType.bed_type);

		// 					roomTypeSelect.append(`
        //                         <option value="${roomType.id}" data-bedtype="${roomType.bed_type}">
        //                             ${roomType.name}
        //                         </option>
        //                     `);
		// 				});

		// 				toggleFields(); // Run toggleFields after populating room types
		// 			}
		// 		});
		// 	}

		// 	function toggleFields() {
		// 		var selectedBedType = $("#id_room_type option:selected").attr("data-bedtype")?.trim().toLowerCase() || "";

		// 		console.log("Selected Bed Type:", selectedBedType);

		// 		if (selectedBedType === "conference") {
		// 			$("#seatingSection").removeClass("hidden");  // Show Seating Capacity
		// 			$("#bedTypeSection").addClass("hidden");  // Hide Bed Type
		// 		} else {
		// 			$("#seatingSection").addClass("hidden");  // Hide Seating Capacity
		// 			$("#bedTypeSection").removeClass("hidden");  // Show Bed Type
		// 		}
		// 	}

		// 	// Trigger toggleFields when room type changes
		// 	$("#id_room_type").change(()=>{
		// 		console.log("changed value");
		// 	});

		// 	// Fetch room data on page load
		// 	fetchRoomData();
		// });

		document.addEventListener('DOMContentLoaded', function () {
			const singleRoom = document.getElementById('singleRoom');
			const bulkRooms = document.getElementById('bulkRooms');
			const singleRoomNumber = document.getElementById('singleRoomNumber');
			const bulkRoomNumbers = document.getElementById('bulkRoomNumbers');

			function toggleRoomNumberInputs() {
				if (singleRoom.checked) {
					console.log("Single Room selected.");
					singleRoomNumber.style.display = 'block';
					bulkRoomNumbers.style.display = 'none';
					singleRoomNumber.querySelector('input').required = true;
					bulkRoomNumbers.querySelectorAll('input').forEach(input => {
						input.required = false;
						input.value = ''; // Clear hidden values
					});
				} else {
					console.log("Bulk Rooms selected.");
					singleRoomNumber.style.display = 'none';
					bulkRoomNumbers.style.display = 'block';
					singleRoomNumber.querySelector('input').required = false;
					bulkRoomNumbers.querySelectorAll('input').forEach(input => input.required = true);
				}
			}

			singleRoom.addEventListener('change', toggleRoomNumberInputs);
			bulkRooms.addEventListener('change', toggleRoomNumberInputs);

			// Add this new code for room type handling
			// const roomType = document.getElementById('room_type');
			// const bedTypeSection = document.getElementById('bedTypeSection');
			// const seatingSection = document.getElementById('seatingSection');
			// const bedTypeInputs = bedTypeSection.querySelectorAll('input[name="bed_type"]');

			// document.addEventListener('DOMContentLoaded', function() {
			// 	function toggleFields() {
			// 		var selectedRoomType = $("#room_type option:selected").text().toLowerCase();
			// 		var selectedBedType = $("#bed_type option:selected").text().toLowerCase();

			// 		if (selectedRoomType.includes("conference") || selectedBedType.includes("conference")) {
			// 			$("#seating_capacity").closest(".form-group").show();  // Show Seating Capacity
			// 			$("#bedTypeSection").hide();  // Hide Bed Type
			// 		} else {
			// 			$("#seating_capacity").closest(".form-group").hide();
			// 			$("#bedTypeSection").show();  // Show Bed Type
			// 		}
			// 	}

			// 	// Run on page load
			// 	toggleFields();

			// 	// Run when the dropdown value changes
			// 	$("#room_type, #bed_type").change(function () {
			// 		toggleFields();
			// 	});
			// });
		})
		function previewImages(event) {
			const preview = document.getElementById('imagePreview');
			const files = event.target.files;
			const maxImages = 10;
			const existingImages = preview.children.length;
			const remainingSlots = maxImages - existingImages;

			// Check if adding new images would exceed the limit
			if (files.length > remainingSlots) {
				alert(`You can only upload up to ${maxImages} images. You have ${existingImages} images already.`);
				event.target.value = ''; // Clear the input
				return;
			}

			for (const file of files) {
				const reader = new FileReader();
				reader.onload = function (e) {
					const imgContainer = document.createElement('div');
					imgContainer.className = 'position-relative';

					const img = document.createElement('img');
					img.src = e.target.result;
					img.classList.add('preview-image', 'rounded');

					const removeBtn = document.createElement('button');
					removeBtn.innerHTML = '×';
					removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
					removeBtn.onclick = function () {
						imgContainer.remove();
						// Enable input if images are less than max
						const imageInput = document.getElementById('imageInput');
						if (preview.children.length < maxImages) {
							imageInput.disabled = false;
						}
					};

					imgContainer.appendChild(img);
					imgContainer.appendChild(removeBtn);
					preview.appendChild(imgContainer);

					// Disable input if max images reached
					if (preview.children.length >= maxImages) {
						document.getElementById('imageInput').disabled = true;
					}
				}
				reader.readAsDataURL(file);
			}
		}

		function handleSubmit(event) {
			event.preventDefault();
			const formData = new FormData(event.target);
			const data = Object.fromEntries(formData.entries());

			// Get selected features
			data.features = Array.from(formData.getAll('features'));

			// Here you would typically send the data to your backend
			console.log('Form Data:', data);

			// Show success message
			alert('Room added successfully!');
			event.target.reset();
			document.getElementById('imagePreview').innerHTML = '';
		}

		function resetForm() {
			// Reset the form
			document.getElementById('addRoomForm').reset();

			// Clear image preview
			document.getElementById('imagePreview').innerHTML = '';

			// Enable image input
			document.getElementById('imageInput').disabled = false;

			// Reset room number display (show single room, hide bulk)
			document.getElementById('singleRoomNumber').style.display = 'block';
			document.getElementById('bulkRoomNumbers').style.display = 'none';

			// Reset radio button to single room
			document.getElementById('singleRoom').checked = true;

			// Reset required attributes
			document.querySelector('#singleRoomNumber input').required = true;
			document.querySelectorAll('#bulkRoomNumbers input').forEach(input => input.required = false);

			// Reset room type related sections
			const bedTypeSection = document.getElementById('bedTypeSection');
			const seatingSection = document.getElementById('seatingSection');
			bedTypeSection.style.display = 'block';
			seatingSection.style.display = 'none';

			// Reset bed type required attributes
			bedTypeSection.querySelectorAll('input[name="bedType"]').forEach(input => input.required = true);
			seatingSection.querySelector('input').required = false;
		}

		function editRoom(roomId) {
			// Change form title and button text
			document.querySelector('#addRoomOffcanvasLabel').textContent = 'Edit Room';
			document.querySelector('.btn-submit').textContent = 'Update Room';

			// Update form action with correct URL namespace
			const form = document.getElementById('addRoomForm');
			form.action = `/admin-panel/rooms/${roomId}/edit/`;

			// Hide bulk room options when editing
			document.querySelector('.radio-group').style.display = 'none';
			document.getElementById('bulkRoomNumbers').style.display = 'none';
			document.getElementById('singleRoomNumber').style.display = 'block';

			// Add error handling for the fetch request
			fetch(`/admin-panel/rooms/${roomId}/edit/`)
				.then(response => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}
					return response.json();
				})
				.then(data => {
					if (!data) {
						throw new Error('No data received');
					}

					// Populate form fields
					document.querySelector('input[name="room_number"]').value = data.room_number || '';
					document.querySelector('input[name="block"]').value = data.block || '';
					document.querySelector('select[name="room_type"]').value = data.room_type || ''; // This line populates the room_type
					document.querySelector('select[name="bed_type"]').value = data.bed_type || '';

					// Handle AC type radio buttons
					const acTypeRadio = document.querySelector(`input[name="ac_type"][value="${data.ac_type}"]`);
					if (acTypeRadio) {
						acTypeRadio.checked = true;
					}

					// Handle numeric fields
					document.querySelector('input[name="base_price"]').value = data.base_price || '';
					document.querySelector('input[name="weekend_price"]').value = data.weekend_price || '';
					document.querySelector('input[name="holiday_price"]').value = data.holiday_price || '';
					document.querySelector('input[name="hourly_price"]').value = data.hourly_price || '';
					document.querySelector('input[name="max_occupancy"]').value = data.max_occupancy || '';
					document.querySelector('textarea[name="description"]').value = data.description || '';

					// Handle features
					const featureCheckboxes = document.querySelectorAll('input[name="features"]');
					featureCheckboxes.forEach(checkbox => {
						checkbox.checked = data.features && data.features.includes(checkbox.value);
					});

					// Handle room type specific fields
					const roomTypeSelect = document.querySelector('select[name="room_type"]');
					if (data.room_type === 'conference') {
						document.getElementById('bedTypeSection').style.display = 'none';
						document.getElementById('seatingSection').style.display = 'block';
						document.querySelector('input[name="seating_capacity"]').value = data.seating_capacity || '';
					} else {
						document.getElementById('bedTypeSection').style.display = 'block';
						document.getElementById('seatingSection').style.display = 'none';
					}
					// Handle existing images
					const imagePreview = document.getElementById('imagePreview');
					imagePreview.innerHTML = ''; // Clear existing preview

					if (data.images && data.images.length > 0) {
						data.images.forEach(image => {
							const imgContainer = document.createElement('div');
							imgContainer.className = 'position-relative d-inline-block me-2 mb-2';

							const img = document.createElement('img');
							img.src = image.url;
							img.classList.add('preview-image', 'rounded');
							img.style.width = '100px';
							img.style.height = '100px';
							img.style.objectFit = 'cover';

							const removeBtn = document.createElement('button');
							removeBtn.innerHTML = '×';
							removeBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0';
							removeBtn.onclick = function () {
								if (confirm('Are you sure you want to remove this image?')) {
									imgContainer.remove();
								}
							};

							imgContainer.appendChild(img);
							imgContainer.appendChild(removeBtn);
							imagePreview.appendChild(imgContainer);
						});
					}

					// Trigger room type change event
					roomTypeSelect.dispatchEvent(new Event('change'));
				})
				.catch(error => {
					console.error('Error fetching room data:', error);
					alert('Error loading room data. Please try again.');
				});
		}

		function deleteRoom(roomId) {
			if (confirm('Are you sure you want to delete this room? This action cannot be undone.')) {
				// Get CSRF token from the cookie
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
				const csrftoken = getCookie('csrftoken');

				// Make the delete request
				fetch(`/admin-panel/rooms/${roomId}/delete/`, {
					method: 'POST',
					headers: {
						'X-CSRFToken': csrftoken,
						'Content-Type': 'application/json',
					},
					credentials: 'same-origin'  // This is important for cookies
				})
					.then(response => {
						if (!response.ok) {
							throw new Error('Network response was not ok');
						}
						return response.json();
					})
					.then(data => {
						if (data.success) {
							// Show success message using Bootstrap toast or alert
							alert('Room deleted successfully!');
							// Reload the page to reflect changes
							window.location.reload();
						} else {
							alert('Error deleting room: ' + (data.error || 'Unknown error'));
						}
					})
					.catch(error => {
						console.error('Error:', error);
						alert('Error deleting room. Please try again.');
					});
			}
		}

		document.getElementById('addRoomForm').addEventListener('submit', function (event) {
			event.preventDefault(); // Prevent the default form submission

			const formData = new FormData(this);

			fetch(this.action, {
				method: 'POST',
				body: formData,
				headers: {
					'X-CSRFToken': '{{ csrf_token }}' // Include CSRF token
				}
			})
				.then(response => response.json())
				.then(data => {
					if (data.success === false) {
						// Show SweetAlert for error message
						Swal.fire({
							icon: 'error',
							title: 'Error',
							text: data.message,
							confirmButtonText: 'OK'
						});
					} else {
						// Show success message
						Swal.fire({
							icon: 'success',
							title: 'Success',
							text: 'Room added successfully!',
							confirmButtonText: 'OK'
						}).then(() => {
							window.location.href = "{% url 'admin-panel:room_list' %}"; // Redirect to rooms page
						});
					}
				})
				.catch(error => {
					console.error('Error:', error);
					Swal.fire({
						icon: 'error',
						title: 'Error',
						text: 'An unexpected error occurred. Please try again.',
						confirmButtonText: 'OK'
					});
				});
		});

       
        
        

        document.addEventListener('DOMContentLoaded', function () {
            const spaForm = document.getElementById('spaForm');
            const imageInput = document.getElementById('image');
            const imagePreview = document.getElementById('imagePreview');
            const imagePreviewText = document.getElementById('imagePreviewText');
        
            // Image preview functionality
            imageInput.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        imagePreview.src = e.target.result;
                        imagePreview.style.display = 'block';
                        imagePreviewText.style.display = 'none';
                    };
                    reader.readAsDataURL(file);
                } else {
                    imagePreview.style.display = 'none';
                    imagePreviewText.style.display = 'block';
                }
            });
        
            // Form submission with debugging
            spaForm.addEventListener('submit', function (event) {
                event.preventDefault(); // Prevent default form submission
                console.log('Form submission intercepted'); // Debug: Confirm this runs
        
                let formData = new FormData(spaForm);
                console.log('Form action URL:', spaForm.action); // Debug: Check the URL
        
                // fetch(spaForm.action, {
                //     method: 'POST',
                //     body: formData,
                //     headers: {
                //         'X-Requested-With': 'XMLHttpRequest' // Indicate AJAX request
                //     }
                // })
                // .then(response => {
                //     console.log('Response received:', response); // Debug: Check response
                //     if (!response.ok) {
                //         throw new Error('Network response was not ok');
                //     }
                //     return response.json(); // Parse JSON response
                // })
                // .then(data => {
                //     console.log('Parsed data:', data); // Debug: Log the parsed response
        
                //     if (data.status === 'success') {
                //         Swal.fire({
                //             icon: 'success',
                //             title: 'Success!',
                //             text: data.message
                //         });
                //         // Add the new item to the list (if applicable)
                //         addListItem(
                //             formData.get('name'),
                //             formData.get('fromTime'),
                //             formData.get('toTime'),
                //             formData.get('description'),
                //             document.getElementById('image').files[0]
                //         );
        
                //         // Reset form
                //         spaForm.reset();
                //         imagePreview.style.display = 'none';
                //         imagePreviewText.style.display = 'block';
                //     } else {
                //         Swal.fire({
                //             icon: 'error',
                //             title: 'Error!',
                //             text: data.message
                //         });
                //     }
                // })
                // .catch(error => {
                //     console.error('Fetch error:', error); // Debug: Log any errors
                //     Swal.fire({
                //         icon: 'error',
                //         title: 'Oops...',
                //         text: 'Something went wrong! Please try again.'
                //     });
                // });
            });
        });
        
        // Function to format time for display
        function formatTime(time) {
            if (!time) return '--:--';
            const [hours, minutes] = time.split(':');
            const hour = parseInt(hours);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const formattedHour = hour % 12 || 12;
            return `${formattedHour}:${minutes} ${ampm}`;
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const serviceForm = document.getElementById('serviceForm');
            const iconUpload = document.getElementById('iconUpload');
            const imageUpload = document.getElementById('imageUpload');
            const iconPreview = document.getElementById('iconPreview');
            const imagePreview = document.getElementById('imagePreview');
            const resetBtn = document.getElementById('resetBtn');

            // Preview functions
            function handleFilePreview(file, previewElement, isIcon) {
                if (file) {
                    // Validate file size
                    const maxSize = isIcon ? 1024 * 1024 : 5 * 1024 * 1024;
                    if (file.size > maxSize) {
                        Swal.fire({
                            icon: 'error',
                            title: 'File Too Large',
                            text: `File size must be less than ${isIcon ? '1MB' : '5MB'}`
                        });
                        return false;
                    }

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewElement.innerHTML = `<img src="${e.target.result}" class="img-fluid ${isIcon ? 'icon-img' : 'preview-img'}" alt="preview">`;
                    };
                    reader.readAsDataURL(file);
                    return true;
                }
                return false;
            }

            // File upload previews
            iconUpload.addEventListener('change', function() {
                handleFilePreview(this.files[0], iconPreview, true);
            });

            imageUpload.addEventListener('change', function() {
                handleFilePreview(this.files[0], imagePreview, false);
            });

            // Form submission
            serviceForm.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(serviceForm);

                // Show loading state
                const submitBtn = serviceForm.querySelector('button[type="submit"]');
                const originalBtnText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
                submitBtn.disabled = true;

                fetch('/admin-panel/save-service/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: data.message
                        });
                        serviceForm.reset();
                        iconPreview.innerHTML = '<i class="fas fa-upload fa-2x text-muted"></i>';
                        imagePreview.innerHTML = '<i class="fas fa-image fa-3x text-muted"></i>';
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error!',
                            text: data.message
                        });
                    }
                })
                .catch(error => {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: 'Something went wrong! Please try again.'
                    });
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Reset button state
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                });

                // Manually trigger the form submission event
                const submitEvent = new Event('submit', {
                    bubbles: true,
                    cancelable: true,
                });
                serviceForm.dispatchEvent(submitEvent);
            });

            // Reset button handler
            resetBtn.addEventListener('click', function() {
                serviceForm.reset();
                iconPreview.innerHTML = '<i class="fas fa-upload fa-2x text-muted"></i>';
                imagePreview.innerHTML = '<i class="fas fa-image fa-3x text-muted"></i>';
            });
        });
        

        // document.addEventListener("DOMContentLoaded", function () {
        //     const aboutUsForm = document.getElementById("aboutUsForm");
        //     const fileUpload = document.getElementById("file-upload");
        //     const titleInput = document.getElementById("title");
        //     const descriptionInput = document.getElementById("description");
        //     const fileName = document.getElementById("file-name");
        //     const previewImage = document.getElementById("preview-image");
    
        //     // Show selected file name
        //     fileUpload.addEventListener("change", () => {
        //         const file = fileUpload.files[0];
        //         fileName.textContent = file ? file.name : "No file chosen";
    
        //         // Image preview logic
        //         if (file) {
        //             const reader = new FileReader();
        //             reader.onload = function (e) {
        //                 previewImage.src = e.target.result;
        //                 previewImage.style.display = "block";
        //             };
        //             reader.readAsDataURL(file);
        //         } else {
        //             previewImage.src = "";
        //             previewImage.style.display = "none";
        //         }
        //     });
    
        //     // Submit handler
        //     aboutUsForm.addEventListener("submit", function (e) {
        //         e.preventDefault();
        //         console.log("Form submission initiated.");

        //         // Basic validations
        //         if (fileUpload.files.length === 0) {
        //             Swal.fire({
        //                 icon: "error",
        //                 title: "Oops...",
        //                 text: "Please upload an image before submitting!",
        //             });
        //             return;
        //         }
    
        //         if (!titleInput.value.trim()) {
        //             Swal.fire({
        //                 icon: "error",
        //                 title: "Validation Error",
        //                 text: "Title is required!",
        //             });
        //             return;
        //         }
    
        //         if (!descriptionInput.value.trim()) {
        //             Swal.fire({
        //                 icon: "error",
        //                 title: "Validation Error",
        //                 text: "Description is required!",
        //             });
        //             return;
        //         }
    
        //         const formData = new FormData(aboutUsForm);
        //         console.log("FormData created.");

        //         // Optional loading state
        //         Swal.fire({
        //             title: "Submitting...",
        //             didOpen: () => Swal.showLoading(),
        //             allowOutsideClick: false,
        //             allowEscapeKey: false,
        //             showConfirmButton: false
        //         });
    
        //         fetch("/admin-panel/save-about-us/", {
        //             method: "POST",
        //             body: formData,
        //             headers: {
        //                 "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        //             },
        //         })
        //         .then((response) => {
        //             if (!response.ok) {
        //                 throw new Error("Network response was not OK");
        //             }
        //             return response.json();
        //         })
        //         .then((data) => {
        //             if (data.success) {
        //                 Swal.fire({
        //                     icon: "success",
        //                     title: "Success!",
        //                     text: data.message,
        //                 }).then(() => {
        //                     aboutUsForm.reset();
        //                     resetImagePreview();
        //                 });
        //             } else {
        //                 console.error("Server returned error:", data.errors);
        //                 Swal.fire({
        //                     icon: "error",
        //                     title: "Error!",
        //                     text: data.message,
        //                 });
        //             }
        //         })
        //         .catch((error) => {
        //             console.error("Fetch error:", error);
        //             Swal.fire({
        //                 icon: "error",
        //                 title: "Oops...",
        //                 text: "Something went wrong! Please check console.",
        //             });
        //         });
        //     });
    
        //     // Reset image preview
        //     function resetImagePreview() {
        //         fileName.textContent = "No file chosen";
        //         fileUpload.value = "";
        //         previewImage.src = "";
        //         previewImage.style.display = "none";
        //     }
    
        //     // Global JS error catcher
        //     window.addEventListener("error", function (e) {
        //         console.error("Global JS Error:", e.message);
        //     });
    
        //     // Reset button functionality
        //     document.getElementById("resetBtn").addEventListener("click", function () {
        //         aboutUsForm.reset();
        //         resetImagePreview();
        //     });
        // });
    
// document.addEventListener("DOMContentLoaded", function () {
//     const aboutUsForm = document.getElementById("aboutUsForm");
//     if (!aboutUsForm) {
//         console.error("Form not found!");
//         return;
//     }

//     const fileUpload = document.getElementById("file-upload");
//     const titleInput = document.getElementById("title");
//     const descriptionInput = document.getElementById("description");
//     const fileName = document.getElementById("file-name");

//     aboutUsForm.addEventListener("submit", function (e) {
//         e.preventDefault();

//         console.log("Submit event triggered");

//         // Validate File Input
//         if (fileUpload.files.length === 0) {
//             Swal.fire({
//                 icon: "error",
//                 title: "Oops...",
//                 text: "Please upload an image before submitting!",
//             });
//             return;
//         }

//         // Validate Title
//         if (!titleInput.value.trim()) {
//             Swal.fire({
//                 icon: "error",
//                 title: "Validation Error",
//                 text: "Title is required!",
//             });
//             return;
//         }

//         // Validate Description
//         if (!descriptionInput.value.trim()) {
//             Swal.fire({
//                 icon: "error",
//                 title: "Validation Error",
//                 text: "Description is required!",
//             });
//             return;
//         }

//         let formData = new FormData(aboutUsForm);
//         console.log("FormData prepared, sending fetch...");

//         fetch("/admin-panel/about-us-submit/", {
//             method: "POST",
//             body: formData,
//             headers: {
//                 "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
//             },
//         })
//         .then((response) => {
//             console.log("Fetch response received:", response);
//             return response.json();
//         })
//         .then((data) => {
//             console.log("Data received:", data);
//             if (data.success) {
//                 Swal.fire({
//                     icon: "success",
//                     title: "Success!",
//                     text: data.message,
//                 }).then(() => {
//                     aboutUsForm.reset();
//                     resetImagePreview();
//                 });
//             } else {
//                 Swal.fire({
//                     icon: "error",
//                     title: "Error!",
//                     text: data.message,
//                 });
//             }
//         })
//         .catch((error) => {
//             console.error("Fetch error:", error);
//             Swal.fire({
//                 icon: "error",
//                 title: "Oops...",
//                 text: "Something went wrong! Please try again.",
//             });
//         });
//     });

//     function resetImagePreview() {
//         fileName.textContent = "No file chosen";
//         fileUpload.value = "";
//         document.getElementById("preview-image").src = "#";
//     }
// });
