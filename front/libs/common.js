/* Copyright 2015-2016 Sébastien Maccagnoni
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

// Supported languages. Update here when adding languages
languages = {
    'en': 'english',
    'fr': 'français'
}
fallback_language = 'en';
langs = Object.keys(languages);
langs_negociation = {};
for (lang in langs) {
    langs_negociation[lang+'_*'] = lang;
};

// Adapted from http://stackoverflow.com/a/21189057
(function() {
  var $http = angular.injector(['ng']).get('$http');
  $http.get('/api/config').then(
    function (response) {
      angular.module('config', []).constant('CONFIG', response.data);
      angular.element(document).ready(function() {
        angular.bootstrap(document, ['awesomeshop']);
      });
    }
  );
})();

angular.module('l10n_param', ['pascalprecht.translate'])
.config(function($httpProvider) {
    $httpProvider.interceptors.push(function($injector) {
        return {
            'request': function(config) {
                if (config.url.indexOf('/api/') == 0) {
                    $translate = $injector.get('$translate');
                    if (!config.params) {
                        config.params = {};
                    }
                    config.params.lang = $translate.use();
                };
                return config;
            }
        };
    });
});

angular.module('spinner', ['ui.bootstrap'])
.config(function($httpProvider) {
    loading_count = 0;
    function show_or_hide_spinner(inc) {
        loading_count += inc;
        if (loading_count > 0) {
            document.getElementById('spinner').className="";
        } else {
            document.getElementById('spinner').className="ng-hide";
        };
    }
    show_or_hide_spinner(0);
    $httpProvider.interceptors.push(function($rootScope, $q) {
        return {
            'request': function(config) {
                show_or_hide_spinner(+1);
                return config;
            },
            'response': function(response) {
                show_or_hide_spinner(-1);
                return response;
            },
            'responseError': function(rejection) {
                show_or_hide_spinner(-1);
                if (rejection.status != 401) {
                    if (rejection.data) {
                        $rootScope.$emit('apierror', rejection.data.message)
                    } else {
                        $rootScope.$emit('apierror', {'type': 'unknown'})
                    }
                }
                return $q.reject(rejection);
            }
        };
    });
})
.directive('enableErrorHandler', function($uibModal){
    return {
        link: function(scope, elem, attrs) {
                scope.$on('apierror', function(evt, data) {
                    var template_url;
                    if (data) {
                        if (data.type == 'message') {
                            scope.message = data.message;
                            template_url = 'common/stringerror.html'
                        } else if (data.type == 'fields') {
                            scope.errors = data.errors;
                            template_url = 'common/fieldserror.html'
                        } else {
                            template_url = 'common/unknownerror.html'
                        };
                    } else {
                        template_url = 'common/unknownerror.html'
                    };
                    $uibModal.open({
                            templateUrl: template_url
                    });
                });
        }
    };
});

angular.module('authentication', ['http-auth-interceptor', 'ui.bootstrap'])
.controller('AuthenticationCtrl', function($scope, $http, authService) {
    $scope.login = function() {
        $http.post('/api/login', {
                email: $scope.auth.email,
                password: $scope.auth.password
        })
            .then(function(response) {
                var success = response.data.auth;
                $scope.auth.success = success;
                if (success) {
                    authService.loginConfirmed(response.data);
                    $scope.$close();
                }
            });
    }
})
.directive('triggerAuth', ['$uibModal', function($uibModal) {
    return {
        link: function(scope, elem, attrs) {
                scope.$on('event:auth-loginRequired', function() {
                    var modalInstance = $uibModal.open({
                        templateUrl: 'common/login.html',
                        controller: 'AuthenticationCtrl'
                    });
                });
        }
    };
}])
.run(function($rootScope, $http, $translate, tmhDynamicLocale) {
    // Change locale when user is authenticated
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        if (data.locale) {
            $translate.use(data.locale);
            tmhDynamicLocale.set(data.locale);
        }
    });
    // Load user data
    $http.get('/api/userdata')
        .then(function(response) {
            if (response.data.auth) {
                $rootScope.$broadcast('event:auth-loginConfirmed', response.data);
            } else {
                $rootScope.$broadcast('event:auth-anonymous');
            };
        });
});
