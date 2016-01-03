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
angular.module('dbUsers', [])
.config(function($stateProvider) {
    $stateProvider
        .state('users', {
            url: '/users',
            templateUrl: 'users',
            controller: 'UsersCtrl'
        })
        .state('newuser', {
            url: '/user',
            templateUrl: 'user',
            controller: 'UserCtrl'
        })
        .state('user', {
            url: '/user/:user_id',
            templateUrl: 'user',
            controller: 'UserCtrl'
        })
})
.controller('UsersCtrl', function($scope, $http) {
    $http.get('/api/user')
        .then(function(response) {
            $scope.users = response.data;
        });
})
.controller('UserCtrl', function($scope, $http, $stateParams, $state) {
    var uid = $stateParams.user_id;
    $scope.delete_address = function(index) {
        $scope.user.addresses.splice(index, 1);
    }
    $scope.submit = function() {
        $http.post('/api/user', $scope.user)
            .then(function(response) {
                if (uid) {
                    $scope.user = response.data;
                } else {
                    $state.go('user', {user_id:response.data.id})
                }
            });
    }
    $scope.delete = function() {
        if (uid) {
            $http.delete('/api/user/'+uid)
                .then(function(response) {
                    $state.go('users');
                });
        } else {
            $state.go('users');
        }
    };
    $http.get('/api/countries')
        .then(function(response) {
            $scope.countries = response.data;
        });
    if (uid) {
        $http.get('/api/user/'+uid)
            .then(function(response) {
                $scope.user = response.data;
            });
    } else {
        $scope.user = {addresses:[]};
    }
})
