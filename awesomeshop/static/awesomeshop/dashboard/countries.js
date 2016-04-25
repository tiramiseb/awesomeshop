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
        .state('countriesgroups', {
            url: '/contriesgroup',
            templateUrl: 'countriesgroups',
            controller: 'CountriesGroupsCtrl'
        })
        .state('newcountriesgroup', {
            url: '/countriesgroup/new',
            templateUrl: 'countriesgroup',
            controller: 'CountriesGroupCtrl'
        })
        .state('countriesgroup', {
            url: '/countriesgroup/:group_id',
            templateUrl: 'countriesgroup',
            controller: 'CountriesGroupCtrl'
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
        if ($scope.country.id) {
            $http.put('/api/country/'+$scope.country.id, $scope.country)
                .then(function(response) {
                    $scope.country = response.data;
                    $scope.form.$setPristine();
                });
        } else {
            $http.post('/api/country', $scope.country)
                .then(function(response) {
                    $scope.country = response.data;
                    $scope.form.$setPristine();
                    $state.go('country', {country_id:response.data.id}, {notify:false});
                });
        };
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
    $scope.default_from = function(text) {
        $scope.country.default_name = text;
    }
    if ($stateParams.country_id) {
        $http.get('/api/country/'+$stateParams.country_id)
            .then(function(response) {
                $scope.country = response.data;
            });
    } else {
        $scope.country = {};
    };
})
.controller('CountriesGroupsCtrl', function($scope, $http) {
    $http.get('/api/countriesgroup')
        .then(function(response) {
            $scope.countriesgroups = response.data;
        });
})
.controller('CountriesGroupCtrl', function($scope, $http, $state, $stateParams) {
    $scope.submit = function () {
        if ($scope.group.id) {
            $http.put('/api/countriesgroup/'+$scope.group.id, $scope.group)
                .then(function(response) {
                    $scope.group = response.data;
                    $scope.form.$setPristine();
                });
        } else {
            $http.post('/api/countriesgroup', $scope.group)
                .then(function(response) {
                    $scope.group = response.data;
                    $scope.form.$setPristine();
                    $state.go('countriesgroup', {group_id: response.data.id}, {notify:false});
                });
        };
    }
    $scope.delete = function() {
        if ($scope.group.id) {
            $http.delete('/api/countriesgroup/'+$scope.group.id)
                .then(function(response) {
                    $state.go('countriesgroups');
                });
        } else {
            $state.go('countriesgroups');
        }
    }
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
    $scope.name_from_code = function(code) {
        if ($scope.countries) {
            for (i=0; i<$scope.countries.length; i++) {
                if ($scope.countries[i].code == code) {
                    return $scope.countries[i].name;
                }
            }
        }
        return code;
    }
    $scope.filtered_countries = function() {
        filtered = [];
        if ($scope.countries && $scope.group) {
            for (i=0; i<$scope.countries.length; i++) {
                if ($scope.group.countries.indexOf($scope.countries[i].code) == -1) {
                    filtered.push($scope.countries[i])
                }
            }
        }
        return filtered;
    }
    $scope.add = function(code) {
        $scope.group.countries.push(code);
        $scope.group.countries.sort();
        $scope.form.$setDirty();
    }
    $scope.remove = function(code) {
        $scope.group.countries.splice($scope.group.countries.indexOf(code), 1);
        $scope.form.$setDirty();
    }
    if ($stateParams.group_id) {
        $http.get('/api/countriesgroup/'+$stateParams.group_id)
            .then(function(response) {
                $scope.group = response.data;
            });
    } else {
        $scope.group = {};
    }
})
