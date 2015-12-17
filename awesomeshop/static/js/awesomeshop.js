/*
Copyright 2015 Sébastien Maccagnoni-Munch

This file is part of AwesomeShop.

AwesomeShop is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.
*/
var app = angular.module('awesomeshop', ['ui.bootstrap']);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('[[');
  $interpolateProvider.endSymbol(']]');
}])

.controller('CheckoutCtrl', function ($scope, $http) {
    $scope.choices = {accept_terms:false};
    
    function get_carrier() {
        return $scope.choices.carrier;
    }
    function change_carrier_total() {
        $scope.carriers.forEach(function(carrier) {
            if (carrier.id == $scope.choices.carrier) {
                var price = carrier.price;
                $scope.shipping_fee = price;
                total = parseFloat($scope.cart.total) + parseFloat(price);
                $scope.order_total = total.toFixed(2);
            };
        });
    }
    $scope.update_carriers = function() {
        $http.get('/api/carriers-for-address/'+
                  $scope.choices.delivery_address.id+'/'+$scope.cart.weight)
            .success(function(data, status, headers, config) {
                $scope.carriers = data;
                $scope.choices.carrier = $scope.preferred_carrier;
                $scope.$watch(get_carrier, change_carrier_total)
            });
    };

    $http.get('/api/cart')
        .success(function(data, status, headers, config) {
            $scope.cart = data;
        });
    $http.get('/api/addresses')
        .success(function(data, status, headers, config) {
            $scope.addresses = data;
            $http.get('/api/preferences')
                .success(function(data, status, headers, config) {
                    $scope.choices.delivery_as_billing = data.delivery_as_billing;
                    $scope.choices.payment = data.payment;
                    $scope.preferred_carrier = data.carrier;
                    $scope.choices.reused_package = data.reused_package;
                    $scope.addresses.forEach(function(a) {
                        if (a.id == data.delivery_address) {
                            $scope.choices.delivery_address = a;
                            $scope.update_carriers();
                        };
                        if (a.id == data.billing_address) {
                            $scope.choices.billing_address = a;
                        }
                    });
                });
        });
});
