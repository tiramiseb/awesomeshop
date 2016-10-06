/* Copyright 2016 Sébastien Maccagnoni
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

angular.module('dbOrders', [])
.config(function($stateProvider) {
    $stateProvider
        .state('orders', {
            url: '/orders',
            templateUrl: 'dashboard/orders.html',
            controller: 'OrdersCtrl'
        })
        .state('order', {
            url: '/order/:number',
            templateUrl: 'dashboard/order.html',
            controller: 'OrderCtrl'
        })
})
.controller('OrdersCtrl', function($scope, $http) {
    $http.get('/api/order/all')
        .then(function(response) {
            $scope.orders = response.data;
        });
})
.controller('OrderCtrl', function($http, $scope, $stateParams, $uibModal) {
    function save_order(response) {
        $scope.order = response.data;
    }
    $http.get('/api/order/'+$stateParams.number)
        .then(save_order);
    $scope.change_status = function(new_status) {
        $http.put('/api/order/'+$scope.order.number, {
            status: new_status
        }).then(save_order);
    };
    $scope.set_tracking_number = function() {
        $http.put('/api/order/'+$scope.order.number, {
            status: 'shipped',
            tracking_number: $scope.tracking_number
        }).then(save_order);
    };
    $scope.open_note = function(product) {
        if (product.internal_note) {
            var noteModal = $uibModal.open({
                templateUrl: 'dashboard/internal_note.html',
                controller: 'InternalNoteCtrl',
                resolve: {
                    product: function () {
                        return product;
                    }
                }
            });
        }
    };
})
