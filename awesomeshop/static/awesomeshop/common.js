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

// Adapted from here: http://stackoverflow.com/a/21189057
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

angular.module('spinner', [])
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
    $httpProvider.interceptors.push(function($q) {
        return {
            'response': function(response) {
                show_or_hide_spinner(-1);
                return response;
            },
            'responseError': function(rejection) {
                show_or_hide_spinner(-1);
                return $q.reject(rejection);
            }
        };
    });
    $httpProvider.defaults.transformRequest.push(function(data){
        show_or_hide_spinner(+1);
        return data;
    });
})
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
                    $scope.$close();
                    authService.loginConfirmed();
                }
            });
    }
})
.directive('triggerAuth', ['$uibModal', function($uibModal) {
    return {
        link: function(scope, elem, attrs) {
                scope.$on('event:auth-loginRequired', function() {
                    var modalInstance = $uibModal.open({
                        animation: true,
                        backdrop: 'static',
                        templateUrl: '/part/login',
                        controller: 'AuthenticationCtrl'
                    });
                });
        }
    };
}]);