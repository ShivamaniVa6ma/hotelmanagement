var currentPropertyType = 1;
var packageTaxPercent = 18;
var disableBuyButton = true;
var apiDomain = 'https://api.exceedhms.com';

//Methods For Hotel

var inputRoomCount = $('#inputRoomCount');
var inputTogglePeriod = $('#inputTogglePeriod');
var inputCurrency = $('#inputCurrency');
var annualDiscPer = 10;
var pricingHotelINR =
    [
        {
            Id: 'section-classic',
            Name: 'Classic',
            BasePrice: 2200,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 100,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 40 },
                    { MinQty: 26, MaxQty: 50, Incremental: 40 },
		    { MinQty: 51, MaxQty: 100, Incremental: 40 },
 		    { MinQty: 101, MaxQty: 200, Incremental: 40 }
                ]
        },
        {
            Id: 'section-gold',
            Name: 'Gold',
            BasePrice: 2800,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 200,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 50 },
                    { MinQty: 26, MaxQty: 50, Incremental: 50 },
 		    { MinQty: 51, MaxQty: 100, Incremental: 50 },
		    { MinQty: 101, MaxQty: 200, Incremental: 50 }

                ]
        },
        {
            Id: 'section-platinum',
            Name: 'Platinum',
            BasePrice: 3200,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 300,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 60 },
                    { MinQty: 26, MaxQty: 50, Incremental: 60 },
		    { MinQty: 51, MaxQty: 100, Incremental: 60 },
		    { MinQty: 101, MaxQty: 200, Incremental: 60 }
                ]
        },
        {
            Id: 'section-diamond',
            Name: 'Diamond',
            BasePrice: 4200,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 400,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 100 },
                    { MinQty: 26, MaxQty: 50, Incremental: 100 },
		    { MinQty: 51, MaxQty: 100, Incremental: 100 },
		    { MinQty: 101, MaxQty: 200, Incremental: 100 }

	        ]
        }
    ];
var pricingHotelUSD =
    [
        {
            Id: 'section-classic',
            Name: 'Classic',
            BasePrice: 50,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 5,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 1 },
                    { MinQty: 26, MaxQty: 50, Incremental: 1 },
  		   { MinQty: 51, MaxQty: 100, Incremental: 1 },
		    { MinQty: 101, MaxQty: 200, Incremental: 1 }
                ]
        },
        {
            Id: 'section-gold',
            Name: 'Gold',
            BasePrice: 80,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 5,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 1.5 },
                    { MinQty: 26, MaxQty: 50, Incremental: 1.5 },
  		   { MinQty: 51, MaxQty: 100, Incremental: 1.5 },
		    { MinQty: 101, MaxQty: 200, Incremental: 1.5 }
                ]
        },
        {
            Id: 'section-platinum',
            Name: 'Platinum',
            BasePrice: 110,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 5,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 2 },
                    { MinQty: 26, MaxQty: 50, Incremental: 2 },
  		   { MinQty: 51, MaxQty: 100, Incremental: 2 },
		    { MinQty: 101, MaxQty: 200, Incremental: 2 }
                ]
        },
        {
            Id: 'section-diamond',
            Name: 'Diamond',
            BasePrice: 140,
            BaseQty: 10,
            MaxQty: 200,
            MinIncremental: 5,
            Plan:
                [
                    { MinQty: 11, MaxQty: 25, Incremental: 2.5 },
                    { MinQty: 26, MaxQty: 50, Incremental: 2.5 },
  		   { MinQty: 51, MaxQty: 100, Incremental: 2.5 },
		    { MinQty: 101, MaxQty: 200, Incremental: 2.5 }
 		]
        }
    ];
var pricingAddonHotel =
    [
        {
            IsActive: true,
            IncludeInPayment: true,
            Id: 'SMSModule',
            Name: 'Whatsapp Interface',
            Title: 'Whatsapp Interface Interface (per month)',
            AmountINR: '₹1500',
            AmountUSD: '$30',
            PaymentAmountINR: 18000,
            PaymentAmountUSD: 240
        },
        {
            IsActive: true,
            IncludeInPayment: true,
            Id: 'TallyModule',
            Name: 'Financial Accounting Interface',
            Title: 'Financial Tally accounting Interface (per month)',
            AmountINR: '₹2000',
            AmountUSD: '$30',
            PaymentAmountINR: 24000,
            PaymentAmountUSD: 300
        },
        {
            IsActive: true,
            IncludeInPayment: true,
            Id: 'PaymentGatewayModule',
            Name: 'Payment Gateway Interface',
            Title: 'Payment Gateway Interface (per month)',
            AmountINR: '₹1500',
            AmountUSD: '$30',
            PaymentAmountINR: 18000,
            PaymentAmountUSD: 240
        },
        {
            IsActive: true,
            IncludeInPayment: false,
            Id: 'ChannelManagerModule',
            Name: 'Channel Manager',
            Title: 'Channel Manager  (per month)',
            AmountINR: '₹3500 / Property / Month',
            AmountUSD: '$70 / Property / Month',
            PaymentAmountINR: 3500,
            PaymentAmountUSD: 70

        },
    {
            IsActive: true,
            IncludeInPayment: false,
            Id: 'BookingEngine',
            Name: 'Booking Engine',
            Title: 'Booking Engine  (per month)',
            AmountINR: '₹2000 / Property / Month',
            AmountUSD: '$50 / Property / Month',
            PaymentAmountINR: 2000,
            PaymentAmountUSD: 50

        },
        {
            IsActive: true,
            IncludeInPayment: false,
            Id: '',
            Name: '',
            Title: 'Bloom UpUltimate - Desktop Hotel Software',
            AmountINR: 'Contact us to learn about pricing',
            AmountUSD: 'Contact us to learn about pricing',
            PaymentAmountINR: 0,
            PaymentAmountUSD: 0
        }
    ];


document.addEventListener("DOMContentLoaded", function () {
        window.TogglePeriodHotel = function (checkbox) {
            let yearly = checkbox.checked;
            let url = `/subscription/fetch-pricing/?yearly=${yearly}`;
    
            console.log("Fetching:", url); // Debugging
    
            fetch(url)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log("Received Data:", data); // Debugging
    
                    if (data.pricing) {
                        Object.keys(data.pricing).forEach((planId) => {
                            let planData = data.pricing[planId];
                            console.log(`Plan ${planId} Data:`, planData); // Debugging
    
                            if (typeof planData.discounted_price !== "number" || typeof planData.original_price !== "number") {
                                console.error(`Invalid price data for plan ${planId}:`, planData);
                                return; // Skip updating UI if data is invalid
                            }
    
                            // Find UI elements
                            let priceElement = document.querySelector(`#section-${planId} .price-discounted`);
                            let originalPriceElement = document.querySelector(`#section-${planId} .price-original`);
    
                            if (priceElement) {
                                priceElement.innerText = `₹${planData.discounted_price.toFixed(2)}`;
                            }
    
                            if (originalPriceElement) {
                                if (yearly) {
                                    originalPriceElement.innerHTML = `<s>₹${planData.original_price.toFixed(2)}</s>`; // Strikethrough
                                    originalPriceElement.style.display = "inline"; // Show strikethrough price
                                } else {
                                    originalPriceElement.innerText = `₹${planData.original_price.toFixed(2)}`;
                                    originalPriceElement.style.display = "none"; // Hide when monthly is selected
                                }
                            }
                        });
                    } else {
                        console.error("Error: Pricing data missing.");
                    }
                })
                .catch((error) => console.error("Error fetching pricing:", error));
        };
    
        document.getElementById("inputTogglePeriod").addEventListener("change", function () {
            TogglePeriodHotel(this);
        });
});
    
    
    
    
function ToggleFeaturePanelHotel() {
    $('#section-pricing-hotel .card .card-body').each(function () {
        if ($(this).css('height') == '335px') {
            $(this).animate({ height: '100%' });
            $(this).closest('.card').find('.card-footer h6 a').html('Show Less');
        }
        else {
            $(this).animate({ height: '335px' });
            $(this).closest('.card').find('.card-footer h6 a').html('Show More');
        }
    });
}

function ChangeCurrencyHotel() {
    ChangePriceHotel();

    var loopCount = 0;
    var isCurrencyINR = inputCurrency.val() == 'INR';
    var sectionAddonHotel = $('#section-addon-hotel');
    sectionAddonHotel.find('.body-addon').remove();
    $.each(pricingAddonHotel, function () {
        var entity = this;
        if (entity.IsActive) {
            var htmlToBind = '<div class="row body-addon py-2' + (++loopCount == pricingAddonHotel.length ? '' : ' border-db-1') + '">';
            htmlToBind += '<div class="col-8">' + entity.Title + '</div>';
            htmlToBind += '<div class="col-4 text-right">' + (isCurrencyINR ? entity.AmountINR : entity.AmountUSD) + '</div>';
            htmlToBind += '</div>';
            sectionAddonHotel.append(htmlToBind);
        }
    });
}

function ChangePriceHotel() {
    if (inputRoomCount.val() != '' && inputRoomCount.val() != null) {
        var roomCount = Number(inputRoomCount.val());
        roomCount = roomCount == 0 ? 10 : roomCount;
        inputRoomCount.val(roomCount);

        var pricingOptions = inputCurrency.val() == 'INR' ? pricingHotelINR : pricingHotelUSD;
        var currencySymbol = inputCurrency.val() == 'INR' ? '₹' : '$';
        var isAnnually = inputTogglePeriod.prop('checked');

        if (pricingOptions != null) {
            if (pricingOptions.length > 0) {
                $.each(pricingOptions, function () {
                    var entity = this;
                    var isBreak = false;
                    var slashPrice = 0;
                    var displayPrice = entity.BasePrice;

                    if (roomCount > entity.BaseQty) {
                        var incrementalCount = 0;
                        var innerIncrementalAmount = 0;
                        for (var i = 0; i < entity.Plan.length; i++) {
                            incrementalCount++;
                            var entityPlan = entity.Plan[i];
                            if (roomCount >= entityPlan.MinQty && roomCount <= entityPlan.MaxQty) {
                                if (roomCount > entityPlan.MinQty) {
                                    var innerIncrementalCount = roomCount - entityPlan.MinQty;
                                    innerIncrementalAmount += innerIncrementalCount * entityPlan.Incremental;
                                }
                                isBreak = true;
                                break;
                            }
                            else {
                                var innerIncrementalCount = entityPlan.MaxQty - entityPlan.MinQty;
                                innerIncrementalAmount += innerIncrementalCount * entityPlan.Incremental;
                            }
                        }
                        //if (!isBreak) {
                        //    var lastEntityPlan = entity.Plan[entity.Plan.length - 1];
                        //    innerIncrementalAmount = (lastEntityPlan.MaxQty - lastEntityPlan.MinQty) * lastEntityPlan.Incremental;
                        //}
                        var incrementalAmount = (incrementalCount * entity.MinIncremental) + innerIncrementalAmount;
                        displayPrice += incrementalAmount;
                        if (roomCount > entity.MaxQty)
                            displayPrice += entity.MinIncremental;
                    }

                    var htmlPrice = '';
                    var htmlPriceYearly = '';
                    var displayPriceYearly = 0;
                    if (isAnnually) {
                        slashPrice = displayPrice;
                        displayPrice = ((100 - annualDiscPer) * slashPrice) / 100;
                        htmlPrice = '<sup class="mr-1"><small><del class="text-muted">' + currencySymbol + slashPrice.toFixed() + '</del></small></sup>' + currencySymbol + displayPrice.toFixed();

                        displayPriceYearly = displayPrice * 12;
                        htmlPriceYearly = currencySymbol + displayPriceYearly.toFixed() + '/- annually';
                    }
                    else
                        htmlPrice = currencySymbol + displayPrice.toFixed();

                    var entityBlock = $('#' + entity.Id);
                    entityBlock.find('.text-price').html(htmlPrice);
                    entityBlock.find('.text-price').attr('data-total-amount', displayPrice.toFixed());
                    entityBlock.find('.text-price-detail').html('Per Month Per Property' + (isAnnually ? ' (Paid Yearly)' : ''));
                    entityBlock.find('.text-price-yearly').html(htmlPriceYearly);
                    entityBlock.find('.text-price-yearly').attr('data-total-amount', displayPriceYearly.toFixed());
                });
            }
        }
    }
}

function OnBlurPriceHotel() {
    var roomCount = Number(inputRoomCount.val());
    if (roomCount == 0) {
        inputRoomCount.val(1);
    }
}

//Methods For Hotel



//Methods For Restaurant

var inputTogglePeriodRest = $('#inputTogglePeriodRest');
var inputCurrencyRest = $('#inputCurrencyRest');
var annualDiscPerRest = 10;
var pricingRestaurant =
    [
        {
            Id: 'section-basic',
            Name: 'Basic',
            MonthlyPriceINR: 1800,
            MonthlyPriceUSD: 25
        },
        {
            Id: 'section-advanced',
            Name: 'Advanced',
            MonthlyPriceINR: 2600,
            MonthlyPriceUSD: 35
        }
    ];

function TogglePeriodRestaurant(inputCheckbox) {
    var labelMonthly = $('#labelMonthlyRest');
    var labelYearly = $('#labelYearlyRest');

    if ($(inputCheckbox).prop('checked')) {
        labelMonthly.removeClass('text-active').addClass('text-inactive');
        labelYearly.removeClass('text-inactive').addClass('text-active');
    }
    else {
        labelMonthly.removeClass('text-inactive').addClass('text-active');
        labelYearly.removeClass('text-active').addClass('text-inactive');
    }

    ChangePriceRestaurant();
}

function ToggleFeaturePanelRestaurant() {
    $('#section-pricing-restaurant .card .card-body').each(function () {
        if ($(this).css('height') == '335px') {
            $(this).animate({ height: '100%' });
            $(this).closest('.card').find('.card-footer h6 a').html('Show Less');
        }
        else {
            $(this).animate({ height: '335px' });
            $(this).closest('.card').find('.card-footer h6 a').html('Show More');
        }
    });
}

function ChangePriceRestaurant() {
    var isCurrencyINR = inputCurrencyRest.val() == 'INR';
    var currencySymbol = inputCurrencyRest.val() == 'INR' ? '₹' : '$';
    var isAnnually = inputTogglePeriodRest.prop('checked');

    if (pricingRestaurant != null) {
        if (pricingRestaurant.length > 0) {
            $.each(pricingRestaurant, function () {
                var entity = this;
                var slashPrice = 0;
                var displayPrice = isCurrencyINR ? entity.MonthlyPriceINR : entity.MonthlyPriceUSD;

                var htmlPrice = '';
                var htmlPriceYearly = '';
                var displayPriceYearly = 0;
                if (isAnnually) {
                    slashPrice = displayPrice;
                    displayPrice = ((100 - annualDiscPerRest) * slashPrice) / 100;
                    htmlPrice = '<sup class="mr-1"><small><del class="text-muted">' + currencySymbol + slashPrice.toFixed() + '</del></small></sup>' + currencySymbol + displayPrice.toFixed();

                    displayPriceYearly = displayPrice * 12;
                    htmlPriceYearly = currencySymbol + displayPriceYearly.toFixed() + '/- annually';
                }
                else
                    htmlPrice = currencySymbol + displayPrice.toFixed();

                var entityBlock = $('#' + entity.Id);
                entityBlock.find('.text-price').html(htmlPrice);
                entityBlock.find('.text-price').attr('data-total-amount', displayPrice.toFixed());
                entityBlock.find('.text-price-detail').html('Per Month Per Outlet' + (isAnnually ? ' (Paid Yearly)' : ''));
                entityBlock.find('.text-price-yearly').html(htmlPriceYearly);
                entityBlock.find('.text-price-yearly').attr('data-total-amount', displayPriceYearly.toFixed());
            });
        }
    }
}

//Methods For Restaurant



//Methods For Payment Summary

var classRowModule = 'row-module';
var classRowModuleChecked = 'row-module-checked';
var classRowSubTotal = 'row-sub-total';
var classRowTax = 'row-tax';
var classRowTotal = 'row-total';
var inputPaymentBusinessName = $('#inputPaymentBusinessName');
var inputPaymentContactName = $('#inputPaymentContactName');
var inputPaymentContactNumber = $('#inputPaymentContactNumber');
var inputPaymentEmail = $('#inputPaymentEmail');
var inputPaymentCity = $('#inputPaymentCity');
var inputPaymentGST = $('#inputPaymentGST');
var inputAcceptTermsCondition = $('#inputAcceptTermsCondition');
var buttonModalOpenPaymentSummary = $('#buttonModalOpenPaymentSummary');
var buttonModalClosePaymentSummary = $('#buttonModalClosePaymentSummary');
var buttonPaymentSummaryPay = $('#buttonPaymentSummaryPay');
var tableDataPaymentSummary = $('#tableDataPaymentSummary');
var modalPaymentSummary = $('#modalPaymentSummary');
var sectionPaymentProcessAlert = $('#sectionPaymentProcessAlert');
var isAnnual = true;
var isCurrencyINR = true;
var currentCurrency = '₹';
var currentCurrencyCode = 'INR';
var packageAmount = 0;
var moduleSMSAmount = 0;
var moduleTallyAmount = 0;
var modulePaymentGatewayAmount = 0;
var subTotalAmount = 0;
var packageTaxAmount = 0;
var totalAmount = 0;
var currentPricingPackage = null;
var paymentProcessError = true;
var currentPayload = null;

function PaymentSummaryClear() {
    isAnnual = true;
    isCurrencyINR = true;
    currentCurrency = '₹';
    currentCurrencyCode = 'INR';
    packageAmount = 0;
    packageTaxAmount = 0;
    totalAmount = 0;
    currentPricingPackage = null;
    paymentProcessError = true;
    currentPayload = null;

    inputPaymentBusinessName.val('');
    inputPaymentContactName.val('');
    inputPaymentContactNumber.val('');
    inputPaymentEmail.val('');
    inputPaymentCity.val('');
    inputPaymentGST.val('');
    if (inputAcceptTermsCondition.prop('checked'))
        inputAcceptTermsCondition.click();

    modalPaymentSummary.find('.modal-body .input-required').each(function () {
        $(this).css('border-color', '#ced4da');
    });
}

function PaymentSummaryOpen(package) {
    PaymentSummaryClear();

    if (currentPropertyType == 1) {
        isCurrencyINR = inputCurrency.val() == 'INR';
        var pricingOptions = isCurrencyINR ? pricingHotelINR : pricingHotelUSD;
        currentPricingPackage = pricingOptions.filter(x => x.Id === package)[0];

        isAnnual = inputTogglePeriod.prop('checked');
        currentCurrencyCode = inputCurrency.val();
        currentCurrency = currentCurrencyCode == 'INR' ? '₹' : '$';
        packageAmount = Number($('#' + package + ' .card-body .text-price' + (isAnnual ? '-yearly' : '')).attr('data-total-amount'));
    }
    else {
        isCurrencyINR = inputCurrencyRest.val() == 'INR';
        currentPricingPackage = pricingRestaurant.filter(x => x.Id === package)[0];

        isAnnual = inputTogglePeriodRest.prop('checked');
        currentCurrencyCode = inputCurrencyRest.val();
        currentCurrency = currentCurrencyCode == 'INR' ? '₹' : '$';
        packageAmount = Number($('#' + package + ' .card-body .text-price' + (isAnnual ? '-yearly' : '')).attr('data-total-amount'));
    }

    subTotalAmount = packageAmount;
    packageTaxAmount = (packageTaxPercent * subTotalAmount) / 100;
    totalAmount = subTotalAmount + packageTaxAmount;

    PaymentSummaryBindHtml();
    buttonModalOpenPaymentSummary.click();
}

function PaymentSummaryBindHtml() {
    var htmlToBind = '';
    htmlToBind += '<tr class="text-dark">';
    htmlToBind += '<td class="text-center"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#28a745" class="bi bi-check" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg></td>';
    htmlToBind += '<td>' + currentPricingPackage.Name + (isAnnual ? ' (Annual Cost)' : ' (Monthly Cost)') + '</td>';
    htmlToBind += '<td class="text-right">' + currentCurrency + packageAmount.toFixed(2) + '</td>';
    htmlToBind += '</tr>';

    if (currentPropertyType == 1) {
        $.each(pricingAddonHotel, function () {
            var entity = this;
            if (entity.IsActive && entity.IncludeInPayment) {
                var moduleAmount = (isCurrencyINR ? entity.PaymentAmountINR : entity.PaymentAmountUSD);

                htmlToBind += '<tr class="text-muted ' + classRowModule + '" data-module-name="' + entity.Name + '" data-module-amount="' + moduleAmount + '">';
                htmlToBind += '<td class="text-center"><input type="checkbox" value="" onclick="ToggleModuleAmount(this);"></td>';
                htmlToBind += '<td>' + entity.Title + '</td>';
                htmlToBind += '<td class="text-right"><del class="text-muted">' + currentCurrency + moduleAmount.toFixed(2) + '</del></td>';
                htmlToBind += '</tr>';
            }
        });
    }

    htmlToBind += '<tr class="text-dark">';
    htmlToBind += '<td class="text-right font-weight-bold pb-0" colspan="2">Sub-Total</td>';
    htmlToBind += '<td class="text-right font-weight-bold pb-0 ' + classRowSubTotal + '">' + currentCurrency + subTotalAmount.toFixed(2) + '</td>';
    htmlToBind += '</tr>';

    htmlToBind += '<tr class="text-dark">';
    htmlToBind += '<td class="text-right font-weight-bold pb-0 no-border-top" colspan="2">GST (' + packageTaxPercent.toFixed() + '%)</td>';
    htmlToBind += '<td class="text-right font-weight-bold pb-0 no-border-top ' + classRowTax + '">' + currentCurrency + packageTaxAmount.toFixed(2) + '</td>';
    htmlToBind += '</tr>';

    htmlToBind += '<tr class="text-dark">';
    htmlToBind += '<td class="text-right font-weight-bold pb-0 no-border-top" colspan="2">Total</td>';
    htmlToBind += '<td class="text-right font-weight-bold pb-0 no-border-top ' + classRowTotal + '">' + currentCurrency + totalAmount.toFixed(2) + '</td>';
    htmlToBind += '</tr>';

    tableDataPaymentSummary.find('tbody').html(htmlToBind);

    buttonPaymentSummaryPay.html('<Span>PAY</span><span class="ml-3">' + currentCurrency + totalAmount.toFixed(2) + '</span>');
}

function ToggleModuleAmount(inputObject) {
    var isChecked = $(inputObject).prop('checked');
    var closestRow = $(inputObject).closest('tr.' + classRowModule);
    var moduleAmount = Number(closestRow.attr('data-module-amount'));
    if (isChecked) {
        closestRow.addClass(classRowModuleChecked);
        closestRow.removeClass('text-muted');
        closestRow.addClass('text-dark');
        closestRow.find('td:last-child').html(currentCurrency + moduleAmount.toFixed(2));
    }
    else {
        closestRow.removeClass(classRowModuleChecked);
        closestRow.addClass('text-muted');
        closestRow.removeClass('text-dark');
        closestRow.find('td:last-child').html('<del class="text-muted">' + currentCurrency + moduleAmount.toFixed(2) + '</del>');
    }

    PaymentSummaryCalculate();
}

function PaymentSummaryCalculate() {
    var moduleAmount = 0;
    tableDataPaymentSummary.find('tbody tr.' + classRowModuleChecked).each(function () {
        moduleAmount += Number($(this).attr('data-module-amount'));
    });

    subTotalAmount = packageAmount + moduleAmount;
    packageTaxAmount = (packageTaxPercent * subTotalAmount) / 100;
    totalAmount = subTotalAmount + packageTaxAmount;

    tableDataPaymentSummary.find('tbody tr td.' + classRowSubTotal).html(currentCurrency + subTotalAmount.toFixed(2));
    tableDataPaymentSummary.find('tbody tr td.' + classRowTax).html(currentCurrency + packageTaxAmount.toFixed(2));
    tableDataPaymentSummary.find('tbody tr td.' + classRowTotal).html(currentCurrency + totalAmount.toFixed(2));

    buttonPaymentSummaryPay.html('<Span>PAY</span><span class="ml-3">' + currentCurrency + totalAmount.toFixed(2) + '</span>');
}

function ValidatePaymentSummary() {
    var inputNotValidated = 0;
    modalPaymentSummary.find('.modal-body .input-required').each(function () {
        if ($(this).val() == '') {
            inputNotValidated++;
            $(this).css('border-color', '#dc3545');
        }
        else
            $(this).css('border-color', '#ced4da');
    });

    if (inputNotValidated == 0) {
        if (inputPaymentEmail.val() != '') {
            if (!isEmail(inputPaymentEmail.val())) {
                inputNotValidated++;
                inputPaymentEmail.css('border-color', '#dc3545');
            }
        }
    }

    if (inputNotValidated == 0) {
        inputPaymentEmail.css('border-color', '#ced4da');

        if (inputAcceptTermsCondition.prop('checked')) {
            var listPaymentItems = [];
            listPaymentItems.push({ Id: 0, Name: currentPricingPackage.Name, Amount: packageAmount });
            tableDataPaymentSummary.find('tbody tr.' + classRowModuleChecked).each(function () {
                listPaymentItems.push({ 
                    Id: 0, 
                    IsActive: true, 
                    Name: $(this).attr('data-module-name'), 
                    Amount: Number($(this).attr('data-module-amount')).toFixed(2)
                });
            });

            if (currentPayload == null) {
                currentPayload =
                {
                    Id: 0,
                    IsActive: true,
                    BusinessName: inputPaymentBusinessName.val(),
                    ContactPersonName: inputPaymentContactName.val(),
                    ContactNumber: inputPaymentContactNumber.val(),
                    Email: inputPaymentEmail.val(),
                    City: inputPaymentCity.val(),
                    BusinessGST: inputPaymentGST.val(),
                    PropertyType: currentPropertyType == 1 ? 'Hotel' : 'Restaurant',
                    PaymentPeriod: (currentPropertyType == 1 ? (inputTogglePeriod.prop('checked') ? 'Yearly' : 'Monthly') : (inputTogglePeriodRest.prop('checked') ? 'Yearly' : 'Monthly')),
                    RoomCount: (currentPropertyType == 1 ? Number(inputRoomCount.val()) : 0),
                    Currency: currentCurrencyCode,
                    PaymentItems: listPaymentItems,
                    SubTotalAmount: Number(subTotalAmount.toFixed(2)),
                    TaxPercentage: packageTaxPercent,
                    TaxAmount: Number(packageTaxAmount.toFixed(2)),
                    TotalAmount: Number(totalAmount.toFixed(2)),
                    RazorpayOrderId: null,
                    RazorpayPaymentId: null,
                    RazorpayStatus: null,
                    PackageName: currentPricingPackage.Name
                };

                PaymentProcess();
            }
            else
                ProcessRazorpayPayment();
        }
        else
            alert('Kindly click the checkbox to accept the Terms and Conditions.');
    }
    else {
        modalPaymentSummary.animate({
            scrollTop: 0
        }, 1000);
    }
}

//Methods For Payment Summary



//Methods For Payment Razorpay

var paymentProcessMessage = '<span class="font-weight-bold">Payment Processing...</span> Please Do Not Close The Popup Or Refresh The Page.';
var paymentProcessErrorMessage = '<span class="font-weight-bold">Error!</span> An error has occurred.';

function PaymentProcess() {
    var dataPayload = JSON.stringify(currentPayload);

    $.ajax({
        type: "POST",
        url: apiDomain + '/api/Razorpay/ProcessPayment',
        data: dataPayload,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function (jqXHR, settings) {
            buttonPaymentSummaryPay.attr('disabled', true);
            buttonModalClosePaymentSummary.hide();

            sectionPaymentProcessAlert.find('div.alert').removeClass('alert-danger');
            sectionPaymentProcessAlert.find('div.alert').addClass('alert-warning');
            sectionPaymentProcessAlert.find('div.alert').html(paymentProcessMessage);
            sectionPaymentProcessAlert.show();
        },
        success: function (response) {
            if (response != null && response != undefined) {
                if (response.Data != null) {
                    paymentProcessError = false;
                    currentPayload = response.Data;

                    ProcessRazorpayPayment(true);
                }
            }
        },
        failure: function (response) {
            PaymentError();
        },
        error: function (response) {
            PaymentError();
        },
        complete: function (jqXHR, textStatus) {
            if (paymentProcessError)
                PaymentError();
        }
    });
}

function ProcessRazorpayPayment(fromProcess = false) {
    if (currentPayload != null) {
        if (!fromProcess) {
            buttonPaymentSummaryPay.attr('disabled', true);
            buttonModalClosePaymentSummary.hide();

            sectionPaymentProcessAlert.find('div.alert').removeClass('alert-danger');
            sectionPaymentProcessAlert.find('div.alert').addClass('alert-warning');
            sectionPaymentProcessAlert.find('div.alert').html(paymentProcessMessage);
            sectionPaymentProcessAlert.show();
        }

        var options = {
            "key": currentPayload.RazorpayMerchantKey,
            "amount": currentPayload.Amount,
            "name": currentPayload.RazorpayMerchantName,
            "description": currentPayload.Description,
            "image": apiDomain + currentPayload.RazorpayMerchantLogo,
            "handler": function (responsePayment) {
                currentPayload.RazorpayPaymentId = responsePayment.razorpay_payment_id;
                PaymentCapture();
            },
            "prefill": {
                "name": currentPayload.ContactPersonName,
                "email": currentPayload.Email,
                "contact": currentPayload.ContactNumber
            },
            "modal": {
                "backdropclose": false,
                "escape": false,
                "ondismiss": function () {
                    PaymentError();
                }
            },
            "notes": {
                "Note": currentPayload.RazorpayNotes
            },
            "theme": {
                "color": currentPayload.RazorpayThemeColor,
                "emi_mode": currentPayload.RazorpayIsEMIAvailable
            },
            "order_id": currentPayload.RazorpayOrderId
        };

        var paymentRazorpay = new Razorpay(options);
        paymentRazorpay.open();
    }
}

function PaymentCapture() {
    paymentProcessError = true;

    var dataPayload = JSON.stringify(currentPayload);
    $.ajax({
        type: "POST",
        url: apiDomain + '/api/Razorpay/MarkPaymentAsCaptured',
        data: dataPayload,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        beforeSend: function (jqXHR, settings) {
        },
        success: function (response) {
            if (response != null && response != undefined) {
                if (response.Data != null) {
                    paymentProcessError = false;
                    location.href = "payment-confirmation.html";
                }
            }

            if (paymentProcessError)
                PaymentError();
        },
        failure: function (response) {
            PaymentError();
        },
        error: function (response) {
            PaymentError();
        }
    });
}

function PaymentError() {
    buttonModalClosePaymentSummary.show();

    sectionPaymentProcessAlert.find('div.alert').addClass('alert-danger');
    sectionPaymentProcessAlert.find('div.alert').removeClass('alert-warning');
    sectionPaymentProcessAlert.find('div.alert').html(paymentProcessErrorMessage);
    sectionPaymentProcessAlert.show();

    buttonPaymentSummaryPay.attr('disabled', false);
}

//Methods For Payment Razorpay



//Methods For Common

//regular expressions to extract IP and country values
// const countryCodeExpression = /loc=([\w]{2})/;
let userIPExpression = /ip=([\w\.]+)/;

// //automatic country determination.
// function SetDefaultCurrency() {
//     return new Promise((resolve, reject) => {
//         var xhr = new XMLHttpRequest();
//         xhr.timeout = 3000;
//         xhr.onreadystatechange = function () {
//             if (this.readyState == 4) {
//                 if (this.status == 200) {
//                     countryCode = countryCodeExpression.exec(this.responseText)
//                     ip = userIPExpression.exec(this.responseText)
//                     if (countryCode === null || countryCode[1] === '' ||
//                         ip === null || ip[1] === '') {
//                         reject('IP/Country code detection failed');
//                     }
//                     let result = {
//                         "countryCode": countryCode[1],
//                         "IP": ip[1]
//                     };
//                     resolve(result)
//                 } else {
//                     reject(xhr.status)
//                 }
//             }
//         }
//         xhr.ontimeout = function () {
//             reject('timeout')
//         }
//         xhr.open('GET', 'https://www.cloudflare.com/cdn-cgi/trace', true);
//         xhr.send();
//     });
// }

function InputOnlyNumber() {
    if ($(".input-number").length) {
        $(".input-number").keypress(function (e) {
            if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                return false;
            }
        });
    }
}

// function DetectCurrency() {
//     SetDefaultCurrency().then(result => TogglePropertySection(1, true, result)).catch(e => console.log(e));
// }

function TogglePropertySection(propertyType, onLoad = false, dataCountry) {
    if (onLoad) {
        var currency = (dataCountry == null || dataCountry == undefined ? 'INR' : (dataCountry.countryCode == 'IN' ? 'INR' : 'USD'));
        inputCurrency.val(currency);
        inputCurrencyRest.val(currency);
    }

    currentPropertyType = propertyType;
    var sectionProperty = $('.section-property');
    switch (propertyType) {
        case 1:
            sectionProperty.find('.card-property-parent:first-child span').addClass('active');
            sectionProperty.find('.card-property-parent:last-child span').removeClass('active');
            $('#section-pricing-hotel').show();
            $('#section-pricing-restaurant').hide();
            ChangeCurrencyHotel();
            break;
        case 2:
            sectionProperty.find('.card-property-parent:last-child span').addClass('active');
            sectionProperty.find('.card-property-parent:first-child span').removeClass('active');
            $('#section-pricing-hotel').hide();
            $('#section-pricing-restaurant').show();
            ChangePriceRestaurant();
            break;
    }
}

function isEmail(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

function InitScrollStick() {
    $(window).scroll(function () {
        var distanceFromTop = $(document).scrollTop();
        if ($('#section-pricing-hotel').css('display') != 'none') {
            if (distanceFromTop >= ($('#secStickMark').height() + 150)) {
                $('.ch-sticky').show();
            }
            else {
                $('.ch-sticky').hide();
            }
        }

        if ($('#section-pricing-restaurant').css('display') != 'none') {
            if (distanceFromTop >= ($('#secStickMarkRes').height() + 250)) {
                $('.ch-sticky').show();
            }
            else {
                $('.ch-sticky').hide();
            }
        }
    });
}

$(document).ready(function () {
    $('.main-wrapper .btn-package-buy').each(function () {
        if (disableBuyButton) {
            if ($(this).hasClass('display-enable')) {
                $(this).removeClass('display-enable');
                $(this).addClass('display-disable');
            }
        }
        else {
            if ($(this).hasClass('display-disable')) {
                $(this).removeClass('display-disable');
                $(this).addClass('display-enable');
            }
        }
    });
    InputOnlyNumber();
    // DetectCurrency();
    InitScrollStick();
    $('#inputRoomCount').on('change', ChangePriceHotel);
});

//Methods For Common