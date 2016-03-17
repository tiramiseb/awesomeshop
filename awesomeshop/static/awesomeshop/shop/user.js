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
.controller('ProfileCtrl', function($scope, $state, $uibModal) {
    if (!$scope.user.auth) {
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
.controller('ChangeEmailCtrl', function($rootScope, $scope, $http) {
    $scope.change_email = function() {
        $http.post('/api/userdata', {
            email: $scope.email
        })
            .then(function(response) {
                $rootScope.user = response.data;
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
.controller('DeleteAccountCtrl', function($rootScope, $scope, $state, $http) {
    $scope.delete_account = function() {
        $http.post('/api/userdata/delete')
            .then(function(response) {
                $rootScope.user = response.data;
                $state.go('index');
                $scope.$close();
            })
    }
})
.controller('AddressesCtrl', function($rootScope, $scope, $http) {
    // Duplicate the addresses list so that the user object is not modified in
    // place (which would result in an inconsistence if the user leaves the
    // page without saving his/her modifications)
    $scope.addresses = $rootScope.user.addresses.slice();
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    }
    $scope.is_last_odd = function(index) {
        return ((index == $scope.addresses.length - 1) && (index % 2 == 0));
    };
    $scope.send = function() {
        $http.post('/api/userdata', {'addresses': $scope.addresses})
            .then(function(response) {
                $rootScope.user = response.data;
            });
    };
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
});
