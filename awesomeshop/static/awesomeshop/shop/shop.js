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
        .state('category', {
            templateUrl: 'shop/category',
            controller: 'CategoryCtrl',
            params: {
                id: ""
            }
        })
        .state('product', {
            templateUrl: 'shop/product',
            controller: 'ProductCtrl',
            params: {
                category: "",
                slug: ""
            }
        })
        .state('category_or_product', {
            url: '/{path:any}',
            template: '',
            controller: 'CategoryOrProductCtrl',
        })
    LightboxProvider.templateUrl = 'part/lightbox';
})
.controller('CategoryOrProductCtrl', function($rootScope, $stateParams, $state, $timeout) {
    var path = $stateParams.path;
    if (!path) {
        $state.go('index');
    } else {
        function go_to_state() {
            if ($rootScope.categories) {
                var categories = $rootScope.categories,
                    found = false;
                for (var i=0; i < categories.length; i++) {
                    if (path == categories[i].path) {
                        $state.go('category', { id: categories[i].id });
                        found = true;
                        break;
                    };
                };
                if (!found) {
                    var category,
                        catpath = path.replace(/\/[^\/]*$/, ''),
                        prodslug = path.replace(/^.*\//g, '');
                    for (var i=0; i < categories.length; i++) {
                        if (catpath == categories[i].path) {
                            category = categories[i];
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
    }
})
.controller('CategoryCtrl', function($http, $scope, $stateParams) {
    $http.get('/api/category/'+$stateParams.id)
        .then(function(response) {
            $scope.category = response.data;
        });
})
.controller('ProductCtrl', function($http, $scope, $state, $stateParams, Lightbox) {
    $http.get('/api/product/catslug/'+$stateParams.category+'/'+$stateParams.slug)
        .then(function(response) {
            $scope.product = response.data;
            if ($scope.product.photos.length > 1) {
                $scope.thumb_width = parseInt(12 / ($scope.product.photos.length - 1));
            };
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
