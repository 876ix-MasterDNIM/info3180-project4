var app = angular.module('app', []);
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('//');
    $interpolateProvider.endSymbol('//');
});

app.controller('wishlistCtrl', function($scope, $http) {
  $scope.Wishlist = [];
  $http.get('/wishlist')
      .then(function(result) {
          console.log(result)
          $scope.Wishlist = result.data.response;
      });
});
