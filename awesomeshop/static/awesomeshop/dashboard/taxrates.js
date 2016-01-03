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

angular.module('dbTaxrates', [])
.config(function($stateProvider) {
    $stateProvider
        .state('taxrates', {
            url: '/taxrates',
            templateUrl: 'taxrates',
            controller: 'TaxratesCtrl'
        })
})
.controller('TaxratesCtrl', function($scope, $http) {
    $scope.newrate = {};
    $http.get('/api/taxrate')
        .then(function(response) {
            $scope.taxrates = response.data;
        })
    $scope.add = function() {
        $http.post('/api/taxrate', $scope.newrate)
            .then(function(response) {
                $scope.taxrates.push(response.data);
                $scope.newrate = {};
            });
    }
    $scope.save = function(rate) {
        $http.post('/api/taxrate', rate)
            .then(function(response) {
                rate = response.data;
            });
    }
    $scope.delete = function(rate) {
        $http.delete('/api/taxrate/'+rate.id)
            .then(function(response) {
                $scope.taxrates.splice($scope.taxrates.indexOf(rate), 1);
            });
    }
})
