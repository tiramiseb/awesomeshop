/* Copyright 2016 Sébastien Maccagnoni-Munch
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
angular.module('shopUser', ['validation.match'])
.config(function($stateProvider) {
    $stateProvider
        .state('profile', {
            url: '/profile',
            templateUrl: 'shop/profile',
            controller: 'ProfileCtrl',
            title: 'Profile'
        })
        .state('profile.addresses', {
            url: '/addresses',
            templateUrl: 'shop/addresses',
            controller: 'AddressesCtrl',
            title: 'Addresses'
        })
})
.controller('ProfileCtrl', function($scope, $state, $uibModal, user) {
    $scope.user = user;
    if (!user.get().auth) {
        $state.go('index');
    }
    $scope.change_email = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'part/emailaddress',
                controller: 'ChangeEmailCtrl'
                })
    };
    $scope.change_password = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'part/password',
                controller: 'ChangePasswordCtrl'
                })
    };
    $scope.delete_account = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'part/deleteaccount',
                controller: 'DeleteAccountCtrl'
                })
    };
})
.controller('ChangeEmailCtrl', function($scope, $http, user) {
    $scope.user = user;
    $scope.change_email = function() {
        $http.post('/api/userdata', {
            email: $scope.email
        })
            .then(function(response) {
                user.set(response.data);
                $scope.$close();
            })
    }
})
.controller('ChangePasswordCtrl', function($scope, $http) {
    $scope.change_password = function() {
        $http.post('/api/userdata', {
            password: $scope.password
        })
            .then(function(response) {
                $scope.$close();
            })
    }
})
.controller('DeleteAccountCtrl', function($scope, $state, $http, user) {
    $scope.delete_account = function() {
        $http.post('/api/userdata/delete')
            .then(function(response) {
                user.set(response.data);
                $state.go('index');
                $scope.$close();
            })
    }
})
.controller('AddressesCtrl', function($scope, $http, user) {
    // Duplicate the addresses list so that the user object is not modified in
    // place (which would result in an inconsistence if the user leaves the
    // page without saving his/her modifications)
    $scope.addresses = angular.copy(user.get().addresses);
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    }
    $scope.is_last_odd = function(index) {
        return ((index == $scope.addresses.length - 1) && (index % 2 == 0));
    };
    $scope.send = function() {
        $http.post('/api/userdata', {'addresses': $scope.addresses})
            .then(function(response) {
                user.set(response.data);
            });
    };
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
})
.controller('AddressCtrl', function($scope, $http, user, address_id) {
    if (address_id) {
        if (user.get().addresses) {
            addresses = user.get().addresses;
        };
        for (var i=0; i<addresses.length; i++) {
            if (addresses[i].id == address_id) {
                $scope.address = addresses[i];
                break;
            };
        };
        $scope.modify = true;
    } else {
        $scope.address = {};
        $scope.modify = false;
    }
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    };
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
    $scope.save = function() {
        var addresses = angular.copy(user.get().addresses);
        if ($scope.address.id) {
            for (var i=0; i<addresses.length; i++) {
                if (addresses[i].id == $scope.address.id) {
                    addresses[i] = $scope.address;
                    found = true;
                    break;
                };
            };
            if (!found) {
                addresses.push($scope.address);
            }
        } else {
            addresses.push($scope.address);
        }
        $http.post('/api/userdata', {'addresses': addresses})
            .then(function(response) {
                user.set(response.data);
                $scope.$close();
            });
    };
})
