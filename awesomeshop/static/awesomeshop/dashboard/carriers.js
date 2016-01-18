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

angular.module('dbCarriers', [])
.config(function($stateProvider) {
    $stateProvider
        .state('carriers', {
            url: '/carrier',
            templateUrl: 'carriers',
            controller: 'CarriersCtrl'
        })
        .state('newcarrier', {
            url: '/carrier/new',
            templateUrl: 'carrier',
            controller: 'CarrierCtrl'
        })
        .state('carrier', {
            url: '/carrier/:carrier_id',
            templateUrl: 'carrier',
            controller: 'CarrierCtrl'
        })
})
.controller('CarriersCtrl', function($scope, $http) {
    $http.get('/api/carrier')
        .then(function(response) {
            $scope.carriers = response.data;
        });
})
.controller('CarrierCtrl', function($scope, $http, $stateParams, $state, CONFIG) {
    $scope.langs = CONFIG.languages;
    $scope.submit = function() {
        $http.post('/api/carrier', $scope.carrier)
            .then(function(response) {
                var is_new = !$scope.carrier.id;
                console.log(response)
                $scope.carrier = response.data;
                $scope.form.$setPristine();
                if (is_new) {
                    $state.go('carrier', {carrier_id:response.data.id}, {notify:false});
                }
            });
    }
    $scope.delete = function() {
        if ($scope.carrier.id) {
            $http.delete('/api/carrier/'+$scope.carrier.id)
                .then(function(response) {
                    $state.go('carriers');
                });
        } else {
            $state.go('carriers');
        }

    };
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
    $http.get('/api/countriesgroup')
        .then(function(response) {
            $scope.countriesgroups = response.data;
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
    $scope.id_from_code = function(code) {
        if ($scope.countries) {
            for (i=0; i<$scope.countries.length; i++) {
                if ($scope.countries[i].code == code) {
                    return $scope.countries[i].id;
                }
            }
        }
    }
    $scope.name_from_id = function(groupid) {
        if ($scope.countriesgroups) {
            for (i=0; i<$scope.countriesgroups.length; i++) {
                if ($scope.countriesgroups[i].id == groupid) {
                    return $scope.countriesgroups[i].name;
                }
            }
        }
        return groupid;
    }
    $scope.filtered_countries = function() {
        filtered = [];
        if ($scope.countries && $scope.carrier) {
            for (i=0; i<$scope.countries.length; i++) {
                if ($scope.carrier.countries.indexOf($scope.countries[i].code) == -1) {
                    filtered.push($scope.countries[i])
                }
            }
        }
        return filtered;
    }
    $scope.filtered_countriesgroups = function() {
        filtered = [];
        if ($scope.countriesgroups && $scope.carrier) {
            for (i=0; i<$scope.countriesgroups.length; i++) {
                if ($scope.carrier.countries_groups.indexOf($scope.countriesgroups[i].id) == -1) {
                    filtered.push($scope.countriesgroups[i])
                }
            }
        }
        return filtered;
    }
    $scope.add_country = function(code) {
        $scope.carrier.countries.push(code);
        $scope.carrier.countries.sort();
        $scope.form.$setDirty();
    }
    $scope.add_countriesgroup = function(groupid) {
        $scope.carrier.countries_groups.push(groupid);
        $scope.carrier.countries_groups.sort();
        $scope.form.$setDirty();
    }
    $scope.remove_country = function(code) {
        $scope.carrier.countries.splice($scope.carrier.countries.indexOf(code), 1);
        $scope.form.$setDirty();
    }
    $scope.remove_countriesgroup = function(name) {
        $scope.carrier.countries_groups.splice($scope.carrier.countries_groups.indexOf(name), 1);
        $scope.form.$setDirty();
    }
    
    if ($stateParams.carrier_id) {
        $http.get('/api/carrier/'+$stateParams.carrier_id)
            .then(function(response) {
                $scope.carrier = response.data;
            });
    } else {
        $scope.carrier = {'countries':[], 'countries_groups':[]};
    }
})
