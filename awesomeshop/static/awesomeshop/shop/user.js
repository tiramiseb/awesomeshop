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
angular.module('shopUser', [])
.config(function($stateProvider) {
    $stateProvider
        .state('profile', {
            url: '/profile',
            templateUrl: 'shop/profile',
            controller: 'ProfileCtrl'
        })
})
.controller('ProfileCtrl', function($scope, $state, $uibModal) {
    if (!$scope.user.auth) {
        $state.go('index');
    }
    $scope.change_email = function() {
        var modalInstance = $uibModal.open({
                templateUrl: 'part/emailaddress',
                controller: 'ChangeEmailCtrl'
                })
    };
})
.controller('ChangeEmailCtrl', function($rootScope, $scope, $http) {
    $scope.change_email = function() {
        $http.post('/api/userdata', {
            email: $scope.email
        })
            .then(function(response) {
                $rootScope.user = response.data;
                $scope.$close();
            })
    }
});
