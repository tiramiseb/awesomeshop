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
        'shopPage', 'shopUser'
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
.filter('trusthtml', function($sce) {
    return $sce.trustAsHtml;
})
.run(function($rootScope, $uibModal, $http, $document) {
    $rootScope.$on('$stateChangeSuccess', function() {
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
    $http.get('/api/userdata')
        .then(function(response) {
            $rootScope.user = response.data;
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
