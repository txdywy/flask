// define angular module/app
var formApp = angular.module('formApp', ['angular-loading-bar']);
var myApp = formApp
myApp.directive('fileModel', ['$parse', function ($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            
            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}]);

myApp.service('fileUpload', ['$http', 'Scopes', function ($http, Scopes) {
    this.uploadFileToUrl = function(file, uploadUrl){
        var fd = new FormData();
        fd.append('file', file);
        setTimeout(function() { alert('Do not submit until the image appears.'); }, 0.001);
        console.log('start http')
        $http.post(uploadUrl, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        })
        .success(function(data){
            console.log(data);
            Scopes.get('formController').formData.image = data
        })
        .error(function(){
        });
    }
}]);

myApp.controller('myCtrl', ['$scope', 'fileUpload', 'Scopes', function($scope, fileUpload, Scopes){
    Scopes.store('myCtrl', $scope)
    $scope.uploadFile = function(){
        var file = $scope.myFile;
        console.log('file is ' + JSON.stringify(file));
        var uploadUrl = "/upload_image";
        fileUpload.uploadFileToUrl(file, uploadUrl, Scopes);
    };
    
}]);  


// create angular controller and pass in $scope and $http
formApp.controller('formController', function($scope, $http, Scopes) {
  Scopes.store('formController', $scope);

  // create a blank object to hold our form information
  // $scope will allow this to pass between controller and view
  $scope.formData = {};

  // process the form
  $scope.processForm = function() {
    $http({
          method  : 'POST',
          url     : 'owner_upload',
          data    : $.param($scope.formData),  // pass in data as strings
          headers : { 'Content-Type': 'application/x-www-form-urlencoded' }  // set the headers so angular passing info as form data (not request payload)
      })  
          .success(function(data) {
              console.log(data);
               
              if (data==='success') {
                  window.location.reload();
                  window.alert('sucess')
                // if not successful, bind errors to error variables
                  /*
                  $scope.errorTitle = data.errors.title;
                  $scope.errorDesp = data.errors.desp;
                  $scope.errorIncentive = data.errors.incentive;
                  $scope.errorImage = data.errors.image;
                  $scope.errorClient = data.errors.client;
                  */
              } else {
                  window.alert('failed, need more parameters')
                // if successful, bind success message to message
                  /*
                  $scope.message = data.message;
                  $scope.errorTitle = '';
                  $scope.errorDesp = '';
                  $scope.errorIncentive = '';
                  $scope.errorImage = '';
                  $scope.errorClient = '';
                  */
              }
              
          });

  };

});

myApp.factory('Scopes', function ($rootScope) {
    var mem = {};
 
    return {
        store: function (key, value) {
            $rootScope.$emit('scope.stored', key);
            mem[key] = value;
        },
        get: function (key) {
            return mem[key];
        }
    };
});
