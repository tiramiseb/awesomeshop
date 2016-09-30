/* Copyright 2015-2016 Sébastien Maccagnoni
 *
 * This file is part of AwesomeShop.
 *
 * AwesomeShop is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
 * details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.
 */


angular.module('awesomeshop', [
        // External modules
        'ngAnimate', 'pascalprecht.translate', 'tmh.dynamicLocale',
        'ui.bootstrap', 'ui.router', 'validation.match',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner', 
        // Dashboard modules
        'dbCarriers', 'dbCategories', 'dbCountries', 'dbOrders', 'dbPages',
        'dbProducts', 'dbTaxrates', 'dbUsers'
])
.config(function($locationProvider, $interpolateProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider, $translateProvider, $translatePartialLoaderProvider, tmhDynamicLocaleProvider) {
    $urlRouterProvider.otherwise('');
    $urlMatcherFactoryProvider.strictMode(false);
    tmhDynamicLocaleProvider.localeLocationPattern('bower_components/angular-i18n/angular-locale_{{locale}}.js');
    $translatePartialLoaderProvider.addPart('common');
    $translatePartialLoaderProvider.addPart('dashboard');
    $translateProvider
        .useMessageFormatInterpolation()
        .useSanitizeValueStrategy('escape')
        .useLoader('$translatePartialLoader', {urlTemplate: 'l10n/{lang}/{part}.json'})
        .registerAvailableLanguageKeys(langs, langs_negociation)
        .fallbackLanguage(fallback_language)
        .determinePreferredLanguage();
    $stateProvider
        .state('index', {
            url: '/test',
            templateUrl: 'dashboard/index.html',
            controller: 'IndexCtrl'
        })
})
.filter('trusthtml', function($sce) {
    return $sce.trustAsHtml;
})
.filter('htmlbr', function($sce) {
    return function(input) {
        if (input) {
            return $sce.trustAsHtml(input.replace(/\n/g, '<br>'));
        };
    };
})
.run(function($timeout, $rootScope, CONFIG) {
    $rootScope.displayable_from_id = function(scope, listname, value) {
        if (!scope[listname]) {
            $timeout($rootScope.displayable_from_id, 100, true, scope, listname, value);
        } else {
            objlist = scope[listname];
            for (var i=0; i<objlist.length; i++) {
                if (value == objlist[i].id) {
                    scope['displayable'+listname] = objlist[i];
                    break
                }
            }
        }

    };
    $rootScope.CONFIG = CONFIG;
})
.controller('IndexCtrl', function($http, $scope) {
    $http.get('/api/order', {params: {'status': 'preparation'}})
        .then(function(response) {
            $scope.prep_orders = response.data;
        })
    $http.get('/api/order', {params: {'status': 'payment_received'}})
        .then(function(response) {
            $scope.paid_orders = response.data;
        })
    $http.get('/api/order', {params: {'status': 'awaiting_payment'}})
        .then(function(response) {
            $scope.awaiting_payment_orders = response.data;
        })
    $http.get('/api/product-regular', {params: {'out_of_stock': 'true'}})
        .then(function(response) {
            $scope.out_of_stock_products = response.data;
        })
    $http.get('/api/product-regular', {params: {'stock_lower_than_alert': 'true'}})
        .then(function(response) {
            $scope.stock_alert_products = response.data;
        })
})
.controller('InternalNoteCtrl', function($scope, product) {
    $scope.product = product;
})
