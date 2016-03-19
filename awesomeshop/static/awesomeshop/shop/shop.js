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
angular.module('shopShop', ['bootstrapLightbox'])
.config(function($stateProvider, LightboxProvider) {
    $stateProvider
        .state('index', {
            url: '/',
            templateUrl: 'shop/index',
            title: 'Home'
        })
        .state('category', {
            templateUrl: 'shop/category',
            controller: 'CategoryCtrl',
            params: {
                id: ""
            },
            title: 'Category'
        })
        .state('product', {
            templateUrl: 'shop/product',
            controller: 'ProductCtrl',
            params: {
                category: "",
                slug: ""
            },
            title: 'Product'
        })
        .state('new_products', {
            url: '/new',
            templateUrl: 'shop/category',
            controller: 'NewProductsCtrl',
            title: 'New products'
        })
        .state('category_or_product', {
            url: '/{path:any}',
            template: '',
            controller: 'CategoryOrProductCtrl',
        })
    LightboxProvider.templateUrl = 'part/lightbox';
})
.controller('CategoryOrProductCtrl', function($stateParams, $state, $timeout, categories) {
    var path = $stateParams.path;
    function go_to_state() {
        var cats = categories.get();
        if (cats) {
            var found = false;
            for (var i=0; i < cats.length; i++) {
                if (path == cats[i].path) {
                    // Without this timeout, state is loaded twice
                    $timeout(function() {
                        $state.go('category', { id: cats[i].id });
                        }, 0);
                    found = true;
                    break;
                };
            };
            if (!found) {
                var category,
                    catpath = path.replace(/\/[^\/]*$/, ''),
                    prodslug = path.replace(/^.*\//g, '');
                for (var i=0; i < cats.length; i++) {
                    if (catpath == cats[i].path) {
                        category = cats[i];
                        break;
                    };
                };
                if (category) {
                    $state.go('product', {
                        category: category.id,
                        slug: prodslug
                    })
                } else {
                    $state.go('index');
                };
            }
        } else {
            $timeout(go_to_state, 200);
        };
    };
    go_to_state();
})
.controller('CategoryCtrl', function($http, $rootScope, $scope, $stateParams) {
    $http.get('/api/category/'+$stateParams.id)
        .then(function(response) {
            $scope.category = response.data;
            $rootScope.$title = $scope.category.name;
        });
})
.controller('ProductCtrl', function($http, $rootScope, $scope, $state, $stateParams, Lightbox, cart) {
    $scope.cart = cart;
    $http.get('/api/product/catslug/'+$stateParams.category+'/'+$stateParams.slug)
        .then(function(response) {
            $scope.product = response.data;
            if ($scope.product.photos.length > 1) {
                $scope.thumb_width = parseInt(12 / ($scope.product.photos.length - 1));
            };
            $rootScope.$title = $scope.product.name;
        }, function(response) {
            $state.go('index');
        });
    $scope.quantity = 1;
    $scope.dec_quantity = function() {
        if ($scope.quantity > 1) {
            $scope.quantity -= 1;
        }
    }
    $scope.inc_quantity = function() {
        if ($scope.product.stock >= $scope.quantity || $scope.product.on_demand) { // XXX Deduce quantity in cart
            $scope.quantity += 1;
        }
    }
    $scope.openLightboxModal = function (index) {
        Lightbox.openModal($scope.product.photos, index);
    };
})
.controller('NewProductsCtrl', function($http, $scope, translateFilter) {
    $scope.category = {
        name: translateFilter('New products'),
        products: []
    }
    $http.get('/api/newproduct')
        .then(function(response) {
            $scope.category.products = response.data;
        });
})
.controller('ProductInListCtrl', function($scope, cart) {
    $scope.cart = cart;
})
.controller('CartButtonCtrl', function($scope, cart) {
    $scope.cart = cart;
});
