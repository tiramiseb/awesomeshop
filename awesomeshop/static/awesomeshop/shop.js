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
angular.module('awesomeshop', [
        // External modules
        //'ngAnimate', 'ui.bootstrap', 'ui.router', 'validation.match',
        'ui.bootstrap', 'ui.router',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner'
])
.config(function($interpolateProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $urlRouterProvider.otherwise('');
    $urlMatcherFactoryProvider.strictMode(false);
    $stateProvider
        .state('index', {
            url: '',
            templateUrl: 'shop/index',
            controller: 'IndexCtrl'
        })
})
.factory('UserData', function($http, $rootScope) {
    var userdata = {};
    $http.get('/api/userdata')
        .then(function(response) {
            userdata.user = response.data;
        });
    $rootScope.$on('event:auth-loginConfirmed', function(event, data){
        userdata.user = data;
    });
    return userdata;
})
.controller('UserControls', function($http, $scope, $window, UserData) {
    $scope.user = function() {
        return UserData.user;
    }
    $scope.forcelogin = function() {
        $http.get('/api/forcelogin');
    };
    $scope.logout = function() {
        $http.get('/api/logout')
            .then(function(response) {
                UserData.user = response.data;
            });
    };
    $scope.setlang = function(lang) {
        $http.put('/api/setlang', {'lang': lang})
            .then(function() {
                $window.location.reload();
            })
    };
})
.controller('CategoriesList', function($scope, $http) {
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            $scope.categories = response.data;
        });
})
.controller('DocumentationList', function($scope, $http) {
    $http.get('/api/page-doc')
        .then(function(response) {
            $scope.pages = response.data;
        });
})
.controller('InfoList', function($scope, $http) {
    $http.get('/api/page-info')
        .then(function(response) {
            $scope.pages = response.data;
        });
})
.controller('IndexCtrl', function($scope) {
})
