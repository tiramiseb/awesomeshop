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
.filter('htmlbr', function($sce) {
    return function(input) {
        if (input) {
            return $sce.trustAsHtml(input.replace(/\n/g, '<br>'));
        };
    };
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
.factory('countries', function($http) {
    var countries;
    $http.get('/api/country')
        .then(function(response) {
            countries = response.data;
        });
    return {
        get: function() {
            return countries;
        }
    };
})
.factory('newproducts', function($http) {
    var newproducts;
    $http.get('/api/newproducts')
        .then(function(response) {
            newproducts = response.data;
        });
    return {
        get: function() {
            return newproducts;
        },
        count: function() {
            if (newproducts) {
                return newproducts.length;
            } else {
                return 0;
            };
        }
    };
})
.factory('categories', function($rootScope, $http) {
    var categories,
        current_product_category;
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            categories = response.data;
        });
    $rootScope.$on('$stateChangeStart', function() {
        current_product_category = undefined;
    });
    $rootScope.$on('$stateChangeSuccess', function(event, toState, toParams) {
        if (toState.name == 'product') {
            current_product_category = toParams.category;
        };
    });
    return {
        get: function() {
            return categories;
        },
        from_current_product() {
            return current_product_category;
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
.factory('user', function($rootScope, $state, $http, $uibModal) {
    var user = undefined;
    $http.get('/api/userdata')
        .then(function(response) {
            user = response.data;
            if (response.data.auth) {
                $rootScope.$broadcast('event:auth-loginConfirmed', response.data);
            };
        });
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        user = data;
    });
    return {
        forcelogin: function() {
            $http.get('/api/forcelogin');
        },
        get: function() {
            return user;
        },
        set: function(data) {
            user = data;
        },
        logout: function() {
            $http.get('/api/logout')
                .then(function(response) {
                    user = response.data;
                    $state.go('index');
                });
        },
        resend_confirmation: function() {
            $http.get('/api/register/resend');
        },
        setlang: function(lang) {
            $http.put('/api/setlang', {'lang': lang})
                .then(function() {
                    window.location.reload();
                })
        }
    }
})
.factory('savedCarts', function($rootScope, $timeout, $http, cart, user) {
    var carts;
    function get_saved_carts() {
        $http.get('/api/cart')
            .then(function(response) {
                carts = response.data;
            });
    };
    if (user.get()) {
        get_saved_carts();
    };
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        // Timeout, just to be sure it is executed after the user data is loaded
        $timeout(function() {
            get_saved_carts();
        }, 10);
    });
    return {
        get: function() {
            return carts;
        },
        add: function(cart) {
            carts.push(cart);
        },
        count: function() {
            if (carts) {
                return carts.length;
            } else {
                return '';
            };
        },
        remove: function(index) {
            $http.delete('/api/cart/'+carts[index].id)
                .then(function() {
                    carts.splice(index, 1);
                })
        }
    };
})
.factory('cart', function($localStorage, $http, $state) {
    if ($localStorage.cart) {
        // Ask the server to adjust the cart (availability and price)
        $http.post('/api/cart/verify', $localStorage.cart)
            .then(function(response) {
                $localStorage.cart = response.data;
            });
    } else {
        $localStorage.cart = [];
    };
    return {
        add: function(product, quantity) {
            var found = false;
            for (var i=0; i<$localStorage.cart.length; i++) {
                if ($localStorage.cart[i].product.id == product.id) {
                    $localStorage.cart[i].quantity += quantity;
                    found = true;
                    break;
                }
            };
            if (!found) {
                $localStorage.cart.push({
                    'product': product,
                    'quantity': quantity
                })
            };
        },
        remove: function(product) {
            var index = -1;
            for (var i=0; i<$localStorage.cart.length; i++) {
                if ($localStorage.cart[i].product.id == product.id) {
                    index=i;
                    break;
                };
            };
            if (index >= 0) {
                $localStorage.cart.splice(index, 1);
            };
        },
        set: function(targetcart, do_not_verify) {
            if (do_not_verify) {
                $localStorage.cart = targetcart;
            } else {
                $http.post('/api/cart/verify', targetcart)
                    .then(function(response) {
                        $localStorage.cart = response.data;
                    });
            };
        },
        stock: function(product) {
            if (product) {
                // Check the available stock, deducing quantity in cart
                var stock = product.stock;
                for (var i=0; i<$localStorage.cart.length; i++) {
                    if ($localStorage.cart[i].product.id == product.id) {
                        stock = Math.max(0, stock - $localStorage.cart[i].quantity);
                        break;
                    };
                };
                return stock;
            } else {
                return 0;
            }
        },
        amount: function() {
            var amount = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var qt = $localStorage.cart[i].quantity,
                    unitprice = $localStorage.cart[i].product.net_price;
                amount += qt * unitprice;
            }
            return amount;
        },
        count: function() {
            var count = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                if (!$localStorage.cart[i].quantity) {
                    $localStorage.cart[i].quantity = 1;
                } else if ($localStorage.cart[i].quantity > $localStorage.cart[i].product.stock && $localStorage.cart[i].product.overstock_delay == -1) {
                    // Reduce quantity to stock if overstock is not allowed
                    $localStorage.cart[i].quantity = $localStorage.cart[i].product.stock;
                };
                count += $localStorage.cart[i].quantity;
            }
            return count;
        },
        reset: function() {
            $localStorage.cart = [];
            $state.go('index');
        },
        empty: function() {
            $localStorage.cart = [];
        },
        list: function() {
            return $localStorage.cart;
        },
        total: function() {
            var total = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                total += $localStorage.cart[i].product.net_price * $localStorage.cart[i].quantity;
            };
            return total;
        },
        in_stock: function() {
            var in_stock = true;
            for (var i=0; i<$localStorage.cart.length; i++) {
                if ($localStorage.cart[i].product.stock < $localStorage.cart[i].quantity) {
                    // If the stock is not sufficient for a single "not
                    // overstock" product, the whole cart is marked as "not in
                    // stock"
                    in_stock = false;
                    break;
                };
            };
            return in_stock;
        },
        delay: function() {
            var delay = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var product = $localStorage.cart[i].product;
                if (product.stock < $localStorage.cart[i].quantity) {
                    if (product.delay == -1) {
                        delay = -1;
                    } else {
                        delay = Math.max(product.overstock_delay, delay);
                    }
                } else {
                    delay = Math.max(product.delay, delay);
                };
            };
            return delay;
        }
    }
})
.factory('orders', function($rootScope, $http, $timeout, user) {
    var orders;
    function get_orders() {
        $http.get('/api/order')
            .then(function(response) {
                orders = response.data;
            });
    };
    if (user.get()) {
        get_orders();
    };
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        // Timeout, just to be sure it is executed after the user data is loaded
        $timeout(function() {
            get_orders();
        }, 10);
    });
    return {
        count: function() {
            if (orders) {
                return orders.length;
            } else {
                return '';
            };
        },
        get: function() {
            return orders;
        },
        add: function(order) {
            orders.push(order);
        }
    }

})
.factory('title', function() {
    var title = '';
    return {
        set: function(newtitle) {
            title = newtitle;
        },
        get: function() {
            return title;
        }
    }
})
.run(function($timeout, $rootScope, $document, title) {
    $rootScope.$on('$stateChangeSuccess', function(event, toState) {
        if (toState.title) {
            // Without this timeout, the history is scrambled
            $timeout(function() {
                title.set(toState.title);
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
.controller('TitleCtrl', function($scope, title) {
    $scope.title = title;
})
.controller('UserCtrl', function($scope, user, savedCarts, orders) {
    $scope.user = user;
    $scope.saved_carts = savedCarts;
    $scope.orders = orders;
})
.controller('NewProductsCtrl', function($scope, newproducts) {
    $scope.newproducts = newproducts;
})
.controller('CategoriesListCtrl', function($scope, categories) {
    $scope.categories = categories;
})
.controller('DocsListCtrl', function($scope, docs) {
    $scope.docs = docs;
})
.controller('InfosListCtrl', function($scope, infos) {
    $scope.infos = infos;
})
.controller('SearchFormCtrl', function($scope, $state) {
    $scope.search = function() {
        $state.go('search', {'q': $scope.terms});
    }
})
