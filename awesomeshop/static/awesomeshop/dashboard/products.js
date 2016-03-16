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

angular.module('dbProducts', ['angularFileUpload', 'slugifier'])
.config(function($stateProvider) {
    $stateProvider
        .state('products', {
            url: '/product',
            templateUrl: 'products',
            controller: 'ProductsCtrl'
        })
        .state('newproduct', {
            url: '/product/new',
            templateUrl: 'product',
            controller: 'ProductCtrl'
        })
        .state('product', {
            url: '/product/:product_id',
            templateUrl: 'product',
            controller: 'ProductCtrl'
        })
})
.controller('ProductsCtrl', function($scope, $http) {
    $http.get('/api/product')
        .then(function(response) {
            $scope.products = response.data;
        });
})
.controller('ProductCtrl', function($scope, $http, $stateParams, $state, FileUploader, Slug, CONFIG) {
    $scope.langs = CONFIG.languages;
    $scope.sortoptions = {containment:'#photos'};
    $scope.sort_photo = function(from_rank, to_rank) {
        $http.get('/api/product/'+$scope.product.id+'/photo/'+from_rank+'/move/'+to_rank);
    };
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            $scope.categories = response.data;
        });
    $http.get('/api/product')
        .then(function(response) {
            $scope.products = response.data;
        });
    $http.get('/api/page-doc')
        .then(function(response) {
            $scope.documentations = response.data;
        });
    $http.get('/api/taxrate')
        .then(function(response) {
            $scope.taxrates = response.data;
        })
    function reinit(pid) {
        $scope.uploader = new FileUploader({
            url: '/api/product/'+pid+'/photo',
            autoUpload: true,
            removeAfterUpload: true
        });
        $scope.uploader.onSuccessItem = function(item, response, status, header) {
            $scope.photos.push(response);
        };
    }
    $scope.name_from_id = function(prodid) {
        if ($scope.products) {
            for (i=0; i<$scope.products.length; i++) {
                if ($scope.products[i].id == prodid) {
                    return $scope.products[i].name;
                }
            }
        }
        return prodid;
    }
    $scope.filtered_products = function() {
        filtered = [];
        if ($scope.products && $scope.product) {
            for (i=0; i<$scope.products.length; i++) {
                if ($scope.products[i].id != $scope.product.id && $scope.product.related_products.indexOf($scope.products[i].id) == -1) {
                    filtered.push($scope.products[i])
                }
            }
        }
        return filtered;
    }
    $scope.add_prod = function(prodid) {
        $scope.product.related_products.push(prodid);
        $scope.product.related_products.sort();
        $scope.form.$setDirty();
    }
    $scope.remove_prod = function(prodid) {
        $scope.product.related_products.splice($scope.product.related_products.indexOf(prodid), 1);
        $scope.form.$setDirty();
    }
    $scope.net_price = function() {
        if ($scope.taxrates && $scope.product) {
            for (i=0; i<$scope.taxrates.length; i++) {
                if ($scope.product.tax == $scope.taxrates[i].id) {
                    return parseFloat($scope.product.gross_price) * ( 1 + parseFloat($scope.taxrates[i].rate) );
                }
            }
        }
        return '?';
    }
    $scope.submit = function() {
        $http.post('/api/product', $scope.product)
            .then(function(response) {
                var is_new = !$scope.product.id;
                $scope.product = response.data;
                $scope.form.$setPristine();
                if (is_new) {
                    $state.go('product', {product_id:response.data.id}, {notify:false});
                }
            });
    }
    $scope.delete = function() {
        if ($scope.product.id) {
            $http.delete('/api/product/'+$scope.product.id)
                .then(function(response) {
                    $state.go('products');
                });
        } else {
            $state.go('products');
        }
    };
    $scope.slug_from = function(text) {
        $scope.product.slug = Slug.slugify(text);
    };
    $scope.delete_photo = function(filename, index) {
        $http.delete('/api/product/'+$scope.product.id+'/photo/'+filename)
            .then(function() {
                $scope.photos.splice(index, 1);
            })
    }
    if ($stateParams.product_id) {
        $http.get('/api/product/'+$stateParams.product_id+'/edit')
            .then(function(response) {
                $scope.product = response.data;
                // angular-sortable-view doesn't seem to work with embedded lists
                $scope.photos = $scope.product.photos;
                reinit($scope.product.id);
            });
    } else {
        $scope.product = {};
    }
});
