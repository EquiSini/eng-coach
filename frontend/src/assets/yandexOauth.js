console.log("login component works")
   window.onload = function() {
      window.YaAuthSuggest.init({
                  client_id: "4e22d6f5bf1b4489964a45cf61956e39",
                  response_type: 'token',
                  redirect_uri: "http://localhost/yandexOauth2callback"
               },
               "http://localhost", {
                  view: 'button',
                  parentId: 'container',
                  buttonView: 'main',
                  buttonTheme: 'light',
                  buttonSize: 'm',
                  buttonBorderRadius: 0
               }
            )
            .then(function(result) {
               return result.handler()
            })
            .then(function(data) {
               console.log('Сообщение с токеном: ', data);
               document.body.innerHTML += `Сообщение с токеном: ${JSON.stringify(data)}`;
            })
            .catch(function(error) {
               console.log('Что-то пошло не так: ', error);
               document.body.innerHTML += `Что-то пошло не так: ${JSON.stringify(error)}`;
            });
      };