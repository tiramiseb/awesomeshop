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
            url: '/cart',
            templateUrl: 'shop/cart',
            controller: 'CartCtrl',
            title: 'My cart'
        })
        .state('checkout', {
            url: '/checkout',
            templateUrl: 'shop/checkout',
            controller: 'CheckoutCtrl',
            title: 'Checkout'
        })
        .state('saved_carts', {
            url: '/saved_carts',
            templateUrl: 'shop/saved_carts',
            controller: 'SavedCartsCtrl',
            title: 'Saved carts'
        })
        .state('orders', {
            url: '/orders',
            templateUrl: 'shop/orders',
            controller: 'OrdersCtrl',
            title: 'My orders'
        })
        .state('order', {
            url: '/orders/:number',
            templateUrl: 'shop/order',
            controller: 'OrderCtrl'
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
.controller('CartCtrl', function($http, $scope, cart, savedCarts) {
    $scope.cart = cart;
    $scope.save = function() {
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
})
.controller('CheckoutCtrl', function($timeout, $scope, $state, $http, $uibModal, cart, user, orders) {
    var countries = {},
        totalweight = 0,
        cartlines = cart.list(),
        available_carriers = {};
    user.forcelogin();
    $scope.cart = cart;
    $scope.user = user;
    $scope.cart_total = 0;
    $scope.choice = {
        delivery_as_billing: true,
        accept_reused_package: true
    };
    $timeout(function() {
        // Reused latest data from the user
        var userdata = user.get();
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
    }, 100);
    for (var i=0; i<cartlines.length; i++) {
        totalweight += cartlines[i].product.weight * cartlines[i].quantity;
        $scope.cart_total += cartlines[i].product.net_price * cartlines[i].quantity;
    };
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
            cart.set(response.data, true);
        });
    $http.get('/api/payment')
        .then(function(response) {
            $scope.payments = response.data;
        });
    $scope.add_address = function() {
        $uibModal.open({
            templateUrl: 'part/address',
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
            templateUrl: 'part/address',
            controller: 'AddressCtrl',
            resolve: {
                address_id: function() {
                    return addr;
                }
            }
        })
    };
    $http.get('/api/country')
        .then(function(response) {
            countries = response.data;
        });
    function code_to_country(code) {
        for (i=0; i<countries.length; i++) {
            if (countries[i].code == code) {
                return code + ' - ' + countries[i].name;
            };
        };
        return code;
    };
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
    $scope.$watch('choice.delivery_address', function(address_id) {
        var addresses = [];
        if (address_id) {
            if (user.get() && user.get().addresses) {
                addresses = user.get().addresses;
            };
            for (var i=0; i<addresses.length; i++) {
                if (addresses[i].id == address_id) {
                    var country = addresses[i].country;
                    if (!available_carriers[country]) {
                        $http.get('/api/carrier/'+country+'/'+totalweight.toString())
                            .then(function(response) {
                                available_carriers[country] = response.data;
                            });
                    };
                    return;
                };
            };
        };
    });
    $scope.get_available_carriers = function() {
        var addresses = [],
            address_id = $scope.choice.delivery_address;
        if (user.get() && user.get().addresses) {
            addresses = user.get().addresses;
        };
        for (var i=0; i<addresses.length; i++) {
            if (addresses[i].id == address_id) {
                return available_carriers[addresses[i].country];
            };
        };
    };
    $scope.get_shipping_fee = function() {
        var carriers = $scope.get_available_carriers();
        if (carriers) {
            for (var i=0; i<carriers.length; i++) {
                if (carriers[i].carrier.id == $scope.choice.carrier) {
                    return parseFloat(carriers[i].cost);
                }
            };
        }
    };
    $scope.open_terms = function() {
        $uibModal.open({
            templateUrl: 'part/page_in_modal',
            controller: 'CheckoutTermsCtrl'
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
                    human_status: order.human_status,
                    status_color: order.status_color,
                    date: order.date,
                    products: order.products.length,
                    net_total: order.net_total
                });
                $state.go('order', {number: order.number});
            });
    };
})
.controller('CheckoutTermsCtrl', function($http, $scope) {
    $http.get('/api/page-info/terms_of_purchase')
        .then(function(response) {
            $scope.page = response.data;
        });
})
.controller('SavedCartsCtrl', function($scope, savedCarts, cart) {
    $scope.saved_carts = savedCarts;
    $scope.load_cart = function(targetcart) {
        cart.set(targetcart);
    }
})
.controller('OrdersCtrl', function($scope, orders) {
    $scope.orders = orders;
})
.controller('OrderCtrl', function($uibModal, $stateParams, $scope, $http, $filter, title) {
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
                    if (data.type == 'message') {
                        $uibModal.open({
                            templateUrl: 'part/paymentmessage',
                            controller: 'PaymentMessageCtrl',
                            resolve: {
                                message: function() {
                                    return data.message;
                                }
                            }
                        })
                    };
                };
            })
    };
})
.controller('PaymentMessageCtrl', function($scope, message) {
    $scope.message = message;
});
