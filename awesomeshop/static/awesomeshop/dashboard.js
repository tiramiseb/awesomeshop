/* Copyright 2015 Sébastien Maccagnoni-Munch
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
        'ngAnimate', 'ui.bootstrap', 'ui.router', 'validation.match',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner', 
        // Dashboard modules
        'dbCarriers', 'dbCategories', 'dbCountries', 'dbOrders', 'dbPages',
        'dbProducts', 'dbTaxrates', 'dbUsers'
])
.config(function($interpolateProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $urlRouterProvider.otherwise('');
    $urlMatcherFactoryProvider.strictMode(false);
    $stateProvider
        .state('index', {
            url: '',
            templateUrl: 'index',
            controller: 'IndexCtrl'
        })
})
.filter('htmlbr', function($sce) {
    return function(input) {
        if (input) {
            return $sce.trustAsHtml(input.replace(/\n/g, '<br>'));
        };
    };
})
.run(function($timeout, $rootScope) {
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
    $http.get('/api/product', {params: {'out_of_stock': 'true'}})
        .then(function(response) {
            $scope.out_of_stock_products = response.data;
        })
    $http.get('/api/product', {params: {'stock_lower_than_alert': 'true'}})
        .then(function(response) {
            $scope.stock_alert_products = response.data;
        })
})
