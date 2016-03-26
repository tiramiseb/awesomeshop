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
        .state('cart', {
            url:'/cart',
            templateUrl: 'shop/cart',
            controller: 'CartCtrl',
            title: 'My cart'
        })
        .state('saved_carts', {
            url: '/saved_carts',
            templateUrl: 'shop/saved_carts',
            controller: 'SavedCartsCtrl',
            title: 'Saved carts'
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
.controller('CategoryCtrl', function($http, $scope, $stateParams, title) {
    $http.get('/api/category/'+$stateParams.id)
        .then(function(response) {
            $scope.category = response.data;
            title.set($scope.category.name);
        });
})
.controller('ProductCtrl', function($http, $scope, $state, $stateParams, Lightbox, cart, title) {
    $scope.cart = cart;
    $http.get('/api/product/catslug/'+$stateParams.category+'/'+$stateParams.slug)
        .then(function(response) {
            $scope.product = response.data;
            if ($scope.product.photos.length > 1) {
                $scope.thumb_width = parseInt(12 / ($scope.product.photos.length - 1));
            };
            title.set($scope.product.name);
        }, function(response) {
            $state.go('index');
        });
    $scope.quantity = 1;
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
})
.controller('CartCtrl', function($http, $scope, cart) {
    $scope.cart = cart;
    $scope.save = function() {
        var data = {
            name: $scope.cartname,
            lines: cart.list()
        };
        $http.post('/api/cart', data)
            .then(function(response) {
                $scope.saved_cart = response.data.name;
            });
    }
})
.controller('SavedCartsCtrl', function($scope, savedCarts, cart) {
    $scope.saved_carts = savedCarts;
    $scope.load_cart = function(targetcart) {
        cart.set(targetcart);
    }
})
