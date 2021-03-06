/* Copyright 2015 Sébastien Maccagnoni
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
            templateUrl: 'dashboard/users.html',
            controller: 'UsersCtrl'
        })
        .state('newuser', {
            url: '/user',
            templateUrl: 'dashboard/user.html',
            controller: 'UserCtrl'
        })
        .state('user', {
            url: '/user/:user_id',
            templateUrl: 'dashboard/user.html',
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
    $scope.submit = function() {
        if ($scope.user.id) {
            $http.put('/api/user/'+$scope.user.id, $scope.user)
                .then(function(response) {
                    $scope.user = response.data;
                    $scope.form.$setPristine();
                });
        } else {
            $http.post('/api/user', $scope.user)
                .then(function(response) {
                    $scope.user = response.data;
                    $scope.form.$setPristine();
                    $state.go('user', {user_id:response.data.id}, {notify:false});
                });
        };
    }
    $scope.delete = function() {
        if ($scope.user.id) {
            $http.delete('/api/user/'+$scope.user.id)
                .then(function(response) {
                    $state.go('users');
                });
        } else {
            $state.go('users');
        }
    };
    $http.get('/api/country')
        .then(function(response) {
            $scope.countries = response.data;
        });
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    }
    if ($stateParams.user_id) {
        $http.get('/api/user/'+$stateParams.user_id)
            .then(function(response) {
                $scope.user = response.data;
            });
    } else {
        $scope.user = {addresses:[]};
    }
})
