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
angular.module('shopUser', ['validation.match'])
.config(function($stateProvider) {
    $stateProvider
        .state('profile', {
            url: '/profile',
            templateUrl: 'shop/profile.html',
            controller: 'ProfileCtrl',
            title: 'PROFILE'
        })
        .state('profile.addresses', {
            url: '/addresses',
            templateUrl: 'shop/addresses.html',
            controller: 'AddressesCtrl',
            title: 'ADDRESSES'
        })
        .state('register', {
            url: '/register',
            templateUrl: 'shop/register.html',
            controller: 'RegisterCtrl',
            title: 'CREATE_ACCOUNT'
        })
})
.controller('RegisterCtrl', function($state, $scope, $http, user, authService) {
    $scope.register = function() {
        $http.post('/api/register', {
                email: $scope.email,
                password: $scope.password
                })
            .then(function(response) {
                authService.loginConfirmed(response.data);
                $scope.$close();
            })
    }
})
.controller('ProfileCtrl', function($scope, $state, $uibModal, user) {
    $scope.user = user;
    if (user.get() && !user.get().auth) {
        $state.go('index');
    }
    $scope.change_email = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'shop/emailaddress.html',
                controller: 'ChangeEmailCtrl'
                })
    };
    $scope.change_password = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'shop/password.html',
                controller: 'ChangePasswordCtrl'
                })
    };
    $scope.delete_account = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'shop/deleteaccount.html',
                controller: 'DeleteAccountCtrl'
                })
    };
})
.controller('ChangeEmailCtrl', function($scope, $http, user) {
    $scope.user = user;
    $scope.change_email = function() {
        $http.put('/api/userdata', {
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
        $http.put('/api/userdata', {
            password: $scope.password
        })
            .then(function(response) {
                $scope.$close();
            })
    }
})
.controller('DeleteAccountCtrl', function($scope, $state, $http, user) {
    $scope.delete_account = function() {
        $http.delete('/api/userdata')
            .then(function(response) {
                user.set(response.data);
                $state.go('index');
                $scope.$close();
            })
    }
})
.controller('AddressesCtrl', function($scope, $http, user, countries, $translate) {
    // Duplicate the addresses list so that the user object is not modified in
    // place (which would result in an inconsistence if the user leaves the
    // page without saving his/her modifications)
    $scope.addresses = angular.copy(user.get().addresses);
    $scope.countries = countries;
    $translate('MY_ADDRESS').then(function(str) {
        $scope.MY_ADDRESS = str;
    });
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    }
    $scope.is_last_odd = function(index) {
        return ((index == $scope.addresses.length - 1) && (index % 2 == 0));
    };
    $scope.send = function() {
        $http.put('/api/userdata', {'addresses': $scope.addresses})
            .then(function(response) {
                user.set(response.data);
            });
    };
})
.controller('AddressCtrl', function($scope, $http, $translate, user, address_id, countries) {
    $scope.countries = countries;
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
        $translate('MY_ADDRESS').then(function(title) {
            $scope.address.title = title;
        })
        $scope.modify = false;
    }
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    };
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
        $http.put('/api/userdata', {'addresses': addresses})
            .then(function(response) {
                user.set(response.data);
                $scope.$close();
            });
    };
})
