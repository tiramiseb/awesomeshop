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
        'duScroll', 'ngAnimate', 'ngStorage', 'ui.bootstrap', 'ui.router',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner',
        // Shop modules
        'shopPage', 'shopUser',
        'shopShop'
])
.config(function($locationProvider, $interpolateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $locationProvider.html5Mode(true);
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $urlRouterProvider.otherwise('/');
    $urlMatcherFactoryProvider.strictMode(false);
})
.filter('trusthtml', function($sce) {
    return $sce.trustAsHtml;
})
.factory('translation', function($http) {
    var translations;
    $http.get('/messages')
        .then(function(response) {
            translations = response.data;
        });
    return function (message) {
        if (translations) {
            return translations[message] || message;
        } else {
            return message;
        };
    };
})
.filter('translate', function(translation) {
    return function(input) {
        return translation(input);
    }
})
.factory('categories', function($http) {
    var categories;
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            categories = response.data;
        });
    return {
        get: function() {
            return categories;
        }
    };
})
.factory('docs', function($http) {
    var docs;
    $http.get('/api/page-doc')
        .then(function(response) {
            docs = response.data;
        });
    return {
        get: function() {
            return docs;
        }
    };
})
.factory('infos', function($http) {
    var infos;
    $http.get('/api/page-info')
        .then(function(response) {
            infos = response.data;
        });
    return {
        get: function() {
            return infos;
        }
    };
})
.factory('user', function($rootScope, $http, $uibModal) {
    var user = {};
    $http.get('/api/userdata')
        .then(function(response) {
            user = response.data;
        });
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        user = data;
    });
    function forcelogin() {
        $http.get('/api/forcelogin');
    };
    function get_user() {
        return user
    };
    function logout() {
        $http.get('/api/logout')
            .then(function(response) {
                user = response.data;
            });
    };
    function register() {
        $uibModal.open({
                templateUrl: 'part/register',
                controller: 'RegisterCtrl'
                })
    };
    function resend_confirmation() {
        $http.get('/api/register/resend');
    };
    function setlang(lang) {
        $http.put('/api/setlang', {'lang': lang})
            .then(function() {
                window.location.reload();
            })
    };
    function set_user(data) {
        user = data;
    };
    return {
        forcelogin: forcelogin,
        get_user: get_user,
        logout: logout,
        register: register,
        resend_confirmation: resend_confirmation,
        setlang: setlang
    }
})
.factory('cart', function($localStorage) {
    if (!$localStorage.cart) {
        $localStorage.cart = [];
    };
    // XXX Ask the server to adjust the cart (products availability and price)
    return {
        add: function(product, quantity) {
            var found = false;
            for (var i=0; i<$localStorage.cart.length; i++) {
                if ($localStorage.cart[i][0].id == product.id) {
                    $localStorage.cart[i][1] += quantity;
                    found = true;
                    break;
                }
            };
            if (!found) {
                $localStorage.cart.push([product, quantity])
            };
        },
        amount: function() {
            var amount = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var qt = $localStorage.cart[i][1],
                    unitprice = $localStorage.cart[i][0].net_price;
                amount += qt * unitprice;
            }
            return amount;
        },
        count: function() {
            var count = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                count += $localStorage.cart[i][1];
            }
            return count;
        }
    }
})
.run(function($timeout, $http, $rootScope, $uibModal, $document, $localStorage) {
    $rootScope.$on('$stateChangeSuccess', function(event, toState) {
        if (toState.title) {
            $timeout(function() {
                $rootScope.$title = toState.title;
            }, 0);
        };
        $document.scrollTop(0,300);
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
.controller('UserCtrl', function($scope, user) {
    $scope.u = user;
})
.controller('RegisterCtrl', function($scope, $http, user) {
    $scope.register = function() {
        $http.post('/api/register', {
                email: $scope.email,
                password: $scope.password
                })
            .then(function(response) {
                user.set_user(response.data);
                $scope.$close();
            })
    }
})
.controller('DocsListCtrl', function($scope, docs) {
    $scope.docs = docs;
})
.controller('CategoriesListCtrl', function($scope, categories) {
    $scope.categories = categories;
})
.controller('InfosListCtrl', function($scope, infos) {
    $scope.infos = infos;
})
