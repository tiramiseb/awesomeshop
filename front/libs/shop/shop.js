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
            templateUrl: 'shop/index.html',
            title: 'HOME'
        })
        .state('search', {
            url: '/search?q',
            templateUrl: 'shop/search.html',
            controller: 'SearchCtrl',
            title: 'SEARCH'
        })
        .state('category', {
            templateUrl: 'shop/category.html',
            controller: 'CategoryCtrl',
            params: {
                id: ""
            },
            title: 'CATEGORY'
        })
        .state('product', {
            templateUrl: 'shop/product.html',
            controller: 'ProductCtrl',
            params: {
                category: "",
                slug: ""
            },
            title: 'PRODUCT'
        })
        .state('new_products', {
            url: '/new',
            templateUrl: 'shop/newproducts.html',
            controller: 'NewProductsCtrl',
            title: 'NEW_PRODUCTS'
        })
        .state('cart', {
            url: '/cart',
            templateUrl: 'shop/cart.html',
            controller: 'CartCtrl',
            title: 'MY_CART'
        })
        .state('saved_carts', {
            url: '/saved_carts',
            templateUrl: 'shop/saved_carts.html',
            controller: 'SavedCartsCtrl',
            title: 'SAVED_CARTS'
        })
        .state('orders', {
            url: '/orders',
            templateUrl: 'shop/orders.html',
            controller: 'OrdersCtrl',
            title: 'My orders'
        })
        .state('order', {
            url: '/orders/:number',
            templateUrl: 'shop/order.html',
            controller: 'OrderCtrl'
        })
        .state('category_or_product', {
            url: '/{path:any}',
            template: '',
            controller: 'CategoryOrProductCtrl',
        })
    LightboxProvider.templateUrl = 'shop/lightbox.html';
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
.controller('CategoryCtrl', function($http, $rootScope, $scope, $stateParams, user, title) {
    $scope.user = user;
    function get_category() {
        $http.get('/api/category/'+$stateParams.id)
            .then(function(response) {
                $scope.category = response.data;
                title.set($scope.category.name);
            });
    };
    get_category();
    stoptranslate = $rootScope.$on('$translateChangeSuccess', get_category);
    $scope.$on('$destroy', stoptranslate);
})
.controller('ProductCtrl', function($http, $rootScope, $scope, $state, $stateParams, $httpParamSerializer, Lightbox, products, cart, title, user, $timeout) {
    $scope.user = user;
    $scope.cart = cart;
    $scope.quantity = 1;
    $scope.openLightboxModal = function (index) {
        Lightbox.openModal($scope.product.photos, index);
    };
    get_product = function() {
        products.getcatslug($stateParams.category, $stateParams.slug)
            .then(function(product) {
                $scope.product = product;
                // Initialize product-type-dependent functions
                //
                // the following functions must be created, dependent on each product type:
                //
                // make_data:
                //      return the data as a string or null/undef
                if (product.type == 'regular') {
                    function make_data() {
                        return null;
                    }
                } else if (product.type == 'kit') {
                    $scope.update_price = function() {
                        // Whenever a choice changes, reload the product with
                        // the corresponding data
                        products.getid($scope.product.id, make_data())
                            .then(function(prod) {
                                $scope.product = prod;
                            })
                    };
                    function make_data() {
                        var query = [];
                        for (var i=0; i<$scope.product.products.length; i++) {
                            var prod = $scope.product.products[i];
                            query.push(prod.id+':'+prod.selected);
                        };
                        return query.join(',');
                    }
                };
                // Common stuff
                $scope.add_to_cart = function() {
                    cart.add($scope.product.id, make_data(), $scope.quantity);
                };
                if ($scope.product.photos.length > 1) {
                    $scope.thumb_width = parseInt(12 / ($scope.product.photos.length - 1));
                };
                title.set($scope.product.name);
            }, function(response) {
                $state.go('index');
            });
    };
    get_product();
    stoptranslate = $rootScope.$on('$translateChangeSuccess', get_product);
    $scope.$on('$destroy', stoptranslate);
})
.controller('ProductInListCtrl', function($scope, cart) {
    $scope.cart = cart;
})
.controller('CartButtonCtrl', function($rootScope, $scope, $timeout, cart) {
    $scope.cart = cart;
    $scope.$on('cart:added', function(event, data) {
        $rootScope.added_to_cart = data;
        $timeout(function() {
            // Only hide the popup if there is no new event
            if ($rootScope.added_to_cart == data) {
                $rootScope.added_to_cart = null;
            }
        }, 5000);
    });
    $scope.$on('cart:loaded', function(event, data) {
        $rootScope.loaded_to_cart = data;
        $timeout(function() {
            // Only hide the popup if there is no new event
            if ($rootScope.loaded_to_cart == data) {
                $rootScope.loaded_to_cart = null;
            }
        }, 5000);
    });
})
.controller('CartCtrl', function($timeout, $scope, $state, $http, $uibModal, cart, savedCarts, user, orders, countries) {
    var available_carriers = {};
    $scope.cart = cart;
    $scope.user = user;
    $scope.countries = countries;
    $scope.cart_total = 0;
    $scope.choice = {
        delivery_as_billing: true,
        accept_reused_package: true
    };
    function load_preferences(foobar, userdata) {
        if (userdata) {
            if (userdata.latest_delivery_address) {
                $scope.choice.delivery_address = userdata.latest_delivery_address;
            };
            if (userdata.latest_delivery_as_billing) {
                $scope.choice.delivery_as_billing = userdata.latest_delivery_as_billing;
            };
            if (userdata.latest_billing_address) {
                $scope.choice.billing_address = userdata.latest_billing_address;
            };
            if (userdata.latest_carrier) {
                $scope.choice.carrier = userdata.latest_carrier;
            };
            if (userdata.latest_payment) {
                $scope.choice.payment = userdata.latest_payment;
            };
            if (userdata.latest_reused_package) {
                $scope.choice.accept_reused_package = userdata.latest_reused_package;
            };
        };
    }
    $scope.$on('event:auth-loginConfirmed', load_preferences);
    $timeout(function() {
        var userdata = user.get();
        if (userdata) {
            load_preferences(null, userdata);
        };
    }, 100);
    $http.post('/api/cart/verify', cart.list())
        .then(function(response) {
            var oldcart = cart.list(),
                oldsummary = {};
            for (var i=0; i<oldcart.length; i++) {
                oldsummary[oldcart[i].product.id] = oldcart[i].quantity;
            }
            for (var i=0; i<response.data.length; i++) {
                if (oldsummary[response.data[i].product.id] != response.data[i].quantity) {
                    $scope.stock_changed = true;
                }
            }
            cart.load(response.data, true);
        });
    $http.get('/api/payment')
        .then(function(response) {
            $scope.payments = response.data;
        });
    $scope.save_cart = function() {
        var data = {
            name: $scope.cartname,
            lines: cart.list()
        };
        $http.post('/api/cart', data)
            .then(function(response) {
                $scope.saved_cart = response.data.name;
                savedCarts.add(response.data);
            });
    }
    $scope.add_address = function() {
        $uibModal.open({
            templateUrl: 'shop/address.html',
            controller: 'AddressCtrl',
            resolve: {
                address_id: function() {
                    return undefined;
                }
            }
        })
    };
    $scope.modify_address = function(addr) {
        $uibModal.open({
            templateUrl: 'shop/address.html',
            controller: 'AddressCtrl',
            resolve: {
                address_id: function() {
                    return addr;
                }
            }
        })
    };
    function code_to_country(code) {
        var countrieslist = countries.get();
        if (countrieslist) {
            for (var i=0; i<countrieslist.length; i++) {
                if (countrieslist[i].code == code) {
                    return code + ' - ' + countrieslist[i].name;
                };
            };
        };
        return code;
    };
    $scope.prefixed = function(country) {
        return country.code+' - '+country.name;
    }
    $scope.full_address = function(address_id) {
        var addresses = [];
        if (user.get() && user.get().addresses) {
            addresses = user.get().addresses;
        };
        for (var i=0; i<addresses.length; i++) {
            if (addresses[i].id == address_id) {
                var address = addresses[i];
                return address.firstname + ' ' + address.lastname + '\n' + address.address + '\n' + code_to_country(address.country);
            };
        };
        return '';
    };
    find_carriers = function(country) {
        var weight = cart.weight().toString(),
            carriers = available_carriers[country];
        if (carriers && carriers[weight]) {
            return carriers[weight];
        };
        // The function has not returned yet, it means the available
        // carriers are unknown: get them, but only if the country is known
        if (country) {
            if (!available_carriers[country]) {
                available_carriers[country] = {};
            }
            available_carriers[country][weight] = [];
            $http.get('/api/carrier/'+country+'/'+weight)
                .then(function(response) {
                    available_carriers[country][weight] = response.data;
                    // and then a new digest cycle is run, this content
                    // is now present in available_carriers, it will be read
                });
        }
    }
    $scope.get_available_carriers = function() {
        var addresses = [],
            address_id = $scope.choice.delivery_address;
        if (user.get() && user.get().addresses) {
            addresses = user.get().addresses;
        };
        for (var i=0; i<addresses.length; i++) {
            if (addresses[i].id == address_id) {
                return find_carriers(addresses[i].country);
            };
        };
    };
    $scope.shipping_fee_estimation = function() {
        var carriers = find_carriers($scope.estimation_country);
        if (carriers && carriers.length) {
            return parseFloat(carriers[0].cost);
        };
    }
    $scope.get_shipping_fee = function() {
        var carriers = $scope.get_available_carriers();
        if (carriers) {
            for (var i=0; i<carriers.length; i++) {
                if (carriers[i].carrier && carriers[i].carrier.id == $scope.choice.carrier) {
                    return parseFloat(carriers[i].cost);
                }
            };
        }
    };
    $scope.open_terms = function() {
        $uibModal.open({
            templateUrl: 'shop/page_in_modal.html',
            controller: 'CartTermsCtrl'
        })
    };
    $scope.confirm = function() {
        var data = angular.copy($scope.choice);
        data.cart = cart.list();
        $http.post('/api/order', data)
            .then(function(response) {
                order = response.data;
                cart.empty();
                orders.add({
                    full_number: order.full_number,
                    number: order.number,
                    status: order.status,
                    status_color: order.status_color,
                    date: order.date,
                    products: order.products.length,
                    net_total: order.net_total,
                    currency: order.currency
                });
                $state.go('order', {number: order.number});
            });
    };
})
.controller('CartTermsCtrl', function($http, $scope) {
    $http.get('/api/page-info/terms_of_purchase')
        .then(function(response) {
            $scope.page = response.data;
        });
})
.controller('SavedCartsCtrl', function($scope, savedCarts, cart) {
    $scope.saved_carts = savedCarts;
    $scope.load_cart = function(targetcart) {
        cart.load(targetcart);
    }
})
.controller('OrdersCtrl', function($scope, orders) {
    $scope.orders = orders;
})
.controller('OrderCtrl', function($uibModal, $stateParams, $scope, $http, $filter, cart, title) {
    $http.get('/api/order/'+$stateParams.number)
        .then(function(response) {
            $scope.order = response.data;
            title.set(
                'Order [[ order.full_number ]], on [[ order.date | date ]]'
                .replace('[[ order.full_number ]]', $scope.order.full_number)
                .replace('[[ order.date | date ]]', $filter('date')($scope.order.date))
            );
        });
    $scope.pay = function() {
        $http.get('/api/order/'+$stateParams.number+'/pay')
            .then(function(response) {
                var data = response.data;
                if (data) {
                    $scope.order = data.order;
                    if (data.type == 'modal') {
                        $uibModal.open({
                            templateUrl: 'shop/'+data.template+'.html',
                            controller: 'PaymentModalCtrl',
                            resolve: {
                                data: function() {
                                    return data.data;
                                }
                            }
                        })
                    } else if (data.type == 'redirect') {
                        window.location.replace(data.target);
                    };
                };
            });
    };
    function cancel(to_cart) {
        var back_to_cart = to_cart || false;
        $http.get('/api/order/'+$stateParams.number+'/cancel')
            .then(function(response) {
                $scope.order = response.data;
                if (back_to_cart) {
                    for (var p=0; p<$scope.order.products.length; p++) {
                        var prod = $scope.order.products[p];
                        cart.add(prod.product.id, prod.data, prod.quantity);
                    };
                };
            });
    }
    $scope.cancel = function() {
        cancel(false);
    }
    $scope.to_cart = function() {
        cancel(true);
    }
})
.controller('PaymentModalCtrl', function($scope, data) {
    $scope.data = data;
})
.controller('SearchCtrl', function($stateParams, $scope, $http) {
    $scope.terms = $stateParams.q || '';
    $scope.waiting = true;
    $http.get('/api/search', {params: {'terms': $scope.terms}})
        .then(function(response) {
            $scope.waiting = false;
            $scope.result = response.data;
        })
})
