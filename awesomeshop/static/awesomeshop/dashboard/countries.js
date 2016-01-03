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

angular.module('dbCountries', [])
.config(function($stateProvider) {
    $stateProvider
        .state('countries', {
            url: '/country',
            templateUrl: 'countries',
            controller: 'CountriesCtrl'
        })
        .state('newcountry', {
            url: '/country/new',
            templateUrl: 'country',
            controller: 'CountryCtrl'
        })
        .state('country', {
            url: '/country/:country_id',
            templateUrl: 'country',
            controller: 'CountryCtrl'
        })
})
.controller('CountriesCtrl', function($scope, $http) {
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
})
.controller('CountryCtrl', function($scope, $http, $stateParams, CONFIG) {
    $scope.langs = CONFIG.languages;
    $scope.submit = function() {
        $http.post('/api/country', $scope.country)
            .then(function(response) {
                var is_new = !$scope.country.id;
                $scope.country = response.data;
                $scope.form.$setPristine();
                if (is_new) {
                    $state.go('country', {country_id:response.data.id}, {notify:false});
                }
            });
    }
    $scope.delete = function() {
        if ($scope.country.id) {
            $http.delete('/api/country/'+$scope.country.id)
                .then(function(response) {
                    $state.go('countries');
                });
        } else {
            $state.go('countries');
        }

    };
    if ($stateParams.country_id) {
        $http.get('/api/country/'+$stateParams.country_id)
            .then(function(response) {
                $scope.country = response.data;
            });
    } else {
        $scope.country = {};
    }
})
