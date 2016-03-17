/* Copyright 2015-2016 Sébastien Maccagnoni-Munch
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
        'duScroll', 'ngAnimate', 'ui.bootstrap', 'ui.router',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner',
        // Shop modules
        'shopPage', 'shopUser',
        'shopShop' // shopShop must be the last one
])
.config(function($locationProvider, $interpolateProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $locationProvider.html5Mode(true);
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $urlRouterProvider.otherwise('/');
    $urlMatcherFactoryProvider.strictMode(false);
    $stateProvider
        .state('index', {
            url: '/',
            templateUrl: 'shop/index',
            controller: 'IndexCtrl',
            title: 'Home'
        })
})
.filter('trusthtml', function($sce) {
    return $sce.trustAsHtml;
})
.filter('translate', function($rootScope) {
    return function(input) {
        if ($rootScope.translations) {
            return $rootScope.translations[input] || input;
        } else {
            return input;
        }
    }
})
.run(function($timeout, $http, $rootScope, $uibModal, $document) {
    $rootScope.$on('$stateChangeSuccess', function(event, toState) {
        if (toState.title) {
            $timeout(function() {
                $rootScope.$title = toState.title;
            }, 0);
        };
        $document.scrollTop(0,300);
    });
    // Stuff related to the user
    $rootScope.$on('event:auth-loginConfirmed', function(event, data){
        $rootScope.user = data;
    });
    $rootScope.user = {};
    $rootScope.forcelogin = function() {
        $http.get('/api/forcelogin');
    };
    $rootScope.logout = function() {
        $http.get('/api/logout')
            .then(function(response) {
                $rootScope.user = response.data;
            });
    };
    $rootScope.register = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'part/register',
                controller: 'RegisterCtrl'
                })
    };
    $rootScope.resend_confirmation = function() {
        $http.get('/api/register/resend');
    };
    $rootScope.setlang = function(lang) {
        $http.put('/api/setlang', {'lang': lang})
            .then(function() {
                window.location.reload();
            })
    };
    $http.get('/messages')
        .then(function(response) {
            $rootScope.translations = response.data;
        });
    $http.get('/api/userdata')
        .then(function(response) {
            $rootScope.user = response.data;
        });
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            $rootScope.categories = response.data;
        });
    $http.get('/api/page-doc')
        .then(function(response) {
            $rootScope.docs = response.data;
        });
    $http.get('/api/page-info')
        .then(function(response) {
            $rootScope.infos = response.data;
        });
})
.directive('productsList', function() {
    return {
        restrict: 'E',
        scope: {
            products: '=products'
        },
        templateUrl: 'part/productslist'
    };
})
.controller('RegisterCtrl', function($rootScope, $scope, $http) {
    $scope.register = function() {
        $http.post('/api/register', {
            email: $scope.email,
            password: $scope.password
        })
            .then(function(response) {
                $rootScope.user = response.data;
                $scope.$close();
            })
    }
})
.controller('IndexCtrl', function() {
})
