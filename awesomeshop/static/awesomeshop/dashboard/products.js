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
            url: '/product-{product_type}/new',
            templateUrl: function($stateParams) {
                return 'product-'+$stateParams.product_type;
            },
            controller: 'ProductCtrl'
        })
        .state('product', {
            url: '/product-{product_type}/:product_id',
            templateUrl: function($stateParams) {
                return 'product-'+$stateParams.product_type;
            },
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
    // Common stuff
    $scope.langs = CONFIG.languages;
    $scope.photos_sortoptions = {containment:'#photos'};
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
    $scope.product_name_from_id = function(prodid) {
        if ($scope.products) {
            for (i=0; i<$scope.products.length; i++) {
                if ($scope.products[i].id == prodid) {
                    return $scope.products[i].name || $scope.products[i].slug;
                }
            }
        }
        return prodid;
    }
    $scope.unrelated_products = function() {
        var filtered = [];
        if ($scope.products && $scope.product) {
            for (i=0; i<$scope.products.length; i++) {
                if ($scope.products[i].id != $scope.product.id && $scope.product.related_products.indexOf($scope.products[i].id) == -1) {
                    filtered.push($scope.products[i])
                }
            }
        }
        return filtered;
    }
    $scope.add_related_product = function(prodid) {
        $scope.product.related_products.push(prodid);
        $scope.product.related_products.sort();
        $scope.form.$setDirty();
    }
    $scope.remove_related_product = function(prodid) {
        $scope.product.related_products.splice($scope.product.related_products.indexOf(prodid), 1);
        $scope.form.$setDirty();
    }
    $scope.submit = function() {
        if ($scope.product.id) {
            $http.put('/api/product-'+$scope.product.type+'/'+$scope.product.id+'/edit', $scope.product)
                .then(function(response) {
                    $scope.product = response.data;
                    $scope.form.$setPristine();
                });
        } else {
            $http.post('/api/product-'+$scope.product.type, $scope.product)
                .then(function(response) {
                    $scope.product = response.data;
                    $scope.form.$setPristine();
                    reinit($scope.product.id);
                    $state.go('product', {product_type:response.data.type, product_id:response.data.id}, {notify:false});
                });
        };
    }
    $scope.delete = function() {
        if ($scope.product.id) {
            $http.delete('/api/product-'+$scope.product.type+'/'+$scope.product.id+'/edit')
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
        $http.get('/api/product-'+$stateParams.product_type+'/'+$stateParams.product_id+'/edit')
            .then(function(response) {
                $scope.product = response.data;
                // angular-sortable-view doesn't seem to work with embedded lists
                $scope.photos = $scope.product.photos;
                $scope.displayable_from_id($scope, 'categories', $scope.product.category)
                $scope.displayable_from_id($scope, 'documentations', $scope.product.documentation)
                reinit($scope.product.id);
            });
    } else {
        $scope.product = {
            related_products: []
        };
    };
    switch ($stateParams.product_type) {
        case 'regular':
            // Specific to regular products
            if (!$stateParams.product_id) {
                $scope.product.type = 'regular';
            };
            $scope.net_price = function() {
                if ($scope.taxrates && $scope.product) {
                    for (i=0; i<$scope.taxrates.length; i++) {
                        if ($scope.product.tax == $scope.taxrates[i].id) {
                            return parseFloat($scope.product.gross_price) * ( 1 + parseFloat($scope.taxrates[i].rate) );
                        };
                    };
                };
                return '?';
            };
            break;
        case 'kit':
            // Specific to kit produts
            if (!$stateParams.product_id) {
                $scope.product.type = 'kit';
                $scope.product.products = [];
            };
            function price(tax) {
                var from = 0.0,
                    to = 0.0,
                    variation = parseFloat($scope.product.price_variation) || 0;
                $scope.product.products.forEach(function(prod) {
                    var min = 999999999999,
                        max = 0;
                    prod.options.forEach(function(option) {
                        var gross = parseFloat(option.quantity * option.product.gross_price);
                        min = Math.min(gross, min);
                        max = Math.max(gross, max);
                    });
                    from = from + min;
                    to = to + max;
                })
                if ($scope.product.euros_instead_of_percent) {
                    from = (from + variation) * (1 + tax);
                    to = (to + variation) * (1 + tax);
                } else {
                    from = from * (1 + variation/100 + tax);
                    to = to * (1 + variation/100 + tax);
                }
                return from.toFixed(2) + ' - ' + to.toFixed(2);
            }
            $scope.gross_price = function() {
                if ($scope.product) {
                    return price(0);
                };
                return '';
            };
            $scope.net_price = function() {
                if ($scope.taxrates && $scope.product) {
                    for (i=0; i<$scope.taxrates.length; i++) {
                        if ($scope.product.tax == $scope.taxrates[i].id) {
                            return price(parseFloat($scope.taxrates[i].rate));
                        }
                    }
                };
                return '';
            };
            break;
    };
});
